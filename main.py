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

from src.db import add_expense, get_user_expenses, init_db
from src.llm_call import ExpenseExtraction, llm_call
from src.rows_to_csv_bytes import rows_to_csv_bytes

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "")
PUBLIC_URL = os.getenv("PUBLIC_URL", "")
DB_PATH = os.getenv("DB_PATH", "")
WHITELIST_IDS = [int(x) for x in os.getenv("WHITELIST_IDS", "").split(",") if x.strip()]
WEBHOOK_PATH = "/webhook"
DB_CONN = "db_conn"

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
    if not is_whitelisted(update, WHITELIST_IDS):
        return
    if update.message is None:
        return
    await update.message.reply_text(
        "👋 Bienvenido.\n\n"
        "Enviá un mensaje con un gasto incluyendo monto y comentario, y si la moneda no es ARS, podés aclararla.\n\n"
        "Ejemplos:\n"
        '- "café en la facu 150"\n'
        '- "20.5 USD regalo cumple"\n'
        '- "netflix 799,99"\n\n'
        "ℹ️ Usá /help para ver todos los comandos."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    if not is_whitelisted(update, WHITELIST_IDS):
        await update.message.reply_text("🚫 Access denied")
        return

    text = (
        "📖 *Ayuda*\n\n"
        "Comandos disponibles:\n"
        "• /help — muestra esta ayuda\n"
        "• /start — introducción rápida\n"
        "• /report — descarga tus gastos en CSV\n\n"
        "Además, podés registrar gastos simplemente escribiendo el texto del gasto, por ejemplo:\n"
        "• `almuerzo 2500`\n"
        "• `20.5 USD regalo cumple`\n"
        "• `netflix 799,99`\n"
    )
    await update.message.reply_markdown_v2(text)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    msg = "No conozco ese comando. Probá /help."
    if not is_whitelisted(update, WHITELIST_IDS):
        msg = "🚫 Access denied"
    await update.message.reply_text(msg)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if not is_whitelisted(update, WHITELIST_IDS):
        await update.message.reply_text("🚫 Access denied")
        return

    if not update.effective_user or not update.effective_chat:
        return

    expense_extraction: ExpenseExtraction = llm_call(update.message.text)

    conn = context.bot_data[DB_CONN]
    await add_expense(
        conn=conn,
        message_id=update.message.message_id,
        chat_id=update.effective_chat.id,
        user_id=update.effective_user.id,
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        value=expense_extraction.value,
        category=expense_extraction.category,
        currency=expense_extraction.currency,
        message=update.message.text,
    )

    await update.message.reply_text(
        f'✅ Gasto de {expense_extraction.value} registrado en categoría "{expense_extraction.category}".'
    )


async def csv_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    if not is_whitelisted(update, WHITELIST_IDS):
        await update.message.reply_text("🚫 Access denied")
        return

    if not update.effective_user or not update.effective_chat:
        return

    conn = context.bot_data[DB_CONN]
    rows = await get_user_expenses(conn, user_id=update.effective_user.id)

    bio = rows_to_csv_bytes(rows)

    await update.message.reply_document(
        document=InputFile(bio), caption="CSV descargado 👇"
    )


tg_app = Application.builder().token(TOKEN).updater(None).build()
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("report", csv_command))
tg_app.add_handler(CommandHandler("help", help_command))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
tg_app.add_handler(MessageHandler(filters.COMMAND, unknown_command))


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
