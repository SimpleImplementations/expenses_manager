from typing import List

import aiosqlite
from pydantic import BaseModel


async def init_db(conn: aiosqlite.Connection) -> None:
    await conn.execute("PRAGMA journal_mode=WAL;")
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            value REAL NOT NULL,
            category TEXT NOT NULL,
            currency TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    await conn.commit()


async def add_expense(
    conn: aiosqlite.Connection,
    message_id: int,
    chat_id: int,
    user_id: int,
    date: str,
    value: float,
    category: str,
    currency: str,
    message: str,
) -> None:
    await conn.execute(
        """
        INSERT INTO expenses (message_id, chat_id, user_id, date, value, category, currency, message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (message_id, chat_id, user_id, date, value, category, currency, message),
    )
    await conn.commit()


class ExpenseRow(BaseModel):
    date: str
    value: float
    category: str
    currency: str
    message: str


async def get_user_expenses(
    conn: aiosqlite.Connection,
    user_id: int,
) -> List[ExpenseRow]:
    cursor = await conn.execute(
        """
        SELECT date, value, category, currency, message
        FROM expenses
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = await cursor.fetchall()
    await cursor.close()

    return [
        ExpenseRow(
            date=row[0],
            value=row[1],
            category=row[2],
            currency=row[3],
            message=row[4],
        )
        for row in rows
    ]
