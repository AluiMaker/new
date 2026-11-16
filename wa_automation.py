"""
Motor de Prospecção Automática via WhatsApp (Baileys).

Fluxo:
 1. Pega leads em 'novo' com telefone (filtros configuráveis).
 2. Envia a Copy 1 com variáveis preenchidas, com intervalo humano aleatório.
 3. Move o lead para 'contatado' e grava data do contato.
 4. Quando o lead responde (webhook /api/wa/incoming), marca 'respondeu'
    e envia automaticamente a Copy 2 (agendamento) — apenas uma vez.
"""
import json
import random
import re
import subprocess
import os
import threading
import time
import urllib.request
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from database import get_connection, update_lead, get_pitch_templates

WA_BASE = "http://127.0.0.1:5056"
SERVICE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_service")

_node_proc: Optional[subprocess.Popen] = None


# ==================== COMUNICAÇÃO COM O MICROSERVIÇO ====================
def wa_request(method: str, path: str, payload: Optional[dict] = None, timeout: int = 30) -> Dict[str, Any]:
    data = json.dumps(payload or {}).encode("utf-8") if method == "POST" else None
    req = urllib.request.Request(
        WA_BASE + path, data=data, method=method,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8"))
        except Exception:
            return {"success": False, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"success": False, "error": str(e), "offline": True}


def ensure_service_running() -> bool:
    """Sobe o microserviço Node automaticamente se não estiver no ar."""
    global _node_proc
    st = wa_request("GET", "/status", timeout=2)
    if not st.get("offline"):
        return True
    if not os.path.isdir(os.path.join(SERVICE_DIR, "node_modules")):
        return False
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    log = open(os.path.join(SERVICE_DIR, "service.log"), "a", encoding="utf-8")
    _node_proc = subprocess.Popen(
        ["node", "index.js"], cwd=SERVICE_DIR,
        stdout=log, stderr=log, creationflags=flags
    )
    for _ in range(20):
        time.sleep(0.5)
        if not wa_request("GET", "/status", timeout=2).get("offline"):
            return True
    return False


def stop_service():
    global _node_proc
    if _node_proc:
        try:
            _node_proc.terminate()
        except Exception:
            pass
        _node_proc = None


# ==================== CONFIGURAÇÃO PERSISTIDA ====================
DEFAULT_CONFIG = {
    "template_id": "autoridade_perda",
    "delay_min": 45,
    "delay_max": 90,
    "daily_limit": 40,
    "only_no_website": True,
    "only_mobile": True,
    "auto_followup": True,
    "work_start": 8,
    "work_end": 19,
}


def get_config() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM whatsapp_config WHERE key = 'automation'")
    row = cur.fetchone()
    conn.close()
    cfg = dict(DEFAULT_CONFIG)
    if row:
        try:
            cfg.update(json.loads(row["value"]))
        except Exception:
            pass
    return cfg


def save_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    merged = get_config()
    for k in DEFAULT_CONFIG:
        if k in cfg:
            merged[k] = cfg[k]
    merged["delay_min"] = max(15, int(merged["delay_min"]))
    merged["delay_max"] = max(merged["delay_min"] + 5, int(merged["delay_max"]))
    merged["daily_limit"] = max(1, min(200, int(merged["daily_limit"])))
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO whatsapp_config (key, value) VALUES ('automation', ?)",
        (json.dumps(merged),)
    )
    conn.commit()
    conn.close()
    return merged


# ==================== UTILITÁRIOS ====================
def fill_variables(text: str, lead: Dict[str, Any]) -> str:
    rating = lead.get("rating")
    return (text or "") \
        .replace("{nome}", lead.get("name") or "sua empresa") \
        .replace("{categoria}", lead.get("category") or "seu segmento") \
        .replace("{rua}", lead.get("street") or "sua rua") \
        .replace("{bairro}", lead.get("neighborhood") or "sua região") \
        .replace("{avaliacao}", str(rating).replace(".", ",") if rating else "5,0") \
        .replace("{avaliacoes}", str(lead.get("reviews_count") or "várias"))


def sent_today() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM wa_messages WHERE direction = 'out' AND kind = 'pitch' AND created_at LIKE ?",
        (f"{today}%",)
    )
    n = cur.fetchone()[0]
    conn.close()
    return n


