FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROME_BIN=/usr/bin/chromium \
    WA_AUTH_ROOT=/data/wa_sessions \
    ENABLE_BAILEYS_AUTOSTART=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    ca-certificates \
    curl \
    git \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxss1 \
    libasound2 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY whatsapp_service/package.json ./whatsapp_service/
RUN cd whatsapp_service && npm install --omit=dev --no-audit --no-fund

COPY . .

RUN mkdir -p /data/wa_sessions /data/backups
ENV DATABASE_PATH=/data/mapaleads.db

EXPOSE 5055

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT:-5055}/health || exit 1

CMD ["sh", "-c", "mkdir -p /data/wa_sessions /data/backups && if [ -z \"$WA_SERVICE_URL\" ]; then (while true; do node /app/whatsapp_service/index.js >> /data/wa_service.log 2>&1; sleep 3; done) & fi && exec gunicorn --worker-class gthread --workers 1 --threads 32 --timeout 180 --bind 0.0.0.0:${PORT:-5055} server:app"]
