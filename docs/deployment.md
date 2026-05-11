# Deployment

The bot runs as two containers: `app` (FastAPI + Telegram webhook handler) and `tunnel` (Cloudflare Quick Tunnel). On startup, the tunnel gets a random `trycloudflare.com` HTTPS URL, the app reads it and registers it as the Telegram webhook. No ports need to be open, no account or domain required. Setup is identical locally and on any remote server.

---

## One-time setup

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER" && newgrp docker
```

---

## First deploy

```bash
git clone <your-repo-url>
cd money_manager
cp .env.example .env   # fill in your values
```

For prod, also create the data directory:

```bash
sudo mkdir -p /srv/botdata && sudo chown -R "$USER:$USER" /srv/botdata
```

Then run:

```bash
docker compose up --build -d
docker compose logs -f
```

The logs will show the assigned `trycloudflare.com` URL and confirm the webhook was registered.

---

## Common commands

```bash
docker compose up --build -d && docker compose logs -f   # redeploy and tail logs
docker compose up --build -d   # start / redeploy
docker compose logs -f         # tail logs
docker compose down            # stop
curl -s http://localhost:8080/health
```

---

## Test

1. Message your bot: `/start`
2. Send an expense: `1000 supermercado ars`
3. Request a report: `/report`