def log_message(lead_id: Optional[int], phone: str, direction: str, kind: str, text: str, status: str = "ok"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO wa_messages (lead_id, phone, direction, kind, text, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (lead_id, phone, direction, kind, text, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


from database import get_connection, update_lead, get_pitch_templates, is_phone_already_contacted

def get_queue(cfg: Dict[str, Any], limit: int = 500) -> List[Dict[str, Any]]:
    sql = """SELECT * FROM leads
             WHERE crm_status = 'novo' AND had_contact = 0
               AND clean_phone IS NOT NULL AND clean_phone != ''
               AND COALESCE(whatsapp_status, 'pendente') IN ('pendente', '')"""
    if cfg.get("only_no_website"):
        sql += " AND (website_type IN ('none', 'social', 'directory') OR website IS NULL)"
    if cfg.get("only_mobile"):
        sql += " AND is_whatsapp = 1"
    sql += " ORDER BY reviews_count DESC, id ASC LIMIT ?"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, (limit * 3,))  # Busca margem para dedup
    raw_rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    valid_queue: List[Dict[str, Any]] = []
    seen_tails = set()
    for r in raw_rows:
        phone = r.get("clean_phone")
        if not phone:
            continue
        digits = "".join(c for c in str(phone) if c.isdigit())
        if len(digits) < 8:
            continue
        tail = digits[-8:]
        if tail in seen_tails:
            continue
        seen_tails.add(tail)
        if is_phone_already_contacted(phone):
            # Corrige no banco para sair da fila permanentemente
            update_lead(r["id"], {"had_contact": 1, "whatsapp_status": "ja_contatado"})
            continue
        valid_queue.append(r)
        if len(valid_queue) >= limit:
            break

    return valid_queue


def get_queue_summary(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    c = cfg or get_config()
    queue = get_queue(c, limit=200)
    return {
        "count": len(queue),
        "sent_today": sent_today(),
        "daily_limit": c["daily_limit"],
        "preview": [{"id": l["id"], "name": l["name"], "phone": l["phone"], "category": l["category"]} for l in queue[:15]]
    }


def get_template(template_id: str) -> Optional[Dict[str, Any]]:
    tpls = get_pitch_templates()
    return next((t for t in tpls if t["id"] == template_id), tpls[0] if tpls else None)


# ==================== CAMPANHA ====================
class CampaignRunner:
    def __init__(self, broadcast: Callable[[str, Any], None]):
        self.broadcast = broadcast
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.state = {
            "running": False, "sent": 0, "failed": 0, "skipped": 0,
            "current": None, "next_send_at": None, "message": "Parado"
        }

    def _emit(self, msg: str):
        self.state["message"] = msg
        self.broadcast("wa_campaign", dict(self.state))

    def start(self) -> Dict[str, Any]:
        if self.state["running"]:
            return {"success": False, "error": "Campanha já está em execução."}
        st = wa_request("GET", "/status", timeout=3)
        if st.get("state") != "connected":
            return {"success": False, "error": "Conecte o WhatsApp pelo QR Code antes de iniciar."}
        self.stop_event.clear()
        self.state.update({"running": True, "sent": 0, "failed": 0, "skipped": 0, "current": None})
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return {"success": True}

    def stop(self):
        self.stop_event.set()
        self.state["running"] = False
        self._emit("Campanha pausada pelo usuário.")

    def _sleep(self, seconds: float) -> bool:
        """Dorme em fatias; retorna False se a campanha foi interrompida."""
        self.state["next_send_at"] = time.time() + seconds
        return not self.stop_event.wait(seconds)

    def _run(self):
        cfg = get_config()
        tpl = get_template(cfg["template_id"])
        if not tpl:
            self.state["running"] = False
            self._emit("Nenhum modelo de copy encontrado.")
            return

        self._emit("Campanha iniciada.")
        seen_in_campaign = set()
        try:
            while not self.stop_event.is_set():
                hour = datetime.now().hour
                if not (cfg["work_start"] <= hour < cfg["work_end"]):
                    self._emit(f"Fora do horário comercial ({cfg['work_start']}h–{cfg['work_end']}h). Aguardando...")
                    if not self._sleep(300):
                        break
                    continue

                if sent_today() >= cfg["daily_limit"]:
                    self._emit(f"Limite diário de {cfg['daily_limit']} envios atingido. Retoma amanhã.")
                    break

                queue = get_queue(cfg, limit=1)
                if not queue:
                    self._emit("Fila vazia: todos os leads elegíveis já foram contatados.")
                    break

                lead = queue[0]
                lead_phone = lead.get("clean_phone") or ""
                digits = "".join(c for c in lead_phone if c.isdigit())
                tail = digits[-8:] if len(digits) >= 8 else digits

                # Dupla validação antes do disparo: NUNCA reenviar se já foi contatado ou enviado na campanha
                if (tail and tail in seen_in_campaign) or is_phone_already_contacted(lead_phone):
                    update_lead(lead["id"], {
                        "had_contact": 1,
                        "whatsapp_status": "ja_contatado",
                        "crm_status": "contatado" if lead.get("crm_status") == "novo" else lead.get("crm_status")
                    })
                    self.state["skipped"] += 1
                    self.broadcast("queue_updated", get_queue_summary(cfg))
                    continue

                if tail:
                    seen_in_campaign.add(tail)

                self.state["current"] = lead["name"]
                text = fill_variables(tpl["content"], lead)
                self._emit(f"Enviando para {lead['name']} ({lead['phone']})...")

                res = wa_request("POST", "/send", {"phone": lead["clean_phone"], "text": text}, timeout=60)

                if res.get("success"):
                    self.state["sent"] += 1
                    update_lead(lead["id"], {
                        "had_contact": 1,
                        "contact_date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "crm_status": "contatado",
                        "whatsapp_status": "enviado",
                    })
                    log_message(lead["id"], lead["clean_phone"], "out", "pitch", text)
                    self.broadcast("lead_updated", {"id": lead["id"], "crm_status": "contatado"})
                    self.broadcast("queue_updated", get_queue_summary(cfg))
                elif res.get("not_on_whatsapp"):
                    self.state["skipped"] += 1
                    update_lead(lead["id"], {"whatsapp_status": "sem_whatsapp"})
                    self.broadcast("queue_updated", get_queue_summary(cfg))
                    self._emit(f"{lead['name']} não possui WhatsApp. Pulando.")
                    continue  # não precisa esperar intervalo
                else:
                    self.state["failed"] += 1
                    update_lead(lead["id"], {"whatsapp_status": "falha"})
                    log_message(lead["id"], lead["clean_phone"], "out", "pitch", text, status="erro")
                    self.broadcast("queue_updated", get_queue_summary(cfg))
                    self._emit(f"Falha ao enviar para {lead['name']}: {res.get('error')}")
                    if res.get("offline") or "não conectado" in str(res.get("error", "")):
                        break

                delay = random.uniform(cfg["delay_min"], cfg["delay_max"])
                self._emit(f"Enviado. Próximo envio em {int(delay)}s (intervalo humano).")
                if not self._sleep(delay):
                    break
        finally:
            self.state["running"] = False
            self.state["current"] = None
            self.state["next_send_at"] = None
            self._emit(self.state["message"] if "Limite" in self.state["message"] or "Fila" in self.state["message"]
                       else "Campanha finalizada.")


# ==================== RESPOSTAS RECEBIDAS ====================
def find_lead_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    digits = re.sub(r"\D", "", phone or "")
    if not digits:
        return None
    # WhatsApp às vezes omite o 9º dígito em números antigos — compara pelos 8 últimos
    tail = digits[-8:]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads WHERE clean_phone LIKE ? ORDER BY had_contact DESC LIMIT 1", (f"%{tail}",))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def handle_incoming(phone: str, text: str, broadcast: Callable[[str, Any], None]) -> Dict[str, Any]:
    lead = find_lead_by_phone(phone)
    if not lead:
        return {"matched": False}

    log_message(lead["id"], phone, "in", "reply", text)
    result = {"matched": True, "lead_id": lead["id"], "followup_sent": False}

    first_reply = not lead.get("had_reply")
    fields = {"had_reply": 1}
    if lead.get("crm_status") in ("novo", "contatado"):
        fields["crm_status"] = "respondeu"
    update_lead(lead["id"], fields)

    cfg = get_config()
    if first_reply and cfg.get("auto_followup") and lead.get("whatsapp_status") == "enviado":
        tpl = get_template(cfg["template_id"])
        follow = fill_variables((tpl or {}).get("follow_up") or "", lead)
        if follow.strip():
            time.sleep(random.uniform(8, 20))  # parece humano lendo a mensagem
            res = wa_request("POST", "/send", {"phone": lead["clean_phone"], "text": follow}, timeout=60)
            if res.get("success"):
                update_lead(lead["id"], {"whatsapp_status": "followup_enviado"})
                log_message(lead["id"], lead["clean_phone"], "out", "followup", follow)
                result["followup_sent"] = True

    broadcast("lead_reply", {
        "id": lead["id"], "name": lead["name"], "text": text[:200],
        "followup_sent": result["followup_sent"]
    })
    return result


def get_conversation(lead_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM wa_messages WHERE lead_id = ? ORDER BY id ASC", (lead_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_recent_activity(limit: int = 30) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT m.*, l.name AS lead_name FROM wa_messages m
                   LEFT JOIN leads l ON l.id = m.lead_id
                   ORDER BY m.id DESC LIMIT ?""", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
