# Useful commands (local server / long polling)

## Run / logs

```bash
docker compose up --build -d
docker compose logs -f app
```

## Health check

```bash
curl -s http://localhost:8080/health
```

## Re-deploy after an update

```bash
git pull
docker compose up --build -d
```

## Stop

```bash
docker compose down
```
