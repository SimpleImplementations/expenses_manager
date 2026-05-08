# 🚀 Deploy on an always-on Ubuntu server (long polling, no webhook)

This guide deploys the bot on a **local Ubuntu server** (always on) using:

- Docker + Docker Compose
- A single container (`app`)
- SQLite persisted to `/srv/botdata`
- **Telegram long polling** (no public URL, no reverse proxy, no DuckDNS)

With polling, your server only needs **outbound** internet access. No ports need to be open to the public.

---

## 1. One-time setup on the Ubuntu server

Install Docker Engine + Compose plugin (Ubuntu):

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
newgrp docker
docker --version
docker compose version
```

Create a persistent data directory for SQLite:

```bash
sudo mkdir -p /srv/botdata
sudo chown -R "$USER:$USER" /srv/botdata
```

---

## 2. Get the code on the server

```bash
git clone <your-repo-url>
cd money_manager
```

---

## 3. Create the env file (server-only)

Create `.env` in the repo root (this file must NOT be committed):

```ini
TELEGRAM_BOT_TOKEN=your_botfather_token
WHITELIST_IDS=123456789,987654321
OPENAI_API_KEY=your_openai_key

# optional (compose already sets this, but keeping it here is fine too)
DB_PATH=/var/lib/bot/bot.db
```

Notes:
- `WHITELIST_IDS` are the Telegram user IDs allowed to use the bot.
- `DB_PATH` is inside the container; the actual DB persists in `/srv/botdata` on the host.

---

## 4. Deploy (build + run)

```bash
docker compose up --build -d
```

Check logs:

```bash
docker compose logs -f app
```

You should see the bot start and begin polling.

---

## 5. Test with Telegram (fastest checklist)

1. Open Telegram and message your bot: `/start`
2. Try a simple expense message, for example:
   - `1000 supermercado ars`
3. Request a report:
   - `/report`

If it replies, polling is working.

---

## 6. Health check (optional)

The container also exposes a simple health endpoint on the server:

```bash
curl -s http://localhost:8080/health
```

---

## 7. Update / restart

```bash
git pull
docker compose up --build -d
```

Stop:

```bash
docker compose down
```
