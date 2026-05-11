import os

# Force-assign all values so tests are isolated from .env (Cursor and other runners
# may pre-load .env before pytest starts, making setdefault a no-op).
os.environ["TELEGRAM_BOT_TOKEN"] = "123456789:AAFakeTokenForTestingPurposesOnly"
os.environ["DB_PATH"] = ":memory:"
os.environ["WHITELIST_IDS"] = "999999999"  # generic placeholder — never a real ID
os.environ["OPENAI_API_KEY"] = "test-key-fake"
os.environ["API_SECRET"] = "test-secret"

import pytest
import aiosqlite
from src.db import init_db


@pytest.fixture
async def db_conn():
    conn = await aiosqlite.connect(":memory:")
    await init_db(conn)
    yield conn
    await conn.close()
