FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/chromium \
    ENABLE_BAILEYS_AUTOSTART=0

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data
ENV DATABASE_PATH=/data/mapaleads.db

EXPOSE 5055

CMD ["sh", "-c", "gunicorn --worker-class gthread --workers 1 --threads 8 --timeout 120 --bind 0.0.0.0:${PORT:-5055} server:app"]

