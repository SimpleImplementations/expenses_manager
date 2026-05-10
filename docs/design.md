# Design decisions

## Telegram webhook via Cloudflare Quick Tunnel

The bot uses Telegram webhooks (not long polling) for update delivery. To avoid needing a public IP, a static domain, or any manual DNS configuration, we run a `cloudflare/cloudflared` sidecar container in quick tunnel mode.

On every startup, Cloudflare assigns a random `trycloudflare.com` HTTPS URL. The app reads it from the cloudflared metrics API (`http://tunnel:2999/quicktunnel`) and immediately registers it as the Telegram webhook via `set_webhook`. This means the URL changes on each restart, but since registration is automatic, it requires no manual intervention.

**Why not long polling:** polling works without a public URL but keeps a persistent outbound connection open and adds ~1s latency per update. Webhooks are cleaner and standard.

**Why not a named Cloudflare Tunnel:** requires a domain managed by Cloudflare. Quick tunnels are free, need no account, and are sufficient for a personal bot.

**Why not DuckDNS:** DuckDNS domains cannot use Cloudflare nameservers, so they are incompatible with named Cloudflare Tunnels. The old setup required manually updating the DuckDNS IP after each EC2 restart.

**Escape hatch:** if a stable URL is ever needed (e.g. for a named tunnel), set `PUBLIC_URL` in `.env` and the app skips the metrics poll entirely and uses that value directly.
