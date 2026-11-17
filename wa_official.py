"""
Integração com a API Oficial do WhatsApp (Meta WhatsApp Cloud API).

Documentação oficial:
https://developers.facebook.com/docs/whatsapp/cloud-api
"""
import json
import re
import urllib.request
import urllib.error
from datetime import datetime
from typing import Any, Dict, List, Optional

from database import (
    get_connection,
    find_user_by_phone_number_id,
    update_lead,
)


def _normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", str(phone or ""))
    if not digits:
        return ""
    if not digits.startswith("55") and len(digits) in (10, 11):
        digits = "55" + digits
    return digits


def _graph_request(
    method: str,
    url: str,
    access_token: str,
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 20,
) -> Dict[str, Any]:
    if not access_token:
        return {"success": False, "error": "Access Token da Meta não configurado."}

    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {access_token.strip()}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "data": body}
    except urllib.error.HTTPError as e:
        raw = ""
        try:
            raw = e.read().decode("utf-8")
            err_json = json.loads(raw)
            msg = err_json.get("error", {}).get("message") or raw
            code = err_json.get("error", {}).get("code")
            return {"success": False, "error": msg, "code": code, "http_status": e.code}
        except Exception:
            return {"success": False, "error": raw or f"HTTP {e.code}", "http_status": e.code}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_connection(phone_number_id: str, access_token: str, api_version: str = "v21.0") -> Dict[str, Any]:
    """Valida o Phone Number ID e Access Token na Graph API da Meta."""
    pid = (phone_number_id or "").strip()
    if not pid:
        return {"success": False, "error": "Informe o Phone Number ID."}
    ver = (api_version or "v21.0").strip()
    url = f"https://graph.facebook.com/{ver}/{pid}?fields=id,display_phone_number,verified_name,quality_rating"
    res = _graph_request("GET", url, access_token)
    if not res.get("success"):
        return res
    d = res.get("data", {})
    return {
        "success": True,
        "id": d.get("id"),
        "display_phone_number": d.get("display_phone_number", ""),
        "verified_name": d.get("verified_name", ""),
        "quality_rating": d.get("quality_rating", ""),
    }


def exchange_code_for_token(
    app_id: str,
    app_secret: str,
    code: str,
    api_version: str = "v21.0",
) -> Dict[str, Any]:
    """Troca o authorization code do Embedded Signup da Meta por um Access Token."""
    if not app_id or not app_secret or not code:
        return {"success": False, "error": "META_APP_ID, META_APP_SECRET ou code ausente."}
    ver = (api_version or "v21.0").strip()
    url = (
        f"https://graph.facebook.com/{ver}/oauth/access_token"
        f"?client_id={app_id.strip()}&client_secret={app_secret.strip()}&code={code.strip()}"
    )
    try:
        with urllib.request.urlopen(url, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tok = data.get("access_token")
            if not tok:
                return {"success": False, "error": "Meta não retornou access_token."}
            return {"success": True, "access_token": tok}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        return {"success": False, "error": f"Erro ao trocar código na Meta: {raw}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def subscribe_waba_webhook(
    waba_id: str,
    access_token: str,
    api_version: str = "v21.0",
) -> Dict[str, Any]:
    """Inscreve automaticamente o App no Webhook da conta WABA do cliente."""
    wid = (waba_id or "").strip()
    if not wid:
        return {"success": False, "error": "WABA ID ausente."}
    ver = (api_version or "v21.0").strip()
    url = f"https://graph.facebook.com/{ver}/{wid}/subscribed_apps"
    return _graph_request("POST", url, access_token, {})


def discover_waba_assets(
    app_id: str,
    app_secret: str,
    access_token: str,
    api_version: str = "v21.0",
) -> Dict[str, str]:
    """Descobre automaticamente WABA ID e Phone Number ID via debug_token caso não venham do postMessage."""
    ver = (api_version or "v21.0").strip()
    waba_id = ""
    phone_id = ""
    try:
        app_token = f"{app_id.strip()}|{app_secret.strip()}"
        from urllib.parse import quote
        dbg_url = f"https://graph.facebook.com/{ver}/debug_token?input_token={quote(access_token)}&access_token={quote(app_token)}"
        with urllib.request.urlopen(dbg_url, timeout=15) as resp:
            dbg = json.loads(resp.read().decode("utf-8")).get("data", {})
        for g in dbg.get("granular_scopes", []):
            if g.get("scope") in ("whatsapp_business_management", "whatsapp_business_messaging") and g.get("target_ids"):
                waba_id = str(g["target_ids"][0])
                break
        if waba_id:
            ph_res = _graph_request("GET", f"https://graph.facebook.com/{ver}/{waba_id}/phone_numbers?fields=id,display_phone_number,verified_name", access_token)
            phones = (ph_res.get("data") or {}).get("data") or []
            if phones:
                phone_id = str(phones[0].get("id") or "")
    except Exception:
        pass
    return {"waba_id": waba_id, "phone_number_id": phone_id}


def list_templates(waba_id: str, access_token: str, api_version: str = "v21.0") -> Dict[str, Any]:
    """Lista os templates aprovados na conta WABA da Meta."""
    wid = (waba_id or "").strip()
    if not wid:
        return {"success": False, "error": "Informe o WABA ID (WhatsApp Business Account ID).", "templates": []}
    ver = (api_version or "v21.0").strip()
    url = f"https://graph.facebook.com/{ver}/{wid}/message_templates?fields=name,status,category,language,components&limit=50"
    res = _graph_request("GET", url, access_token)
    if not res.get("success"):
        return {"success": False, "error": res.get("error"), "templates": []}
    items = res.get("data", {}).get("data", [])
    return {"success": True, "templates": items}


def send_text_message(
    phone_number_id: str,
    access_token: str,
    to_phone: str,
    text: str,
    api_version: str = "v21.0",
) -> Dict[str, Any]:
    """Envia mensagem de texto livre (janela de 24h aberta pelo cliente)."""
    pid = (phone_number_id or "").strip()
    to_clean = _normalize_phone(to_phone)
    if not pid or not to_clean:
        return {"success": False, "error": "Phone Number ID ou telefone de destino inválido."}
    ver = (api_version or "v21.0").strip()
    url = f"https://graph.facebook.com/{ver}/{pid}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_clean,
        "type": "text",
        "text": {"preview_url": True, "body": text},
    }
    res = _graph_request("POST", url, access_token, payload)
    if not res.get("success"):
        return res
    msgs = res.get("data", {}).get("messages", [])
    msg_id = msgs[0].get("id") if msgs else ""
    return {"success": True, "message_id": msg_id, "to": to_clean}


