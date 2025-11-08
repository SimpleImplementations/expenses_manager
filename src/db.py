from typing import List

import aiosqlite
from pydantic import BaseModel

from src.base_categories import BASE_CATEGORIES


# -----------------------------
# Schema Initialization
# -----------------------------
async def init_db(conn: aiosqlite.Connection) -> None:
    await conn.execute("PRAGMA journal_mode=WAL;")
    await conn.execute("PRAGMA foreign_keys=ON;")

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            created_at TEXT DEFAULT (datetime('now'))
        )
        """
    )

    # Global category catalog
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            name TEXT PRIMARY KEY
        )
        """
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_categories (
            user_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            PRIMARY KEY (user_id, category_name),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_name) REFERENCES categories(name) ON DELETE CASCADE
        )
        """
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            value REAL NOT NULL,
            category_name TEXT NOT NULL,
            currency TEXT NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (category_name) REFERENCES categories(name) ON DELETE RESTRICT
        )
        """
    )

    # Indexes
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_uc_user ON user_categories(user_id)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_uc_cat ON user_categories(category_name)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_expenses_user ON expenses(user_id, id)"
    )
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)")
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category_name)"
    )

    # Seed the global catalog with your defaults (once)
    await conn.executemany(
        "INSERT OR IGNORE INTO categories(name) VALUES (?)",
        [(n,) for n in BASE_CATEGORIES],
    )

    await conn.commit()


# -----------------------------
# User registration
# -----------------------------
async def register_user(conn: aiosqlite.Connection, user_id: int) -> None:
    """Create the user and link default categories to them."""
    await conn.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

    # Link the default categories for this user
    await conn.executemany(
        "INSERT OR IGNORE INTO user_categories (user_id, category_name) VALUES (?, ?)",
        [(user_id, n.strip()) for n in BASE_CATEGORIES if n.strip()],
    )

    await conn.commit()


async def is_user_registered(conn: aiosqlite.Connection, user_id: int) -> bool:
    cur = await conn.execute(
        "SELECT 1 FROM users WHERE user_id = ? LIMIT 1",
        (user_id,),
    )
    row = await cur.fetchone()
    await cur.close()
    return row is not None


# -----------------------------
# Category
# -----------------------------
async def add_global_category(conn: aiosqlite.Connection, name: str) -> bool:
    """Add a category to the global catalog. Returns True if created, False if it already existed."""
    name = name.strip()
    if not name:
        raise ValueError("Category name cannot be empty.")
    cur = await conn.execute(
        "INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,)
    )
    created = cur.rowcount > 0
    await cur.close()
    await conn.commit()
    return created


async def link_user_category_by_name(
    conn: aiosqlite.Connection, user_id: int, name: str
) -> bool:
    """Link an existing global category name to a user (returns True if linked)."""
    name = name.strip()
    if not name:
        raise ValueError("Category name cannot be empty.")

    # Ensure the category exists globally
    cur = await conn.execute("SELECT 1 FROM categories WHERE name = ?", (name,))
    exists = await cur.fetchone()
    await cur.close()
    if not exists:
        return False

    cur = await conn.execute(
        "INSERT OR IGNORE INTO user_categories (user_id, category_name) VALUES (?, ?)",
        (user_id, name),
    )
    await conn.commit()
    linked = cur.rowcount > 0
    await cur.close()
    return linked


async def unlink_user_category_by_name(
    conn: aiosqlite.Connection, user_id: int, name: str
) -> bool:
    """
    Unlink a user from a category by name.
    """
    name = name.strip()
    if not name:
        raise ValueError("Category name cannot be empty.")
    cur = await conn.execute(
        "DELETE FROM user_categories WHERE user_id = ? AND category_name = ?",
        (user_id, name),
    )
    removed = cur.rowcount > 0
    await cur.close()
    await conn.commit()
    return removed


async def get_user_categories(conn: aiosqlite.Connection, user_id: int) -> List[str]:
    cur = await conn.execute(
        """
        SELECT uc.category_name
        FROM user_categories uc
        WHERE uc.user_id = ?
        ORDER BY uc.category_name
        """,
        (user_id,),
    )
    rows = await cur.fetchall()
    await cur.close()
    return [r[0] for r in rows]


# -----------------------------
# Expenses
# -----------------------------


class ExpenseRow(BaseModel):
    date: str
    value: float
    category: str
    currency: str
    message: str


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
    if not category:
        raise ValueError("Category name cannot be empty.")

    # Ensure category exists globally
    cur = await conn.execute("SELECT 1 FROM categories WHERE name = ?", (category,))
    exists = await cur.fetchone()
    await cur.close()
    if not exists:
        raise ValueError(f"Category '{category}' does not exist in catalog.")

    # Ensure the user is linked to this category
    cur = await conn.execute(
        "SELECT 1 FROM user_categories WHERE user_id = ? AND category_name = ?",
        (user_id, category),
    )
    link = await cur.fetchone()
    await cur.close()
    if not link:
        raise ValueError(
            f"Category '{category}' is not linked to user {user_id}. Call link_user_category_by_name()."
        )

    await conn.execute(
        """
        INSERT INTO expenses (message_id, chat_id, user_id, date, value, category_name, currency, message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (message_id, chat_id, user_id, date, value, category, currency, message),
    )
    await conn.commit()


async def remove_expense_by_message_id(
    conn: aiosqlite.Connection,
    message_id: int,
    user_id: int,
) -> bool:
    cursor = await conn.execute(
        "DELETE FROM expenses WHERE message_id = ? AND user_id = ?",
        (message_id, user_id),
    )
    await conn.commit()
    return cursor.rowcount > 0  # True if a row was deleted


async def get_user_expenses_report(
    conn: aiosqlite.Connection, user_id: int
) -> List[ExpenseRow]:
    cursor = await conn.execute(
        """
        SELECT e.date, e.value, e.category_name AS category, e.currency, e.message
        FROM expenses e
        WHERE e.user_id = ?
        ORDER BY e.id DESC
        """,
        (user_id,),
    )
    rows = await cursor.fetchall()
    await cursor.close()
    return [
        ExpenseRow(date=r[0], value=r[1], category=r[2], currency=r[3], message=r[4])
        for r in rows
    ]
