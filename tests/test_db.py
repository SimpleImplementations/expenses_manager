import pytest

from src.base_categories import BASE_CATEGORIES
from src.db import (
    add_expense,
    add_global_category,
    get_all_expenses,
    get_user_categories,
    get_user_expenses_report,
    is_user_registered,
    link_user_category_by_name,
    register_user,
    remove_expense_by_message_id,
    unlink_user_category_by_name,
)

USER_ID = 42
CATEGORY = "SUPERMERCADO"  # simple ASCII category guaranteed to be in BASE_CATEGORIES


# ── init_db ────────────────────────────────────────────────────────────────────

async def test_init_db_creates_tables(db_conn):
    cur = await db_conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in await cur.fetchall()}
    assert {"users", "categories", "user_categories", "expenses"}.issubset(tables)


async def test_init_db_seeds_base_categories(db_conn):
    cur = await db_conn.execute("SELECT COUNT(*) FROM categories")
    count = (await cur.fetchone())[0]
    assert count == len(BASE_CATEGORIES)


# ── register_user / is_user_registered ────────────────────────────────────────

async def test_is_user_registered_false_before_registration(db_conn):
    assert not await is_user_registered(db_conn, USER_ID)


async def test_register_user_makes_user_registered(db_conn):
    await register_user(db_conn, USER_ID)
    assert await is_user_registered(db_conn, USER_ID)


async def test_register_user_links_all_base_categories(db_conn):
    await register_user(db_conn, USER_ID)
    cats = await get_user_categories(db_conn, USER_ID)
    assert len(cats) == len(BASE_CATEGORIES)


# ── add_global_category ────────────────────────────────────────────────────────

async def test_add_global_category_new_returns_true(db_conn):
    assert await add_global_category(db_conn, "NEW_CAT") is True


async def test_add_global_category_duplicate_returns_false(db_conn):
    await add_global_category(db_conn, "NEW_CAT")
    assert await add_global_category(db_conn, "NEW_CAT") is False


async def test_add_global_category_empty_raises(db_conn):
    with pytest.raises(ValueError):
        await add_global_category(db_conn, "")


# ── link_user_category_by_name ─────────────────────────────────────────────────

async def test_link_new_category(db_conn):
    await register_user(db_conn, USER_ID)
    await add_global_category(db_conn, "NUEVA")
    assert await link_user_category_by_name(db_conn, USER_ID, "NUEVA") is True


async def test_link_nonexistent_category_returns_false(db_conn):
    await register_user(db_conn, USER_ID)
    assert await link_user_category_by_name(db_conn, USER_ID, "DOESNT_EXIST") is False


async def test_link_empty_name_raises(db_conn):
    with pytest.raises(ValueError):
        await link_user_category_by_name(db_conn, USER_ID, "")


# ── unlink_user_category_by_name ───────────────────────────────────────────────

async def test_unlink_linked_category_returns_true(db_conn):
    await register_user(db_conn, USER_ID)
    assert await unlink_user_category_by_name(db_conn, USER_ID, CATEGORY) is True


async def test_unlink_after_removing_category_not_found(db_conn):
    await register_user(db_conn, USER_ID)
    assert await unlink_user_category_by_name(db_conn, USER_ID, "NONEXISTENT") is False


async def test_unlink_empty_name_raises(db_conn):
    with pytest.raises(ValueError):
        await unlink_user_category_by_name(db_conn, USER_ID, "")


# ── get_user_categories ────────────────────────────────────────────────────────

async def test_get_user_categories_is_sorted(db_conn):
    await register_user(db_conn, USER_ID)
    cats = await get_user_categories(db_conn, USER_ID)
    assert cats == sorted(cats)


# ── add_expense ────────────────────────────────────────────────────────────────

async def test_add_expense_stored(db_conn):
    await register_user(db_conn, USER_ID)
    await add_expense(db_conn, 1, 100, USER_ID, "2024-01-01", 50.0, CATEGORY, "ARS", "compras")
    rows = await get_user_expenses_report(db_conn, USER_ID)
    assert len(rows) == 1
    assert rows[0].value == 50.0
    assert rows[0].category == CATEGORY
    assert rows[0].currency == "ARS"


async def test_add_expense_empty_category_raises(db_conn):
    await register_user(db_conn, USER_ID)
    with pytest.raises(ValueError):
        await add_expense(db_conn, 1, 100, USER_ID, "2024-01-01", 50.0, "", "ARS", "x")


async def test_add_expense_unknown_category_raises(db_conn):
    await register_user(db_conn, USER_ID)
    with pytest.raises(ValueError, match="does not exist"):
        await add_expense(db_conn, 1, 100, USER_ID, "2024-01-01", 50.0, "GHOST_CAT", "ARS", "x")


async def test_add_expense_unlinked_category_raises(db_conn):
    await register_user(db_conn, USER_ID)
    await add_global_category(db_conn, "GLOBAL_ONLY")
    with pytest.raises(ValueError, match="not linked"):
        await add_expense(db_conn, 1, 100, USER_ID, "2024-01-01", 50.0, "GLOBAL_ONLY", "ARS", "x")


# ── remove_expense_by_message_id ───────────────────────────────────────────────

async def test_remove_expense_returns_true(db_conn):
    await register_user(db_conn, USER_ID)
    await add_expense(db_conn, 99, 100, USER_ID, "2024-01-01", 100.0, CATEGORY, "ARS", "to delete")
    assert await remove_expense_by_message_id(db_conn, 99, USER_ID) is True
    assert await get_user_expenses_report(db_conn, USER_ID) == []


async def test_remove_nonexistent_expense_returns_false(db_conn):
    await register_user(db_conn, USER_ID)
    assert await remove_expense_by_message_id(db_conn, 999, USER_ID) is False


# ── get_all_expenses ───────────────────────────────────────────────────────────

async def test_get_all_expenses_empty(db_conn):
    assert await get_all_expenses(db_conn) == []


async def test_get_all_expenses_shape(db_conn):
    await register_user(db_conn, USER_ID)
    await add_expense(db_conn, 1, 100, USER_ID, "2024-01-01", 75.0, CATEGORY, "USD", "test")
    rows = await get_all_expenses(db_conn)
    assert len(rows) == 1
    assert rows[0]["user_id"] == USER_ID
    assert rows[0]["value"] == 75.0
    assert rows[0]["currency"] == "USD"
    assert rows[0]["category"] == CATEGORY
    assert "date" in rows[0]
    assert "message" in rows[0]