def send_template_message(
    phone_number_id: str,
    access_token: str,
    to_phone: str,
    template_name: str,
    language_code: str = "pt_BR",
    body_params: Optional[List[str]] = None,
    api_version: str = "v21.0",
) -> Dict[str, Any]:
    """Envia mensagem usando um Template aprovado na Meta (para iniciar conversa)."""
    pid = (phone_number_id or "").strip()
    to_clean = _normalize_phone(to_phone)
    tname = (template_name or "").strip()
    if not pid or not to_clean or not tname:
        return {"success": False, "error": "Phone Number ID, destino ou nome do template ausente."}
    ver = (api_version or "v21.0").strip()
    url = f"https://graph.facebook.com/{ver}/{pid}/messages"
    template_obj: Dict[str, Any] = {
        "name": tname,
        "language": {"code": (language_code or "pt_BR").strip()},
    }
    if body_params:
        template_obj["components"] = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in body_params],
            }
        ]
    payload = {
        "messaging_product": "whatsapp",
        "to": to_clean,
        "type": "template",
        "template": template_obj,
    }
    res = _graph_request("POST", url, access_token, payload)
    if not res.get("success"):
        return res
    msgs = res.get("data", {}).get("messages", [])
    msg_id = msgs[0].get("id") if msgs else ""
    return {"success": True, "message_id": msg_id, "to": to_clean}


def process_webhook_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Processa eventos recebidos no Webhook da Meta Cloud API:
    - Mensagens recebidas de leads -> registra em wa_messages e move lead para 'respondeu'
    - Status de entrega (sent, delivered, read, failed) -> atualiza status em wa_messages
    """
    events_processed: List[Dict[str, Any]] = []
    entries = payload.get("entry") or []
    now = datetime.now().isoformat()

    conn = get_connection()
    cur = conn.cursor()

    try:
        for entry in entries:
            for change in entry.get("changes") or []:
                value = change.get("value") or {}
                metadata = value.get("metadata") or {}
                phone_number_id = str(metadata.get("phone_number_id") or "")
                owner_cfg = find_user_by_phone_number_id(phone_number_id)
                user_id = owner_cfg["user_id"] if owner_cfg else 1

                # 1. Mensagens recebidas (respostas dos leads)
                for msg in value.get("messages") or []:
                    from_phone = _normalize_phone(msg.get("from", ""))
                    if not from_phone or len(from_phone) < 8:
                        continue
                    tail = from_phone[-8:]
                    msg_type = msg.get("type", "text")
                    text_body = ""
                    if msg_type == "text":
                        text_body = (msg.get("text") or {}).get("body", "")
                    elif msg_type == "button":
                        text_body = (msg.get("button") or {}).get("text", "")
                    elif msg_type == "interactive":
                        inter = msg.get("interactive") or {}
                        text_body = (inter.get("button_reply") or inter.get("list_reply") or {}).get("title", "")
                    else:
                        text_body = f"[{msg_type}]"

                    cur.execute(
                        "SELECT id, name, crm_status FROM leads WHERE user_id = ? AND (clean_phone = ? OR clean_phone LIKE ?) LIMIT 1",
                        (user_id, from_phone, f"%{tail}"),
                    )
                    lead_row = cur.fetchone()
                    lead_id = lead_row["id"] if lead_row else None

                    cur.execute(
                        """
                        INSERT INTO wa_messages (user_id, lead_id, phone, direction, kind, text, status, external_id, created_at)
                        VALUES (?, ?, ?, 'in', 'official_reply', ?, 'received', ?, ?)
                        """,
                        (user_id, lead_id, from_phone, text_body, msg.get("id", ""), now),
                    )

                    if lead_id:
                        new_status = lead_row["crm_status"]
                        if new_status in ("novo", "contatado"):
                            new_status = "respondeu"
                        cur.execute(
                            """
                            UPDATE leads SET had_reply = 1, crm_status = ?, whatsapp_status = 'respondeu', updated_at = ?
                            WHERE id = ? AND user_id = ?
                            """,
                            (new_status, now, lead_id, user_id),
                        )

                    events_processed.append({
                        "type": "incoming_message",
                        "user_id": user_id,
                        "lead_id": lead_id,
                        "phone": from_phone,
                        "text": text_body,
                    })

                # 2. Status de mensagens enviadas (sent, delivered, read, failed)
                for st in value.get("statuses") or []:
                    ext_id = st.get("id", "")
                    status_val = st.get("status", "")
                    if ext_id and status_val:
                        cur.execute(
                            "UPDATE wa_messages SET status = ? WHERE external_id = ? AND user_id = ?",
                            (status_val, ext_id, user_id),
                        )
                        events_processed.append({
                            "type": "status_update",
                            "user_id": user_id,
                            "external_id": ext_id,
                            "status": status_val,
                        })

        conn.commit()
    finally:
        conn.close()

    return events_processed

