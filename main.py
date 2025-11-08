import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List

import aiosqlite
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import BotCommand, InputFile, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.db import (
    add_expense,
    get_user_categories,
    get_user_expenses_report,
    init_db,
    is_user_registered,
    register_user,
    remove_expense_by_message_id,
)
from src.llm_call import ExpenseExtraction, llm_call
from src.rows_to_csv_bytes import rows_to_csv_bytes
from user_interface_messages import HELP_MESSAGE, START_MESSAGE

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "")
PUBLIC_URL = os.getenv("PUBLIC_URL", "")
DB_PATH = os.getenv("DB_PATH", "")
WHITELIST_IDS = [int(x) for x in os.getenv("WHITELIST_IDS", "").split(",") if x.strip()]
WEBHOOK_PATH = "/webhook"
DB_CONN = "db_conn"
ACCESS_DENIED = "Access Denied"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

assert TOKEN
assert PUBLIC_URL
assert DB_PATH
assert WHITELIST_IDS

if not TOKEN or not PUBLIC_URL:
    raise ValueError("BOT_TOKEN and PUBLIC_URL must be set in .env file")


def is_whitelisted(update: Update, owner_id: List[int]) -> bool:
    return bool(update.effective_user and update.effective_user.id in owner_id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not is_whitelisted(update, WHITELIST_IDS):
        return

    if msg is None:
        return

    if not update.effective_user or not update.effective_chat:
        return

    conn = context.bot_data[DB_CONN]
    if not await is_user_registered(conn, update.effective_user.id):
        await register_user(conn, update.effective_user.id)

    await msg.reply_text(START_MESSAGE, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    if not is_whitelisted(update, WHITELIST_IDS):
        await msg.reply_text(ACCESS_DENIED)
        return

    await msg.reply_text(HELP_MESSAGE, parse_mode="HTML")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_whitelisted(update, WHITELIST_IDS):
        msg = ACCESS_DENIED

    if update.message is None:
        return

    msg = "No conozco ese comando. Probá /help."
    await update.message.reply_text(msg)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    if not is_whitelisted(update, WHITELIST_IDS):
        await msg.reply_text(ACCESS_DENIED)
        return

    if not update.effective_user or not update.effective_chat:
        return

    conn = context.bot_data[DB_CONN]
    if not await is_user_registered(conn, update.effective_user.id):
        await register_user(conn, update.effective_user.id)

    user_categories = await get_user_categories(
        conn=context.bot_data[DB_CONN],
        user_id=update.effective_user.id,
    )

    expense_extraction: ExpenseExtraction = llm_call(
        msg.text, categories=user_categories
    )

    await add_expense(
        conn=conn,
        message_id=msg.message_id,
        chat_id=update.effective_chat.id,
        user_id=update.effective_user.id,
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        value=expense_extraction.value,
        category=expense_extraction.category,
        currency=expense_extraction.currency,
        message=msg.text,
    )

    await msg.reply_text(
        f'✅ Gasto de {expense_extraction.value} registrado en categoría "{expense_extraction.category}".'
    )


async def handle_message_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.text:
        return

    if not is_whitelisted(update, WHITELIST_IDS):
        await msg.reply_text(ACCESS_DENIED)
        return

    if not update.effective_user or not update.effective_chat:
        return

    await remove_expense_by_message_id(
        conn=context.bot_data[DB_CONN],
        message_id=msg.message_id,
        user_id=update.effective_user.id,
    )

    user_categories = await get_user_categories(
        conn=context.bot_data[DB_CONN],
        user_id=update.effective_user.id,
    )

    expense_extraction: ExpenseExtraction = llm_call(
        msg.text, categories=user_categories
    )

    conn = context.bot_data[DB_CONN]
    await add_expense(
        conn=conn,
        message_id=msg.message_id,
        chat_id=update.effective_chat.id,
        user_id=update.effective_user.id,
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        value=expense_extraction.value,
        category=expense_extraction.category,
        currency=expense_extraction.currency,
        message=msg.text,
    )

    await msg.reply_text(
        f'✅ Modificación exitosa. ✅ Gasto de {expense_extraction.value} registrado en categoría "{expense_extraction.category}".'
    )


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd_msg = update.message
    if not cmd_msg:
        return

    if not is_whitelisted(update, WHITELIST_IDS):
        await cmd_msg.reply_text(ACCESS_DENIED)
        return

    if not update.effective_user:
        return

    user_id = update.effective_user.id
    target_msg_id = None

    # If the user replied to the original expense message
    if cmd_msg.reply_to_message:
        target_msg_id = cmd_msg.reply_to_message.message_id

    # If nothing identified:
    if target_msg_id is None:
        await cmd_msg.reply_text(
            "Usá /delete respondiendo al mensaje del gasto, o /delete <message_id>."
        )
        return

    # Delete record strictly by (user_id + message_id)
    await remove_expense_by_message_id(
        conn=context.bot_data[DB_CONN],
        message_id=target_msg_id,
        user_id=user_id,
    )

    await cmd_msg.reply_text("🗑️ Gasto eliminado.")


async def csv_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg or not msg.text:
        return

    if not is_whitelisted(update, WHITELIST_IDS):
        await msg.reply_text(ACCESS_DENIED)
        return

    if not update.effective_user or not update.effective_chat:
        return

    conn = context.bot_data[DB_CONN]
    rows = await get_user_expenses_report(conn, user_id=update.effective_user.id)

    bio = rows_to_csv_bytes(rows)

    await msg.reply_document(
        document=InputFile(bio),
        caption="✅ Aquí tienes el registro de tus gastos en formato CSV 💸",
    )


tg_app = Application.builder().token(TOKEN).updater(None).build()
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("delete", delete_command))
tg_app.add_handler(CommandHandler("report", csv_command))
tg_app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
tg_app.add_handler(
    MessageHandler(
        filters.UpdateType.EDITED_MESSAGE & filters.TEXT,
        handle_message_edit,
    )
)
tg_app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.EDITED_MESSAGE,
        handle_message,
    )
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_conn = await aiosqlite.connect(DB_PATH)
    await init_db(db_conn)
    tg_app.bot_data[DB_CONN] = db_conn

    await tg_app.initialize()
    await tg_app.bot.set_my_commands(
        [
            BotCommand("help", "Ver ayuda"),
            BotCommand("start", "Introducción"),
            BotCommand("delete", "Borra el mensaje citado"),
            BotCommand("report", "Descargar gastos en CSV"),
        ]
    )

    await tg_app.bot.set_webhook(url=PUBLIC_URL + WEBHOOK_PATH)

    yield

    await tg_app.shutdown()
    await tg_app.bot.delete_webhook(drop_pending_updates=True)
    await db_conn.close()


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return {"ok": True}


@app.get("/health")
async def health():
    return {"ok": True}


# uvicorn main:app --host 0.0.0.0 --port 8080
# docker compose up --build
