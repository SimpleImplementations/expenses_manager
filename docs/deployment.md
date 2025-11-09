# 🚀 Deploy Telegram Bot on AWS EC2 using Docker, Caddy (HTTPS), DuckDNS, and SQLite

This is the complete step-by-step guide to deploy your Telegram bot on AWS EC2.  
It includes everything we actually did, including real fixes to issues that came up.

---

## 1. Project Structure (Local)

```
csv_exports/
db/
locale/
src/
main.py
requirements.txt
.env               # local development only
docker-compose.yml # local
docker-compose.prod.yml # production/server
Dockerfile
```

The bot uses:
- FastAPI
- python-telegram-bot (webhook mode)
- SQLite database
- Docker / Docker Compose
- Caddy reverse proxy (HTTPS)
- DuckDNS free domain

We will deploy **two containers**:

| Service | Description |
|--------|-------------|
| `app`  | FastAPI bot server (gunicorn + uvicorn) |
| `caddy` | Reverse proxy + automatic Let’s Encrypt HTTPS |

---

## 2. Create AWS EC2 Server

1. Go to AWS → EC2 → Launch Instance.
2. Choose Image: **Amazon Linux 2023**.
3. Instance type: `t2.micro` (Free Tier).
4. Storage: 8–16 GB.
5. Create a Security Group with:
   - SSH (22) allow your IP
   - HTTP (80) allow `0.0.0.0/0`
   - HTTPS (443) allow `0.0.0.0/0`
6. Launch instance and download `.pem` key.

### Connect:
```bash
chmod 600 ~/.ssh/telegram-bot-key.pem
ssh -i ~/.ssh/telegram-bot-key.pem ec2-user@YOUR_SERVER_IP
```

---

## 3. Install Docker + Compose

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

Install Docker Compose:
```bash
sudo curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64   -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

---

## 4. Clone Your GitHub Repo (SSH)

Generate and show key:
```bash
ssh-keygen -t ed25519 -C "ec2-bot"
cat ~/.ssh/id_ed25519.pub
```

Copy this key → GitHub → Settings → SSH Keys → Add Key.

Test:
```bash
ssh -T git@github.com
```

Clone:
```bash
git clone git@github.com:YOURUSERNAME/expenses_manager.git
cd expenses_manager
```

---

## 5. Set Domain Using DuckDNS

Go to https://www.duckdns.org  
Create a domain, e.g.:

```
telegramexpensesbot.duckdns.org
```

Add your **EC2 public IP** to DuckDNS.

---

## 6. Create Production Environment File

```bash
nano .env.prod
```

Put this inside:
```ini
TELEGRAM_BOT_TOKEN=your_botfather_token
WEBHOOK_URL=https://telegramexpensesbot.duckdns.org/telegram/webhook
WEBHOOK_SECRET_TOKEN=a_random_long_secret
DB_PATH=/var/lib/bot/bot.db
```

Do **not** commit `.env.prod`.

---

## 7. Dockerfile (Production)

```dockerfile
# ---- base ----
FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/src
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# ---- prod ----
FROM base AS prod
RUN pip install --no-cache-dir gunicorn uvicorn[standard]
ENV DB_PATH=/var/lib/bot/bot.db
CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker","main:app","--bind","0.0.0.0:8080","--workers","2","--timeout","30"]
```

---

## 8. docker-compose.prod.yml

```yaml
services:
  app:
    build:
      context: .
      target: prod
    env_file: .env.prod
    volumes:
      - ./docker_db:/var/lib/bot

  caddy:
    image: caddy:2
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

---

## 9. Caddyfile

```
telegramexpensesbot.duckdns.org {
    encode gzip
    reverse_proxy app:8080
}
```

Caddy will automatically:
- Request HTTPS certificate
- Redirect HTTP → HTTPS
- Proxy traffic to `app`

---

## 10. Deploy

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

Check logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f app
docker-compose -f docker-compose.prod.yml logs -f caddy
```

---

## 11. Test HTTPS

```bash
curl -I https://telegramexpensesbot.duckdns.org/health
```
Should return:
```
HTTP/2 200
```

---

## 12. Set Telegram Webhook

```bash
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook"   -H "Content-Type: application/json"   -d "{\"url\":\"$WEBHOOK_URL\",\"secret_token\":\"$WEBHOOK_SECRET_TOKEN\"}"
```

Verify:
```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

---

## 13. Common Fixes

| Problem | Cause | Solution |
|--------|--------|---------|
| Let’s Encrypt challenge failed | Port 80 blocked / DNS not updated | Fix Security Group + ensure DuckDNS IP matches server |
| HTTPS returned 502 | App unreachable from proxy | Validate app is running via `curl http://app:8080/health` |
| App hung on startup | Webhook set inside startup sync | Move webhook setup to background task |
 
---

## 14. Deploy Updates

```bash
git pull
docker-compose -f docker-compose.prod.yml up --build -d
```

---

## 15. Stop Services

```bash
docker-compose -f docker-compose.prod.yml down
```

---

✅ Your deployment is complete and stable.  
Your bot now runs **24/7**, **with HTTPS**, **secure webhook**, and **persistent SQLite storage**.
