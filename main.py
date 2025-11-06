import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import aiosqlite
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import InputFile, Update
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
DB_PATH = "db/messages.db"
OWNER_ID = int(os.getenv("OWNER_ID", ""))
WEBHOOK_PATH = "/webhook"
DB_CONN = "db_conn"

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

assert TOKEN
assert PUBLIC_URL
assert DB_PATH
assert OWNER_ID

if not TOKEN or not PUBLIC_URL:
    raise ValueError("BOT_TOKEN and PUBLIC_URL must be set in .env file")


def is_owner(update: Update, owner_id: int) -> bool:
    return bool(update.effective_user and update.effective_user.id == owner_id)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update, OWNER_ID):
        return
    if update.message is None:
        return
    await update.message.reply_text(
        (
            "Enviá un mensaje con un gasto incluyendo monto y comentario, y si la moneda no es ARS, podés aclararla.\n\n"
            "Ejemplos:\n"
            '- "café en la facu 150"\n'
            '- "20.5 USD regalo cumple"\n'
            '- "netflix 799,99"\n\n'
        )
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if not is_owner(update, OWNER_ID):
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

    if not is_owner(update, OWNER_ID):
        await update.message.reply_text("🚫 Access denied")
        return

    if not update.effective_user or not update.effective_chat:
        return

    conn = context.bot_data[DB_CONN]
    rows = await get_user_expenses(conn, user_id=update.effective_user.id)

    bio = rows_to_csv_bytes(rows)

    await update.message.reply_document(
        document=InputFile(bio), caption="Here’s your CSV 👇"
    )


tg_app = Application.builder().token(TOKEN).updater(None).build()
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(CommandHandler("report", csv_command))
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_conn = await aiosqlite.connect(DB_PATH)
    await init_db(db_conn)
    tg_app.bot_data[DB_CONN] = db_conn

    await tg_app.initialize()
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


@app.get("/")
async def health():
    return {"ok": True}


# uvicorn main:app --host 0.0.0.0 --port 8080
