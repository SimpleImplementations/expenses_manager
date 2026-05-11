# AWS EC2 Deployment

## Prerequisites

- An EC2 instance running Ubuntu (t2.micro or larger)
- Your `.pem` key file (downloaded from AWS when you created the instance)

---

## Connect to the EC2

**Find your key** — it's wherever you saved it when creating the EC2 instance:

```bash
find ~ -name "*.pem" 2>/dev/null
```

**Lock permissions** (SSH refuses keys that are too open):

```bash
chmod 400 /path/to/your-key.pem
```

**Connect:**

```bash
ssh -i /path/to/your-key.pem ec2-user@<your-ec2-ip>
```

> Find your public IP in AWS Console → EC2 → Instances → Public IPv4 address.

---

## One-time server setup

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER" && newgrp docker
```

---

## One-time app setup

```bash
git clone <your-repo-url>
cd money_manager
sudo mkdir -p /srv/botdata && sudo chown -R "$USER:$USER" /srv/botdata
cp .env.example .env
nano .env
```

Fill in `.env`:

```env
BUILD_TARGET=prod
DB_VOLUME=/srv/botdata

TELEGRAM_BOT_TOKEN=<from @BotFather>
WHITELIST_IDS=<your Telegram user ID — get it from @userinfobot>
OPENAI_API_KEY=<your OpenAI key>
WEBHOOK_URL=/telegram/webhook
WEBHOOK_SECRET_TOKEN=<run: openssl rand -hex 16>
API_SECRET=<run: openssl rand -hex 32>
```

---

## Deploy

```bash
docker compose up --build -d
docker compose logs -f
```

Wait for the logs to show:
```
Tunnel URL: https://xxxx.trycloudflare.com
Bot ready at https://xxxx.trycloudflare.com/telegram/webhook
```

Verify:
```bash
curl -s http://localhost:8080/health
# → {"ok":true}
```

Then message your bot `/start` on Telegram.

---

## Auto-deploy on push to main (GitHub Actions)

Add these secrets in GitHub → repo → Settings → Secrets → Actions:

| Secret | Value |
|---|---|
| `EC2_HOST` | your EC2 public IP |
| `EC2_USER` | `ec2-user` |
| `EC2_SSH_KEY` | contents of your `.pem` file (`cat /path/to/your-key.pem`) |
| `EC2_APP_DIR` | `/home/ec2-user/money_manager` |

After that, every push to `main` SSHes into the EC2 and runs `git pull && docker compose up --build -d` automatically.

---

## Common commands

```bash
docker compose up --build -d && docker compose logs -f   # redeploy and tail logs
docker compose logs -f                                    # tail logs only
docker compose down                                       # stop everything
curl -s http://localhost:8080/health                      # health check
```

---

## Lost your SSH key?

Generate a new pair on your machine:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/ec2-key
```

Then use AWS Console → EC2 → Actions → Connect → EC2 Instance Connect (browser-based) to paste the contents of `~/.ssh/ec2-key.pub` into `~/.ssh/authorized_keys` on the server. After that, connect normally with `-i ~/.ssh/ec2-key`.
