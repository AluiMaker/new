# Guia de Escala Gratuita na Oracle Cloud (OCI) — MapaLeads PRO

Este guia cobre as duas ações de infraestrutura da Fase 6:
1. **Ativar Backup Externo Criptografado no OCI Object Storage (Always Free 20 GB)** — recomendado fazer **agora**.
2. **Escalar gratuitamente para Oracle Always Free ARM Ampere A1 (4 OCPUs / 24 GB RAM)** — quando passar de ~30 assinantes ativos simultâneos.

---

## Parte 1 — Backup Externo Automático no OCI Object Storage (3 minutos · R$ 0,00)

O motor `backup_manager.py` já realiza snapshots consistentes via `sqlite3.Connection.backup()`, criptografa o pacote (DB + Sessões WhatsApp) com AES/HMAC, valida com teste real de restauração e envia automaticamente para o OCI Object Storage assim que uma PAR URL é cadastrada.

### Passo a passo no Console da Oracle Cloud:
1. Acesse o Console OCI na região **Brazil Southeast (Vinhedo) — `sa-vinhedo-1`**.
2. Vá em **Menu (☰) → Storage → Object Storage & Archive Storage → Buckets**.
3. Clique em **Create Bucket**:
   - **Bucket Name:** `mapaleads-backups`
   - **Default Storage Tier:** `Standard` (20 GB inclusos no Always Free)
   - **Visibility:** `Private`
4. Abra o bucket `mapaleads-backups` → no menu esquerdo clique em **Pre-Authenticated Requests** → **Create Pre-Authenticated Request**:
   - **Name:** `mapaleads-backup-upload`
   - **Pre-Authenticated Request Target:** `Bucket`
   - **Access Type:** `Permit object writes`
   - **Expiration:** selecione 1 ano à frente (renove anualmente)
5. Copie a **Pre-Authenticated Request URL** exibida na tela (ela só é mostrada uma vez!).
6. No **MapaLeads PRO → Painel Admin**:
   - Cole a URL no campo **OCI Object Storage PAR URL** e clique em **Salvar**.
   - Role até **Saúde do Servidor OCI & Backups Consistentes** e clique em **`Testar Envio OCI`** para validar HTTP 200 na hora.

---

## Parte 2 — Migração para Oracle Always Free ARM Ampere A1 (4 OCPUs / 24 GB RAM · R$ 0,00)

A instância atual (`VM.Standard.E2.1.Micro`) possui ~1 GB de RAM e atende bem os primeiros 15–30 assinantes usando 1 busca por vez. Quando o volume crescer, a Oracle oferece gratuitamente no **Always Free** a arquitetura **ARM Ampere A1 (`VM.Standard.A1.Flex`)** com até **4 OCPUs e 24 GB de RAM**.

Todos os containers do MapaLeads PRO (`python:3.12-slim` + `chromium`, `node:20-alpine` e `caddy:2-alpine`) já são **100% compatíveis nativamente com ARM64 (`aarch64`)**.

### Como migrar em 5 minutos sem perda de dados:
1. No Console OCI → **Compute → Instances → Create Instance**:
   - **Shape:** `VM.Standard.A1.Flex` (Ampere ARM) → configure **2 a 4 OCPUs** e **12 a 24 GB RAM** (dentro da cota Always Free).
   - **Image:** `Oracle Linux 8/9` ou `Ubuntu 24.04 Minimal aarch64`.
   - **Boot Volume:** `50 GB` a `100 GB` (Always Free permite até 200 GB no total da conta).
   - **VCN Security List:** garanta ingress rules para portas TCP `80` e `443` (`0.0.0.0/0`).
2. Acesse a nova VM via SSH e execute o script pronto do repositório:
   ```bash
   git clone https://github.com/AluiMaker/new.git ~/mapaleads-pro
   cd ~/mapaleads-pro
   chmod +x scripts/migrate_to_oci_ampere_a1.sh
   SOURCE_HOST="opc@204.216.136.105" SSH_KEY="$HOME/.ssh/oracle_mapaleads.key" MAX_CONCURRENT_SEARCHES=4 ./scripts/migrate_to_oci_ampere_a1.sh
   ```
3. O script automaticamente:
   - Instala Docker e Docker Compose na nova VM ARM64;
   - Gera um snapshot SQLite consistente (`sqlite3.Connection.backup()`) na VM antiga e transfere `.env`, banco e sessões WhatsApp;
   - Configura `MAX_CONCURRENT_SEARCHES=4` (4 buscas simultâneas no Google Maps sem fila!);
   - Sobe `mapaleads-pro`, `mapaleads-wa` e `mapaleads-caddy` e roda `tests_master_suite.py`.
4. Atualize o registro **DNS tipo A** de `mapaleadspro.online` apontando para o novo IP público. O Caddy renovará o certificado HTTPS automaticamente em segundos.
