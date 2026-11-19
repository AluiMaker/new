#!/usr/bin/env bash
# ==============================================================================
# MapaLeads PRO — Script de Migração Segura para Oracle Always Free ARM Ampere A1
# (VM.Standard.A1.Flex — até 4 OCPUs e 24 GB RAM gratuitos na OCI)
#
# Pré-requisitos na nova VM (Oracle Linux 8/9 ou Ubuntu 22.04/24.04 ARM64):
#   1. Portas 80 e 443 liberadas na VCN Security List / NSG.
#   2. Chave SSH com acesso à VM antiga (SOURCE_HOST) ou pacote de backup local.
#
# Uso:
#   chmod +x scripts/migrate_to_oci_ampere_a1.sh
#   SOURCE_HOST="opc@204.216.136.105" SSH_KEY="$HOME/.ssh/oracle_mapaleads.key" ./scripts/migrate_to_oci_ampere_a1.sh
# ==============================================================================
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/mapaleads-pro}"
REPO_URL="${REPO_URL:-https://github.com/AluiMaker/new.git}"
SOURCE_HOST="${SOURCE_HOST:-}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa}"
MAX_SEARCHES="${MAX_CONCURRENT_SEARCHES:-4}"

echo "=== [1/6] Verificando arquitetura e instalando Docker + Compose ==="
ARCH="$(uname -m)"
echo "Arquitetura detectada: ${ARCH}"

if ! command -v docker >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl git docker.io docker-compose-v2
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y dnf-utils git curl
    sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo || true
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  fi
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER" || true
fi

echo "=== [2/6] Abrindo firewall local (80/443) se firewalld/ufw estiver ativo ==="
if command -v firewall-cmd >/dev/null 2>&1 && sudo systemctl is-active --quiet firewalld; then
  sudo firewall-cmd --permanent --add-service=http
  sudo firewall-cmd --permanent --add-service=https
  sudo firewall-cmd --reload
elif command -v ufw >/dev/null 2>&1 && sudo ufw status | grep -q "Status: active"; then
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
fi

echo "=== [3/6] Clonando ou atualizando código do MapaLeads PRO ==="
if [ ! -d "$APP_DIR/.git" ]; then
  git clone "$REPO_URL" "$APP_DIR"
else
  git -C "$APP_DIR" pull origin main
fi
cd "$APP_DIR"

echo "=== [4/6] Transferindo .env, Snapshot SQLite consistente e Sessões WhatsApp ==="
mkdir -p "$APP_DIR/migration_tmp"
if [ -n "$SOURCE_HOST" ]; then
  echo "Gerando snapshot consistente na VM de origem ($SOURCE_HOST)..."
  ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SOURCE_HOST" \
    "docker exec mapaleads-pro python -c \"import sqlite3; src=sqlite3.connect('/data/mapaleads.db'); dst=sqlite3.connect('/data/migration_snapshot.db'); src.backup(dst); dst.close(); src.close(); print('SNAPSHOT_OK')\" && docker cp mapaleads-pro:/data/migration_snapshot.db /tmp/migration_snapshot.db && docker cp mapaleads-pro:/data/wa_sessions /tmp/migration_wa_sessions && tar -czf /tmp/migration_wa_sessions.tar.gz -C /tmp migration_wa_sessions"

  scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SOURCE_HOST:/home/opc/mapaleads-pro/.env" "$APP_DIR/.env"
  scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SOURCE_HOST:/tmp/migration_snapshot.db" "$APP_DIR/migration_tmp/mapaleads.db"
  scp -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SOURCE_HOST:/tmp/migration_wa_sessions.tar.gz" "$APP_DIR/migration_tmp/wa_sessions.tar.gz"
  chmod 600 "$APP_DIR/.env"
  echo "Dados transferidos com segurança."
else
  echo "AVISO: SOURCE_HOST não informado. Copie manualmente .env, mapaleads.db e wa_sessions antes de trocar o DNS."
fi

# Ajusta concorrência de buscas para aproveitar a nova RAM (Ampere A1 24 GB)
if [ -f "$APP_DIR/.env" ]; then
  if grep -q "^MAX_CONCURRENT_SEARCHES=" "$APP_DIR/.env"; then
    sed -i "s/^MAX_CONCURRENT_SEARCHES=.*/MAX_CONCURRENT_SEARCHES=${MAX_SEARCHES}/" "$APP_DIR/.env"
  else
    echo "MAX_CONCURRENT_SEARCHES=${MAX_SEARCHES}" >> "$APP_DIR/.env"
  fi
fi

echo "=== [5/6] Subindo stack Docker Compose (multi-arch AMD64/ARM64) ==="
docker compose build
docker compose up -d

if [ -f "$APP_DIR/migration_tmp/mapaleads.db" ]; then
  echo "Restaurando banco SQLite e sessões WhatsApp nos volumes Docker..."
  docker compose stop mapaleads mapaleads-wa
  docker cp "$APP_DIR/migration_tmp/mapaleads.db" mapaleads-pro:/data/mapaleads.db
  if [ -f "$APP_DIR/migration_tmp/wa_sessions.tar.gz" ]; then
    tar -xzf "$APP_DIR/migration_tmp/wa_sessions.tar.gz" -C "$APP_DIR/migration_tmp"
    docker cp "$APP_DIR/migration_tmp/migration_wa_sessions/." mapaleads-pro:/data/wa_sessions/
  fi
  docker compose start mapaleads-wa mapaleads
  sleep 4
fi

echo "=== [6/6] Validando integridade do banco e suíte de testes ==="
docker exec mapaleads-pro python -c "import sqlite3; c=sqlite3.connect('/data/mapaleads.db'); print('INTEGRITY:', c.execute('PRAGMA integrity_check').fetchone()[0]); print('USERS:', c.execute('SELECT COUNT(*) FROM users').fetchone()[0], 'LEADS:', c.execute('SELECT COUNT(*) FROM leads').fetchone()[0])"
docker exec mapaleads-pro python tests_master_suite.py

echo ""
echo "=============================================================================="
echo "MIGRAÇÃO CONCLUÍDA COM SUCESSO NA NOVA VM (${ARCH})!"
echo "Próximo passo: Atualize o registro DNS A de mapaleadspro.online para o IP"
echo "público desta nova VM. O Caddy renovará o SSL Let's Encrypt automaticamente."
echo "=============================================================================="
