# ---- base ----
FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# make both repo root and ./src importable
ENV PYTHONPATH=/app:/app/src

# install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy code
COPY . .

# ---- dev ----
FROM base AS dev
RUN pip install --no-cache-dir uvicorn[standard]
ENV DB_PATH=/var/lib/bot/bot.db
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# ---- prod ----
FROM base AS prod
RUN pip install --no-cache-dir gunicorn uvicorn[standard]
ENV DB_PATH=/var/lib/bot/bot.db
CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker","main:app","--bind","0.0.0.0:8080","--workers","2","--timeout","30"]
