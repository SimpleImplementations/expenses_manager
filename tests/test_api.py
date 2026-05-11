import pytest
import httpx
import aiosqlite

from src.db import add_expense, init_db, register_user

CATEGORY = "SUPERMERCADO"
AUTH_HEADER = {"Authorization": "Bearer test-secret"}


@pytest.fixture
async def api_client():
    # Import here so conftest env vars are set first
    from main import DB_CONN, app, tg_app

    conn = await aiosqlite.connect(":memory:")
    await init_db(conn)
    tg_app.bot_data[DB_CONN] = conn
    app.state.public_url = "https://test.trycloudflare.com"

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, conn

    await conn.close()


# ── /health ────────────────────────────────────────────────────────────────────

async def test_health_ok(api_client):
    client, _ = api_client
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


# ── /api/tunnel-url ────────────────────────────────────────────────────────────

async def test_tunnel_url(api_client):
    client, _ = api_client
    resp = await client.get("/api/tunnel-url")
    assert resp.status_code == 200
    assert resp.json()["url"] == "https://test.trycloudflare.com"


# ── /api/expenses — auth ───────────────────────────────────────────────────────

async def test_expenses_missing_auth_returns_403(api_client):
    client, _ = api_client
    resp = await client.get("/api/expenses")
    assert resp.status_code == 403


async def test_expenses_wrong_token_returns_403(api_client):
    client, _ = api_client
    resp = await client.get("/api/expenses", headers={"Authorization": "Bearer wrong-token"})
    assert resp.status_code == 403


async def test_expenses_malformed_header_returns_403(api_client):
    client, _ = api_client
    resp = await client.get("/api/expenses", headers={"Authorization": "test-secret"})
    assert resp.status_code == 403


# ── /api/expenses — data ───────────────────────────────────────────────────────

async def test_expenses_valid_auth_empty_db(api_client):
    client, _ = api_client
    resp = await client.get("/api/expenses", headers=AUTH_HEADER)
    assert resp.status_code == 200
    assert resp.json() == []


async def test_expenses_returns_stored_data(api_client):
    client, conn = api_client
    await register_user(conn, 42)
    await add_expense(conn, 1, 100, 42, "2024-06-01", 150.0, CATEGORY, "ARS", "verduras")

    resp = await client.get("/api/expenses", headers=AUTH_HEADER)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["user_id"] == 42
    assert data[0]["value"] == 150.0
    assert data[0]["category"] == CATEGORY
    assert data[0]["currency"] == "ARS"


async def test_expenses_multiple_users(api_client):
    client, conn = api_client
    await register_user(conn, 1)
    await register_user(conn, 2)
    await add_expense(conn, 1, 100, 1, "2024-06-01", 100.0, CATEGORY, "ARS", "a")
    await add_expense(conn, 2, 100, 2, "2024-06-02", 200.0, CATEGORY, "USD", "b")

    resp = await client.get("/api/expenses", headers=AUTH_HEADER)
    data = resp.json()
    assert len(data) == 2
    user_ids = {row["user_id"] for row in data}
    assert user_ids == {1, 2}
