# Dashboard

The dashboard is a local Streamlit app that fetches expense data from the bot's API. It runs on your machine — nothing to deploy.

---

## One-time setup

1. Add to `.env` on the server and redeploy:
   ```
   API_SECRET=any_random_string
   ```
   Generate one with: `openssl rand -hex 32`

2. On your local machine, inside `dashboard/`:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   Edit `secrets.toml`:
   ```toml
   bot_url = "https://your-tunnel-url.trycloudflare.com"
   api_secret = "same_value_as_API_SECRET"
   ```
   Get the current tunnel URL by sending `/tunnelurl` to the bot.

3. Install and run:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```

---

## Getting the tunnel URL

The tunnel URL changes on every bot restart. Send `/tunnelurl` to the bot to get the current one, then update `bot_url` in `secrets.toml`.
