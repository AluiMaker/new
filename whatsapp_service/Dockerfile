FROM node:20-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/whatsapp_service

COPY whatsapp_service/package.json ./
RUN npm install --omit=dev --no-audit --no-fund

COPY whatsapp_service/index.js ./

RUN mkdir -p /data/wa_sessions

ENV WA_PORT=5056 \
    WA_HOST=0.0.0.0 \
    WA_AUTH_ROOT=/data/wa_sessions \
    FLASK_WEBHOOK=http://mapaleads:5055/api/wa/incoming

EXPOSE 5056

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://127.0.0.1:5056/health || exit 1

CMD ["node", "index.js"]
