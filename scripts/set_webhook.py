import os

import requests  # type: ignore
from dotenv import load_dotenv

load_dotenv(".env_prod")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing in .env_prod")

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"

payload = {"url": WEBHOOK_URL, "secret_token": WEBHOOK_SECRET_TOKEN}

response = requests.post(url, json=payload)
print("Status:", response.status_code)
print("Response:", response.text)
