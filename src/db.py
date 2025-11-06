from collections.abc import Iterable
from typing import List, Tuple

import aiosqlite


async def init_db(conn: aiosqlite.Connection) -> None:
    await conn.execute("PRAGMA journal_mode=WAL;")
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            date_iso TEXT NOT NULL,
            value REAL NOT NULL,
            category TEXT NOT NULL,
            currency TEXT NOT NULL,
            comment TEXT NOT NULL
        )
        """
    )
    await conn.commit()


async def add_expense(
    conn: aiosqlite.Connection,
    message_id: int,
    chat_id: int,
    user_id: int,
    date_iso: str,
    value: float,
    category: str,
    currency: str,
    comment: str,
) -> None:
    await conn.execute(
        """
        INSERT INTO expenses (message_id, chat_id, user_id, date_iso, value, category, currency, comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (message_id, chat_id, user_id, date_iso, value, category, currency, comment),
    )
    await conn.commit()


async def get_user_expenses(
    conn: aiosqlite.Connection,
    user_id: int,
) -> Iterable[aiosqlite.Row]:
    cursor = await conn.execute(
        """
        SELECT *
        FROM expenses
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    )
    rows = await cursor.fetchall()
    await cursor.close()
    return rows
