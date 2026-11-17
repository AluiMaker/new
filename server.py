import os
import sys
import time
import json
import queue
import shutil
import secrets
import threading
from functools import wraps
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, render_template, Response, send_file, session, redirect, url_for
import io
from curl_cffi import requests as cffi_requests

from database import (
    DB_PATH, upsert_lead, get_leads, update_lead, delete_lead,
    get_stats, record_search, get_search_history,
    get_pitch_templates, save_pitch_template, delete_pitch_template, reset_user_templates,
    init_db, deduplicate_database, batch_verify_whatsapp, is_phone_already_contacted,
    get_connection, create_user, authenticate_user, get_user_by_id, find_user_by_email,
    list_users, update_user, get_wa_user_config, save_wa_user_config,
    get_user_access_status, extend_user_subscription, count_recent_signups_by_ip,
    cleanup_expired_trials
)
from scraper_engine import GoogleMapsScraper, DEFAULT_SEGMENTS, SWEEP_ALL_TERMS
from exporter import export_to_csv_bytes, export_to_json_bytes
import wa_automation as wa
import wa_official

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
if os.environ.get("PORT") or os.environ.get("FORCE_HTTPS_COOKIE") == "1":
    app.config["SESSION_COOKIE_SECURE"] = True

# Rate limiter em memória para proteção contra força bruta no Login
_login_attempts: Dict[str, list] = {}
_login_lock = threading.Lock()

# Semáforo global para evitar sobrecarga de RAM do Chromium com múltiplos usuários
_search_semaphore = threading.Semaphore(int(os.environ.get("MAX_CONCURRENT_SEARCHES", "1")))


def _client_ip() -> str:
    fwd = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return fwd or request.remote_addr or "unknown"


def _is_login_blocked(ip: str) -> bool:
    now = time.time()
    with _login_lock:
        recent = [t for t in _login_attempts.get(ip, []) if now - t < 600]
        _login_attempts[ip] = recent
        return len(recent) >= 10


def _record_login_failure(ip: str):
    now = time.time()
    with _login_lock:
        arr = [t for t in _login_attempts.get(ip, []) if now - t < 600]
        arr.append(now)
        _login_attempts[ip] = arr


def _clear_login_failures(ip: str):
    with _login_lock:
        _login_attempts.pop(ip, None)


@app.after_request
def _add_security_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return resp

def _load_secret_key() -> str:
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key
    key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".secret_key")
    if os.path.exists(key_file):
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                val = f.read().strip()
                if val:
                    return val
        except Exception:
            pass
    new_key = secrets.token_hex(32)
    try:
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(new_key)
    except Exception:
        pass
    return new_key

app.secret_key = _load_secret_key()

# Estado de busca e filas SSE isolados por usuário (multi-tenant)
_user_search_states: Dict[int, Dict[str, Any]] = {}
_user_event_queues: Dict[int, queue.Queue] = {}
_state_lock = threading.Lock()


def get_user_search_state(user_id: int) -> Dict[str, Any]:
    with _state_lock:
        if user_id not in _user_search_states:
            _user_search_states[user_id] = {
                "is_running": False,
                "current_query": "",
                "total_found": 0,
                "no_website_count": 0,
                "last_log": "Pronto para buscar.",
                "scraper_instance": None,
            }
        return _user_search_states[user_id]


def get_user_event_queue(user_id: int) -> queue.Queue:
    with _state_lock:
        if user_id not in _user_event_queues:
            _user_event_queues[user_id] = queue.Queue()
        return _user_event_queues[user_id]


def broadcast_event(event_type: str, data: Any, user_id: int = 1):
    msg = f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
    try:
        get_user_event_queue(user_id).put_nowait(msg)
    except Exception:
        pass


def current_user_id() -> Optional[int]:
    uid = session.get("user_id")
    return int(uid) if uid is not None else None


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        uid = current_user_id()
        if not uid:
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "Sessão expirada. Faça login novamente.", "auth_required": True}), 401
            return redirect(url_for("login_page"))
        user = get_user_by_id(uid)
        if not user or not user.get("is_active"):
            session.clear()
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "Conta inativa ou não encontrada.", "auth_required": True}), 401
            return redirect(url_for("login_page"))
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        user = get_user_by_id(current_user_id())
        if not user or user.get("role") != "admin":
            return jsonify({"success": False, "error": "Acesso restrito a administradores."}), 403
        return fn(*args, **kwargs)
    return wrapper


def subscription_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        acc = get_user_access_status(current_user_id())
        if not acc.get("active"):
            return jsonify({
                "success": False,
                "subscription_expired": True,
                "error": "Seu período de teste ou assinatura expirou. Renove para continuar."
            }), 402
        return fn(*args, **kwargs)
    return wrapper


def run_scraper_thread(
    user_id: int, query: str, niche: str, street: str, neighborhood: str, city: str,
    lat: Optional[float], lon: Optional[float], target_limit: int, visible_browser: bool,
    mode: str = "single", segments_to_run: Optional[list] = None, auto_dispatch: bool = False,
    place_type: str = "street", zoom: Optional[int] = None
):
    st = get_user_search_state(user_id)
    st["is_running"] = True
    st["current_query"] = query
    st["total_found"] = 0
    st["no_website_count"] = 0

    loc_summary = ", ".join([p for p in (street, neighborhood, city) if p.strip()]) or query
    broadcast_event("search_started", {
        "query": query,
        "niche": niche,
        "location": loc_summary,
        "place_type": place_type,
        "target_limit": target_limit
    }, user_id=user_id)

    def log_cb(msg: str):
        st["last_log"] = msg
        broadcast_event("log", {"message": msg, "time": time.strftime("%H:%M:%S")}, user_id=user_id)

    def progress_cb(prog: Dict[str, Any]):
        st["total_found"] = prog["total_extracted"]
        st["no_website_count"] = prog["no_website_count"]
        broadcast_event("progress", prog, user_id=user_id)

    def lead_cb(lead: Dict[str, Any]):
        if lat is not None and not lead.get("lat"):
            lead["lat"] = lat
        if lon is not None and not lead.get("lon"):
            lead["lon"] = lon
        lead_id, is_new = upsert_lead(lead, user_id=user_id)
        if not lead_id:
            return
        lead["id"] = lead_id
        lead["is_new"] = is_new
        broadcast_event("lead_found", lead, user_id=user_id)
        if lead.get("clean_phone"):
            broadcast_event("queue_updated", wa.get_queue_summary(), user_id=user_id)

    if not _search_semaphore.acquire(timeout=120):
        log_cb("Servidor ocupado com outra busca no momento. Tente novamente em instantes.")
        broadcast_event("search_error", {"error": "Servidor ocupado com outra busca. Tente novamente em instantes."}, user_id=user_id)
        st["is_running"] = False
        broadcast_event("search_finished", {}, user_id=user_id)
        return

    scraper = GoogleMapsScraper(headless=not visible_browser, log_callback=log_cb)
    st["scraper_instance"] = scraper

    try:
        def seg_cb(curr_idx, total_idx, seg_name):
            broadcast_event("segment_change", {
                "current": curr_idx,
                "total": total_idx,
                "segment": seg_name
            }, user_id=user_id)

        if mode == "all":
            sweep_list = segments_to_run if segments_to_run else SWEEP_ALL_TERMS
            broadcast_event("log", {"message": f"Iniciando Varredura Completa em {loc_summary} (Meta: {target_limit} empresas)...", "time": time.strftime("%H:%M:%S")}, user_id=user_id)
            results = scraper.scrape_multi_segments(
                segments=sweep_list,
                street=street,
                neighborhood=neighborhood,
                city=city,
                lat=lat,
                lon=lon,
                target_per_segment=min(35, max(18, target_limit // 2)),
                total_target_limit=target_limit,
                place_type=place_type,
                zoom=zoom,
                on_lead_found=lead_cb,
                progress_callback=progress_cb,
                on_segment_change=seg_cb
            )
        elif mode == "multi" and segments_to_run:
            broadcast_event("log", {"message": f"Iniciando busca em {len(segments_to_run)} segmentos ({place_type.upper()})...", "time": time.strftime("%H:%M:%S")}, user_id=user_id)
            results = scraper.scrape_multi_segments(
                segments=segments_to_run,
                street=street,
                neighborhood=neighborhood,
                city=city,
                lat=lat,
                lon=lon,
                target_per_segment=target_limit,
                total_target_limit=None,
                place_type=place_type,
                zoom=zoom,
                on_lead_found=lead_cb,
                progress_callback=progress_cb,
                on_segment_change=seg_cb
            )
        else:
            results = scraper.scrape_leads(
                query=query,
                niche=niche,
                street=street,
                neighborhood=neighborhood,
                city=city,
                lat=lat,
                lon=lon,
                target_limit=target_limit,
                place_type=place_type,
                zoom=zoom,
                on_lead_found=lead_cb,
                progress_callback=progress_cb
            )

        no_web = sum(1 for x in results if x.get("website_type") in ("none", "social", "directory"))
        record_search(query, niche or ("Todos os Negócios" if mode == "all" else "Multi-Segmentos"), f"{street} {neighborhood} {city}".strip(), len(results), no_web, user_id=user_id)
        broadcast_event("search_completed", {
            "total": len(results),
            "no_website": no_web,
            "message": f"Busca finalizada! {len(results)} empresas com telefone válido encontradas ({no_web} sem site próprio)."
        }, user_id=user_id)
        broadcast_event("queue_updated", wa.get_queue_summary(), user_id=user_id)
    except Exception as e:
        log_cb(f"Erro na busca: {str(e)}")
        broadcast_event("search_error", {"error": str(e)}, user_id=user_id)
    finally:
        try:
            _search_semaphore.release()
        except Exception:
            pass
        st["is_running"] = False
        st["scraper_instance"] = None
        broadcast_event("search_finished", {}, user_id=user_id)

BRAZIL_UF_MAP = {
    "acre": "AC", "alagoas": "AL", "amapá": "AP", "amapa": "AP", "amazonas": "AM", "bahia": "BA",
    "ceará": "CE", "ceara": "CE", "distrito federal": "DF", "espírito santo": "ES", "espirito santo": "ES",
    "goiás": "GO", "goias": "GO", "maranhão": "MA", "maranhao": "MA", "mato grosso": "MT",
    "mato grosso do sul": "MS", "minas gerais": "MG", "pará": "PA", "para": "PA", "paraíba": "PB",
    "paraiba": "PB", "paraná": "PR", "parana": "PR", "pernambuco": "PE", "piauí": "PI", "piaui": "PI",
    "rio de janeiro": "RJ", "rio grande do norte": "RN", "rio grande do sul": "RS",
    "rondônia": "RO", "rondonia": "RO", "roraima": "RR", "santa catarina": "SC",
    "são paulo": "SP", "sao paulo": "SP", "sergipe": "SE", "tocantins": "TO"
}

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/")
@login_required
def index():
    uid = current_user_id()
    user = get_user_by_id(uid)
    access_status = get_user_access_status(uid)
    checkout_url = os.environ.get("CHECKOUT_URL", "")
    return render_template("index.html", current_user=user, access_status=access_status, checkout_url=checkout_url)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        if current_user_id() and get_user_by_id(current_user_id()):
            return redirect(url_for("index"))
        return render_template("auth.html", mode="login")
    ip = _client_ip()
    if _is_login_blocked(ip):
        msg = "Muitas tentativas de login. Aguarde 10 minutos."
        if request.is_json:
            return jsonify({"success": False, "error": msg}), 429
        return render_template("auth.html", mode="login", error=msg)
    data = request.get_json(silent=True) or request.form
    email = data.get("email", "")
    password = data.get("password", "")
    user = authenticate_user(email, password)
    if not user:
        _record_login_failure(ip)
        if request.is_json:
            return jsonify({"success": False, "error": "E-mail ou senha inválidos (ou conta desativada)."}), 401
        return render_template("auth.html", mode="login", error="E-mail ou senha inválidos.")
    _clear_login_failures(ip)
    session["user_id"] = user["id"]
    session.permanent = True
    if request.is_json:
        return jsonify({"success": True, "user": user})
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        if current_user_id() and get_user_by_id(current_user_id()):
            return redirect(url_for("index"))
        return render_template("auth.html", mode="register")

    if os.environ.get("ALLOW_PUBLIC_SIGNUP", "1") != "1":
        msg = "Cadastro público fechado. Adquira um plano ou solicite acesso ao administrador."
        if request.is_json:
            return jsonify({"success": False, "error": msg}), 403
        return render_template("auth.html", mode="register", error=msg)

    ip = _client_ip()
    if count_recent_signups_by_ip(ip, hours=24) >= 2:
        msg = "Limite de contas de teste atingido para este endereço. Tente novamente amanhã."
        if request.is_json:
            return jsonify({"success": False, "error": msg}), 429
        return render_template("auth.html", mode="register", error=msg)

    data = request.get_json(silent=True) or request.form
    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")
    company_name = data.get("company_name", "")
    # Novos cadastros públicos entram automaticamente no Teste Grátis: 3 dias e até 25 leads
    uid, err = create_user(name, email, password, company_name=company_name, role="user", plan="trial", days=3, max_leads=25, signup_ip=ip)
    if err or not uid:
        if request.is_json:
            return jsonify({"success": False, "error": err or "Erro ao criar conta."}), 400
        return render_template("auth.html", mode="register", error=err)
    session["user_id"] = uid
    session.permanent = True
    user = get_user_by_id(uid)
    if request.is_json:
        return jsonify({"success": True, "user": user})
    return redirect(url_for("index"))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    if request.is_json or request.method == "POST":
        return jsonify({"success": True})
    return redirect(url_for("login_page"))


@app.route("/api/me", methods=["GET", "PUT"])
@login_required
def api_me():
    uid = current_user_id()
    if request.method == "PUT":
        data = request.get_json(silent=True) or {}
        allowed_updates = {}
        if "name" in data:
            allowed_updates["name"] = data["name"]
        if "company_name" in data:
            allowed_updates["company_name"] = data["company_name"]
        if data.get("password"):
            if len(str(data["password"])) < 6:
                return jsonify({"success": False, "error": "A nova senha deve ter pelo menos 6 caracteres."}), 400
            allowed_updates["password"] = data["password"]
        update_user(uid, allowed_updates)
    return jsonify({"success": True, "user": get_user_by_id(uid), "access": get_user_access_status(uid)})


@app.route("/api/admin/users", methods=["GET", "POST"])
@admin_required
def api_admin_users():
    if request.method == "GET":
        return jsonify({"success": True, "users": list_users()})
    data = request.get_json(silent=True) or {}
    uid, err = create_user(
        data.get("name", ""),
        data.get("email", ""),
        data.get("password", ""),
        company_name=data.get("company_name", ""),
        role=data.get("role", "user"),
        plan=data.get("plan", "pro"),
        days=int(data.get("days")) if data.get("days") else None,
    )
    if err:
        return jsonify({"success": False, "error": err}), 400
    return jsonify({"success": True, "user": get_user_by_id(uid)})


@app.route("/api/admin/users/<int:target_id>", methods=["PUT"])
@admin_required
def api_admin_update_user(target_id):
    data = request.get_json(silent=True) or {}
    ok = update_user(target_id, data)
    return jsonify({"success": ok, "user": get_user_by_id(target_id)})


@app.route("/api/admin/users/<int:target_id>/renew", methods=["POST"])
@admin_required
def api_admin_renew_user(target_id):
    data = request.get_json(silent=True) or {}
    days = int(data.get("days", 30))
    plan = data.get("plan")
    updated = extend_user_subscription(target_id, days=days, plan=plan)
    if not updated:
        return jsonify({"success": False, "error": "Usuário não encontrado."}), 404
    return jsonify({"success": True, "user": updated})


@app.route("/api/admin/cleanup-trials", methods=["POST"])
@admin_required
def api_admin_cleanup_trials():
    data = request.get_json(silent=True) or {}
    grace_days = int(data.get("grace_days", 15))
    removed = cleanup_expired_trials(grace_days=grace_days)
    return jsonify({"success": True, "removed": removed})


@app.route("/api/billing/webhook", methods=["POST"])
@app.route("/api/billing/webhook/<gateway>", methods=["POST"])
def api_billing_webhook(gateway="generic"):
    """
    Webhook universal para liberação/bloqueio automático de assinantes:
    Compatível com Kiwify, Cakto, Asaas, Mercado Pago ou integração própria.
    Protegido por BILLING_WEBHOOK_SECRET (?token=... ou header X-Webhook-Token).
    """
    expected = os.environ.get("BILLING_WEBHOOK_SECRET", "").strip()
    if expected:
        got = (
            request.args.get("token")
            or request.headers.get("X-Webhook-Token")
            or request.headers.get("asaas-access-token")
            or ""
        ).strip()
        if not secrets.compare_digest(got, expected):
            return jsonify({"success": False, "error": "Invalid webhook token"}), 403

    payload = request.get_json(silent=True) or {}
    gw = (gateway or "generic").lower()

    # Extração normalizada de evento, email, nome e plano
    event_name = str(
        payload.get("webhook_event_type")
        or payload.get("event")
        or payload.get("action")
        or payload.get("type")
        or ""
    ).lower()

    customer = payload.get("Customer") or payload.get("customer") or payload.get("payer") or {}
    email = str(
        customer.get("email")
        or payload.get("email")
        or (payload.get("payment") or {}).get("customerEmail")
        or ""
    ).strip().lower()
    name = str(customer.get("full_name") or customer.get("name") or payload.get("name") or (email.split("@")[0] if email else "Assinante")).strip()
    plan = str(payload.get("plan") or "pro").lower()
    days = int(payload.get("days") or 30)

    if not email:
        return jsonify({"success": True, "ignored": True, "reason": "no_email"}), 200

    approved_events = ("paid", "approved", "order_approved", "subscription_renewed", "subscription_authorized", "payment_confirmed", "payment_received", "active")
    cancel_events = ("refunded", "chargedback", "canceled", "cancelled", "subscription_canceled", "subscription_late", "payment_overdue", "expired")

    user = find_user_by_email(email)

    if any(k in event_name for k in approved_events) or payload.get("status") in ("paid", "approved", "CONFIRMED", "RECEIVED"):
        if not user:
            temp_pass = secrets.token_urlsafe(10)
            uid, err = create_user(name, email, temp_pass, role="user", plan=plan, days=days)
            return jsonify({"success": bool(uid), "action": "created_and_activated", "user_id": uid})
        updated = extend_user_subscription(user["id"], days=days, plan=plan)
        return jsonify({"success": True, "action": "renewed", "user_id": user["id"], "expires_at": (updated or {}).get("plan_expires_at")})

    if any(k in event_name for k in cancel_events):
        if user:
            update_user(user["id"], {"subscription_status": "expired"})
            return jsonify({"success": True, "action": "expired", "user_id": user["id"]})

    return jsonify({"success": True, "ignored": True, "event": event_name}), 200

@app.route("/api/address/suggest")
def api_address_suggest():
    """
    Autocomplete inteligente no estilo Waze/Uber para Cidades, Bairros e Ruas de todo o Brasil.
    Diferencia e classifica categoricamente se o local é Cidade (Município), Bairro ou Rua/Avenida.
    """
    q = (request.args.get("q") or "").strip()
    if len(q) < 3:
        return jsonify([])
        
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={cffi_requests.utils.quote(q)}&format=json&addressdetails=1&countrycodes=br&limit=8"
        headers = {"User-Agent": "MapaLeadsPro/1.0 (contact@mapaleads.local)"}
        resp = cffi_requests.get(url, headers=headers, impersonate="chrome", timeout=5)
        if resp.status_code != 200:
            return jsonify([])
            
        items = resp.json()
        suggestions = []
        seen = set()

        for item in items:
            addr = item.get("address", {})
            addresstype = (item.get("addresstype") or item.get("type") or "").lower()
            item_class = (item.get("class") or "").lower()

            road = addr.get("road") or addr.get("pedestrian") or addr.get("highway") or addr.get("street")
            suburb = addr.get("suburb") or addr.get("neighbourhood") or addr.get("city_district") or addr.get("quarter") or addr.get("subdivision") or ""
            city = addr.get("city") or addr.get("town") or addr.get("municipality") or addr.get("village") or addr.get("county") or ""
            state = addr.get("state") or ""
            
            # Formatar UF
            state_code = ""
            iso = addr.get("ISO3166-2-lvl4", "")
            if iso.startswith("BR-"):
                state_code = iso[3:]
            if not state_code and state:
                state_code = BRAZIL_UF_MAP.get(state.lower().strip(), state)

            # Classificação explícita: RUA vs BAIRRO vs CIDADE
            is_street = bool(road) or item_class == "highway" or addresstype in (
                "road", "street", "highway", "primary", "secondary", "residential",
                "tertiary", "pedestrian", "living_street", "service", "trunk", "track"
            )
            is_bairro = not is_street and (bool(suburb) or addresstype in (
                "suburb", "neighbourhood", "city_district", "quarter", "borough", "subdivision"
            ))

            lat = float(item["lat"]) if "lat" in item else None
            lon = float(item["lon"]) if "lon" in item else None

            if is_street:
                street_val = road or item.get("name") or ""
                city_val = f"{city}, {state_code}".strip(", ") if city else state_code
                city_display = f"{city} - {state_code}" if (city and state_code) else (city or state_code or "Brasil")

                # 1. Sugestão Primária: Rua Toda (Sem prender a 1 bairro; pega a via inteira de uma vez)
                whole_key = f"street_whole|{street_val.lower()}|{city.lower()}"
                if whole_key not in seen:
                    seen.add(whole_key)
                    suggestions.append({
                        "place_type": "street",
                        "type_label": "Rua Toda",
                        "type_icon": "fa-road",
                        "type_color": "blue",
                        "recommended_zoom": 14,
                        "street": street_val,
                        "neighborhood": "",  # Vazio para varrer a rua toda na cidade de uma vez
                        "city": city_val,
                        "display_title": f"{street_val} (Rua Toda)",
                        "display_subtitle": f"Toda a extensão em {city_display}",
                        "full_label": f"{street_val} (Rua Toda), {city_display}",
                        "lat": lat,
                        "lon": lon
                    })

                # 2. Sugestão Secundária: Trecho no Bairro específico (se retornado pelo OSM)
                if suburb:
                    bairro_key = f"street_suburb|{street_val.lower()}|{suburb.lower()}|{city.lower()}"
                    if bairro_key not in seen:
                        seen.add(bairro_key)
                        suggestions.append({
                            "place_type": "street",
                            "type_label": "Trecho no Bairro",
                            "type_icon": "fa-location-dot",
                            "type_color": "cyan",
                            "recommended_zoom": 16,
                            "street": street_val,
                            "neighborhood": suburb,
                            "city": city_val,
                            "display_title": street_val,
                            "display_subtitle": f"{suburb}, {city_display}",
                            "full_label": f"{street_val}, {suburb}, {city_display}",
                            "lat": lat,
                            "lon": lon
                        })
                continue

            elif is_bairro:
                place_type = "neighborhood"
                type_label = "Bairro"
                type_icon = "fa-tree-city"
                type_color = "emerald"
                recommended_zoom = 14
                street_val = ""
                neighborhood_val = suburb or item.get("name") or ""
                city_val = f"{city}, {state_code}".strip(", ") if city else state_code
                display_title = neighborhood_val
                
                sub_parts = []
                if city:
                    sub_parts.append(f"{city} - {state_code}" if state_code else city)
                elif state_code:
                    sub_parts.append(state_code)
                display_sub = f"Bairro em {', '.join(sub_parts)}" if sub_parts else "Bairro"
                full_label = f"{display_title} ({', '.join(sub_parts)})" if sub_parts else display_title

            else:
                place_type = "city"
                type_label = "Cidade"
                type_icon = "fa-city"
                type_color = "purple"
                recommended_zoom = 12
                street_val = ""
                neighborhood_val = ""
                city_name = city or item.get("name") or ""
                city_val = f"{city_name}, {state_code}".strip(", ") if state_code else city_name
                display_title = city_name
                display_sub = f"Município em {state_code}" if state_code else "Município · Brasil"
                full_label = f"{display_title} - {state_code}" if state_code else display_title

            key = f"{place_type}|{display_title}|{display_sub}".lower()
            if key in seen:
                continue
            seen.add(key)
            
            lat = float(item["lat"]) if "lat" in item else None
            lon = float(item["lon"]) if "lon" in item else None
            
            suggestions.append({
                "place_type": place_type,
                "type_label": type_label,
                "type_icon": type_icon,
                "type_color": type_color,
                "recommended_zoom": recommended_zoom,
                "street": street_val,
                "neighborhood": neighborhood_val,
                "city": city_val,
                "display_title": display_title,
                "display_subtitle": display_sub,
                "full_label": full_label,
                "lat": lat,
                "lon": lon
            })
            
        return jsonify(suggestions)
    except Exception as e:
        return jsonify([])

@app.route("/api/address/reverse")
def api_address_reverse():
    """
    Geocodificação reversa inteligente para quando o usuário clica ou coloca um PIN no mapa.
    Detecta a rua/avenida exata, bairro e município para permitir varrer a via inteira negócio por negócio.
    """
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if not lat or not lon:
        return jsonify({"success": False, "error": "Parâmetros lat e lon são obrigatórios."}), 400

    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1&zoom=18"
        headers = {"User-Agent": "MapaLeadsPro/1.0 (contact@mapaleads.local)"}
        resp = cffi_requests.get(url, headers=headers, impersonate="chrome", timeout=5)
        if resp.status_code != 200:
            return jsonify({"success": False, "error": "Não foi possível obter dados do local."})

        data = resp.json()
        addr = data.get("address", {})

        road = addr.get("road") or addr.get("pedestrian") or addr.get("highway") or addr.get("street") or ""
        suburb = addr.get("suburb") or addr.get("neighbourhood") or addr.get("city_district") or addr.get("quarter") or addr.get("subdivision") or ""
        city = addr.get("city") or addr.get("town") or addr.get("municipality") or addr.get("village") or addr.get("county") or ""
        state = addr.get("state") or ""

        # Formatar UF
        state_code = ""
        iso = addr.get("ISO3166-2-lvl4", "")
        if iso.startswith("BR-"):
            state_code = iso[3:]
        if not state_code and state:
            state_code = BRAZIL_UF_MAP.get(state.lower().strip(), state)

        city_display = f"{city} - {state_code}" if (city and state_code) else (city or state_code or "Brasil")
        street_display = road if road else (data.get("name") or "Via sem denominação")
        is_street = bool(road) or any(k in (data.get("addresstype") or "").lower() for k in ["road", "street", "highway", "residential", "living_street", "primary", "secondary", "tertiary"])

        return jsonify({
            "success": True,
            "is_street": is_street,
            "street": street_display,
            "neighborhood": suburb,
            "city": f"{city}, {state_code}".strip(", ") if city else state_code,
            "city_display": city_display,
            "display_title": f"{street_display} (Rua Toda)" if is_street else street_display,
            "display_subtitle": f"Toda a extensão em {city_display}" if is_street else (f"{suburb}, {city_display}" if suburb else city_display),
            "full_label": f"{street_display} (Rua Toda), {city_display}" if is_street else f"{street_display}, {city_display}",
            "lat": float(lat),
            "lon": float(lon),
            "recommended_zoom": 14
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/stats")
@login_required
def api_stats():
    return jsonify(get_stats(user_id=current_user_id()))


@app.route("/api/leads")
@login_required
def api_leads():
    uid = current_user_id()
    website_type = request.args.get("website_type")
    crm_status = request.args.get("crm_status")
    opportunity = request.args.get("opportunity")
    tag = request.args.get("tag")
    has_contact = request.args.get("has_contact")
    has_reply = request.args.get("has_reply")
    has_sale = request.args.get("has_sale")
    has_phone = request.args.get("has_phone") == "1"
    search = request.args.get("search")
    limit = int(request.args.get("limit", 1000))
    offset = int(request.args.get("offset", 0))

    leads = get_leads(
        user_id=uid,
        website_type=website_type,
        crm_status=crm_status,
        opportunity=opportunity,
        tag=tag,
        has_contact=has_contact,
        has_reply=has_reply,
        has_sale=has_sale,
        has_phone=has_phone,
        search=search,
        limit=limit,
        offset=offset
    )
    return jsonify(leads)


@app.route("/api/leads/<int:lead_id>", methods=["PUT"])
@login_required
def api_update_lead(lead_id):
    uid = current_user_id()
    data = dict(request.json or {})
    now = time.strftime("%d/%m/%Y %H:%M")
    status = data.get("crm_status")
    if status == "contatado":
        data.setdefault("had_contact", 1)
        data.setdefault("contact_date", now)
        data.setdefault("whatsapp_status", "enviado")
    elif status == "respondeu":
        data.setdefault("had_contact", 1)
        data.setdefault("had_reply", 1)
    elif status == "fechado":
        data.setdefault("had_contact", 1)
        data.setdefault("had_sale", 1)
    ok = update_lead(lead_id, data, user_id=uid)
    broadcast_event("lead_updated", {"id": lead_id, "crm_status": status}, user_id=uid)
    broadcast_event("queue_updated", wa.get_queue_summary(), user_id=uid)
    return jsonify({"success": ok, "contact_date": now})


@app.route("/api/leads/<int:lead_id>/toggle-contact", methods=["POST"])
@login_required
def api_toggle_contact(lead_id):
    uid = current_user_id()
    data = request.get_json(silent=True) or {}
    now = time.strftime("%d/%m/%Y %H:%M")
    target_status = data.get("crm_status", "contatado")
    update_data = {
        "had_contact": 1,
        "contact_date": now,
        "crm_status": target_status,
        "whatsapp_status": "followup_enviado" if data.get("kind") == "followup" else "enviado"
    }
    if target_status == "respondeu" or data.get("had_reply"):
        update_data["had_reply"] = 1

    ok = update_lead(lead_id, update_data, user_id=uid)

    text = (data.get("text") or "").strip()
    phone = (data.get("phone") or "").strip()
    if text:
        wa.log_message(lead_id, phone, "out", data.get("kind", "pitch"), text)

    broadcast_event("lead_updated", {"id": lead_id, "crm_status": target_status, "contact_date": now}, user_id=uid)
    broadcast_event("queue_updated", wa.get_queue_summary(), user_id=uid)
    return jsonify({"success": ok, "contact_date": now, "crm_status": target_status})


@app.route("/api/leads/<int:lead_id>/record-sale", methods=["POST"])
@login_required
def api_record_sale(lead_id):
    uid = current_user_id()
    data = request.json or {}
    val = float(data.get("sale_value", 0.0))
    update_data = {
        "had_contact": 1,
        "had_sale": 1,
        "sale_value": val,
        "crm_status": "fechado"
    }
    if data.get("product_interest"):
        update_data["product_interest"] = data["product_interest"]
    ok = update_lead(lead_id, update_data, user_id=uid)
    broadcast_event("lead_updated", {"id": lead_id, "crm_status": "fechado"}, user_id=uid)
    return jsonify({"success": ok})


@app.route("/api/leads/<int:lead_id>", methods=["DELETE"])
@login_required
def api_delete_lead(lead_id):
    uid = current_user_id()
    ok = delete_lead(lead_id, user_id=uid)
    broadcast_event("queue_updated", wa.get_queue_summary(), user_id=uid)
    return jsonify({"success": ok})


@app.route("/api/leads/batch-status", methods=["POST"])
@login_required
def api_batch_status():
    uid = current_user_id()
    data = request.json or {}
    ids = data.get("ids", [])
    status = data.get("crm_status", "novo")
    now = time.strftime("%d/%m/%Y %H:%M")
    updated = 0
    for lid in ids:
        fields = {"crm_status": status}
        if status == "contatado":
            fields["had_contact"] = 1
            fields["contact_date"] = now
            fields["whatsapp_status"] = "enviado"
        elif status == "respondeu":
            fields["had_reply"] = 1
        if update_lead(lid, fields, user_id=uid):
            updated += 1
    broadcast_event("queue_updated", wa.get_queue_summary(), user_id=uid)
    return jsonify({"success": True, "updated": updated})


@app.route("/api/segments/presets")
@login_required
def api_segments_presets():
    return jsonify(DEFAULT_SEGMENTS)


@app.route("/api/search/history")
@login_required
def api_search_history():
    return jsonify(get_search_history(user_id=current_user_id(), limit=15))


@app.route("/api/search/start", methods=["POST"])
@subscription_required
def api_search_start():
    uid = current_user_id()
    acc = get_user_access_status(uid)
    if acc.get("leads_limit_reached"):
        return jsonify({
            "success": False,
            "error": f"Você atingiu o limite de {acc.get('max_leads')} leads do seu plano ({acc.get('plan')}). Faça upgrade para continuar."
        }), 402
    st = get_user_search_state(uid)
    if st["is_running"]:
        return jsonify({"success": False, "error": "Já existe uma busca em andamento para a sua conta."}), 400

    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "all")
    segments_raw = data.get("segments") or []
    auto_dispatch = False

    niche = (data.get("niche") or "").strip()
    street = (data.get("street") or "").strip()
    neighborhood = (data.get("neighborhood") or "").strip()
    city = (data.get("city") or "").strip()
    lat = data.get("lat")
    lon = data.get("lon")
    target_limit = int(data.get("target_limit") or (80 if mode == "all" else (20 if mode == "multi" else 40)))
    if acc.get("max_leads", 0) > 0:
        remaining = max(1, acc["max_leads"] - acc.get("leads_count", 0))
        target_limit = min(target_limit, remaining)
    visible_browser = bool(data.get("visible_browser", False))

    if not street and not neighborhood and not city and not niche:
        return jsonify({"success": False, "error": "Informe uma rua, bairro ou cidade para buscar."}), 400

    if mode == "single" and (not niche or niche.lower() in ("todos", "todos os negócios", "qualquer")):
        mode = "all"

    segments_to_run = []
    if mode == "all":
        segments_to_run = list(SWEEP_ALL_TERMS)
    elif mode == "multi":
        if not segments_raw or segments_raw == "todos" or (isinstance(segments_raw, list) and "todos" in segments_raw):
            segments_to_run = list(SWEEP_ALL_TERMS)
        elif isinstance(segments_raw, list):
            preset_dict = {s["id"]: s["name"] for s in DEFAULT_SEGMENTS}
            for s in segments_raw:
                s_clean = str(s).strip()
                if s_clean in preset_dict:
                    segments_to_run.append(preset_dict[s_clean])
                elif s_clean:
                    segments_to_run.append(s_clean)
        if not segments_to_run:
            segments_to_run = list(SWEEP_ALL_TERMS)

    place_type = (data.get("place_type") or ("city" if (city and not street and not neighborhood) else ("neighborhood" if (neighborhood and not street) else "street"))).lower()
    zoom = data.get("zoom")
    if zoom is not None:
        try:
            zoom = int(zoom)
        except Exception:
            zoom = None

    parts = []
    if niche and mode == "single":
        parts.append(niche)
    if street:
        parts.append(street)
    if neighborhood:
        parts.append(neighborhood)
    if city:
        parts.append(city)

    query = " ".join(parts) or (f"Varredura Completa em {street or neighborhood or city or 'Região'}")

    t = threading.Thread(
        target=run_scraper_thread,
        args=(uid, query, niche, street, neighborhood, city, lat, lon, target_limit, visible_browser, mode, segments_to_run, auto_dispatch, place_type, zoom),
        daemon=True
    )
    t.start()

    return jsonify({
        "success": True,
        "query": query,
        "mode": mode,
        "place_type": place_type,
        "segments": segments_to_run,
        "target_limit": target_limit,
        "auto_dispatch": auto_dispatch
    })


@app.route("/api/search/stop", methods=["POST"])
@login_required
def api_search_stop():
    uid = current_user_id()
    st = get_user_search_state(uid)
    if st["scraper_instance"]:
        st["scraper_instance"].request_stop()
        st["is_running"] = False
        broadcast_event("log", {"message": "Busca interrompida pelo usuário.", "time": time.strftime("%H:%M:%S")}, user_id=uid)
        return jsonify({"success": True, "message": "Parada solicitada."})
    return jsonify({"success": False, "error": "Nenhuma busca ativa."})


@app.route("/api/search/status")
@login_required
def api_search_status():
    st = get_user_search_state(current_user_id())
    return jsonify({
        "is_running": st["is_running"],
        "query": st["current_query"],
        "total_found": st["total_found"],
        "no_website_count": st["no_website_count"],
        "last_log": st["last_log"]
    })


@app.route("/api/search/stream")
@login_required
def api_search_stream():
    uid = current_user_id()
    q = get_user_event_queue(uid)
    st = get_user_search_state(uid)

    def event_stream():
        initial_msg = f"event: init\ndata: {json.dumps({'is_running': st['is_running']})}\n\n"
        yield initial_msg

        while True:
            try:
                msg = q.get(timeout=10.0)
                yield msg
            except queue.Empty:
                yield ": keep-alive\n\n"
            except Exception:
                break

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/api/export/csv")
@login_required
def api_export_csv():
    uid = current_user_id()
    website_type = request.args.get("website_type")
    crm_status = request.args.get("crm_status")
    opportunity = request.args.get("opportunity")
    leads = get_leads(user_id=uid, website_type=website_type, crm_status=crm_status, opportunity=opportunity, limit=10000)
    csv_bytes = export_to_csv_bytes(leads)

    filename = f"leads_mapaleads_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(
        io.BytesIO(csv_bytes),
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename
    )


@app.route("/api/pitch-templates")
@login_required
def api_get_templates():
    return jsonify(get_pitch_templates(user_id=current_user_id()))


@app.route("/api/pitch-templates", methods=["POST"])
@login_required
def api_save_template():
    uid = current_user_id()
    data = request.json or {}
    tid = data.get("id") or f"custom_{int(time.time())}"
    title = data.get("title", "Novo Modelo")
    content = data.get("content", "")
    follow_up = data.get("follow_up", "")
    product = data.get("product", "geral")
    meta_template_name = data.get("meta_template_name", "")
    save_pitch_template(tid, title, content, follow_up, product=product, meta_template_name=meta_template_name, user_id=uid)
    return jsonify({"success": True, "id": tid})


@app.route("/api/pitch-templates/<template_id>", methods=["DELETE"])
@login_required
def api_delete_template(template_id):
    ok = delete_pitch_template(template_id, user_id=current_user_id())
    return jsonify({"success": ok})


@app.route("/api/pitch-templates/reset", methods=["POST"])
@login_required
def api_reset_templates():
    reset_user_templates(user_id=current_user_id())
    return jsonify({"success": True, "templates": get_pitch_templates(user_id=current_user_id())})

# ==================== WHATSAPP OFICIAL (META CLOUD API) ====================

@app.route("/api/wa/official/config", methods=["GET", "POST"])
@login_required
def api_wa_official_config():
    uid = current_user_id()
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        # Não sobrescreve token se vier mascarado
        if data.get("meta_access_token", "").startswith("••••"):
            data.pop("meta_access_token", None)
        cfg = save_wa_user_config(uid, data)
        masked = dict(cfg)
        tok = masked.get("meta_access_token") or ""
        masked["has_token"] = bool(tok)
        masked["meta_access_token"] = ("••••" + tok[-6:]) if len(tok) > 6 else ("••••" if tok else "")
        return jsonify({"success": True, "config": masked})

    cfg = get_wa_user_config(uid)
    masked = dict(cfg)
    tok = masked.get("meta_access_token") or ""
    masked["has_token"] = bool(tok)
    masked["meta_access_token"] = ("••••" + tok[-6:]) if len(tok) > 6 else ("••••" if tok else "")
    return jsonify(masked)


@app.route("/api/wa/official/test", methods=["POST"])
@login_required
def api_wa_official_test():
    uid = current_user_id()
    data = request.get_json(silent=True) or {}
    cfg = get_wa_user_config(uid)
    pid = data.get("meta_phone_number_id") or cfg.get("meta_phone_number_id") or ""
    tok = data.get("meta_access_token") or ""
    if not tok or tok.startswith("••••"):
        tok = cfg.get("meta_access_token") or ""
    ver = data.get("meta_api_version") or cfg.get("meta_api_version") or "v21.0"
    res = wa_official.test_connection(pid, tok, ver)
    return jsonify(res), (200 if res.get("success") else 400)


@app.route("/api/wa/official/embedded-config")
@login_required
def api_wa_official_embedded_config():
    app_id = os.environ.get("META_APP_ID", "").strip()
    config_id = os.environ.get("META_EMBEDDED_CONFIG_ID", "").strip()
    api_version = os.environ.get("META_API_VERSION", "v21.0").strip()
    return jsonify({
        "enabled": bool(app_id and config_id),
        "app_id": app_id,
        "config_id": config_id,
        "api_version": api_version,
    })


@app.route("/api/wa/official/embedded-callback", methods=["POST"])
@login_required
def api_wa_official_embedded_callback():
    uid = current_user_id()
    data = request.get_json(silent=True) or {}
    code = (data.get("code") or "").strip()
    phone_number_id = (data.get("phone_number_id") or "").strip()
    waba_id = (data.get("waba_id") or "").strip()

    app_id = os.environ.get("META_APP_ID", "").strip()
    app_secret = os.environ.get("META_APP_SECRET", "").strip()
    api_version = os.environ.get("META_API_VERSION", "v21.0").strip()

    if not app_id or not app_secret:
        return jsonify({"success": False, "error": "META_APP_ID e META_APP_SECRET não configurados no servidor."}), 400
    if not code:
        return jsonify({"success": False, "error": "Código de autorização da Meta não recebido."}), 400

    tok_res = wa_official.exchange_code_for_token(app_id, app_secret, code, api_version)
    if not tok_res.get("success"):
        return jsonify(tok_res), 400

    access_token = tok_res["access_token"]
    if waba_id:
        wa_official.subscribe_waba_webhook(waba_id, access_token, api_version)

    save_wa_user_config(uid, {
        "mode": "official_api",
        "meta_phone_number_id": phone_number_id,
        "meta_waba_id": waba_id,
        "meta_access_token": access_token,
        "meta_api_version": api_version,
    })

    conn_info = wa_official.test_connection(phone_number_id, access_token, api_version) if phone_number_id else {"success": True}
    return jsonify({
        "success": True,
        "phone_number_id": phone_number_id,
        "waba_id": waba_id,
        "connection": conn_info,
    })


@app.route("/api/wa/official/templates")
@login_required
def api_wa_official_templates():
    uid = current_user_id()
    cfg = get_wa_user_config(uid)
    res = wa_official.list_templates(
        cfg.get("meta_waba_id") or "",
        cfg.get("meta_access_token") or "",
        cfg.get("meta_api_version") or "v21.0",
    )
    return jsonify(res), (200 if res.get("success") else 400)


@app.route("/api/wa/official/send", methods=["POST"])
@login_required
def api_wa_official_send():
    uid = current_user_id()
    data = request.get_json(silent=True) or {}
    lead_id = int(data.get("lead_id", 0))
    mode = data.get("send_type", "text")  # "text" ou "template"
    text = (data.get("text") or "").strip()
    template_name = (data.get("template_name") or "").strip()
    language_code = (data.get("language_code") or "pt_BR").strip()
    body_params = data.get("body_params") or []
    force = bool(data.get("force"))

    lead = next((l for l in get_leads(user_id=uid, limit=100000) if l["id"] == lead_id), None)
    if not lead or not lead.get("clean_phone"):
        return jsonify({"success": False, "error": "Lead não encontrado ou sem telefone válido."}), 400

    if not force and is_phone_already_contacted(lead["clean_phone"], user_id=uid):
        return jsonify({
            "success": False,
            "already_contacted": True,
            "error": "Este telefone já foi contatado anteriormente. Confirme para reenviar."
        }), 409

    cfg = get_wa_user_config(uid)
    pid = cfg.get("meta_phone_number_id") or ""
    tok = cfg.get("meta_access_token") or ""
    ver = cfg.get("meta_api_version") or "v21.0"

    if mode == "template":
        tname = template_name or cfg.get("default_template_name") or ""
        lang = language_code or cfg.get("default_template_lang") or "pt_BR"
        res = wa_official.send_template_message(pid, tok, lead["clean_phone"], tname, lang, body_params, ver)
        logged_text = f"[Template Meta: {tname}] " + (text or ", ".join(str(p) for p in body_params))
    else:
        if not text:
            return jsonify({"success": False, "error": "Mensagem vazia."}), 400
        res = wa_official.send_text_message(pid, tok, lead["clean_phone"], text, ver)
        logged_text = text

    if res.get("success"):
        now = time.strftime("%d/%m/%Y %H:%M")
        update_lead(lead_id, {
            "had_contact": 1,
            "contact_date": now,
            "crm_status": "contatado" if lead["crm_status"] == "novo" else lead["crm_status"],
            "whatsapp_status": "enviado",
        }, user_id=uid)
        conn = get_connection()
        try:
            conn.execute(
                """
                INSERT INTO wa_messages (user_id, lead_id, phone, direction, kind, text, status, external_id, created_at)
                VALUES (?, ?, ?, 'out', ?, ?, 'sent', ?, ?)
                """,
                (uid, lead_id, lead["clean_phone"], f"official_{mode}", logged_text, res.get("message_id", ""), time.strftime("%Y-%m-%dT%H:%M:%S"))
            )
            conn.commit()
        finally:
            conn.close()
        broadcast_event("lead_updated", {"id": lead_id, "crm_status": "contatado", "contact_date": now}, user_id=uid)
        return jsonify({"success": True, "message_id": res.get("message_id", "")})

    return jsonify(res), 400


@app.route("/api/wa/official/webhook", methods=["GET", "POST"])
def api_wa_official_webhook():
    """Endpoint público do Webhook Oficial da Meta (Verificação + Recebimento)."""
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token:
            conn = get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM wa_user_configs WHERE meta_verify_token = ? LIMIT 1", (token,))
                row = cur.fetchone()
            finally:
                conn.close()
            env_token = os.environ.get("META_VERIFY_TOKEN", "mapaleads_webhook_2026")
            if row or token == env_token:
                return Response(str(challenge or ""), status=200, mimetype="text/plain")
        return Response("Forbidden", status=403)

    payload = request.get_json(silent=True) or {}
    events = wa_official.process_webhook_payload(payload)
    for ev in events:
        if ev.get("type") == "incoming_message" and ev.get("lead_id"):
            broadcast_event("lead_updated", {"id": ev["lead_id"], "crm_status": "respondeu"}, user_id=ev["user_id"])
            broadcast_event("chat_message", {"lead_id": ev["lead_id"], "direction": "in", "text": ev.get("text", "")}, user_id=ev["user_id"])
    return jsonify({"status": "ok", "processed": len(events)}), 200


# ==================== CHAT / INBOX ESTILO KOMMO ====================

@app.route("/api/chat/threads")
@login_required
def api_chat_threads():
    uid = current_user_id()
    filter_type = (request.args.get("filter") or "all").strip()
    search_q = (request.args.get("search") or "").strip().lower()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT l.*,
                   (SELECT m.text FROM wa_messages m WHERE m.lead_id = l.id AND m.user_id = l.user_id ORDER BY m.id DESC LIMIT 1) AS last_message,
                   (SELECT m.direction FROM wa_messages m WHERE m.lead_id = l.id AND m.user_id = l.user_id ORDER BY m.id DESC LIMIT 1) AS last_direction,
                   (SELECT m.created_at FROM wa_messages m WHERE m.lead_id = l.id AND m.user_id = l.user_id ORDER BY m.id DESC LIMIT 1) AS last_message_at,
                   (SELECT COUNT(*) FROM wa_messages m WHERE m.lead_id = l.id AND m.user_id = l.user_id) AS msg_count
            FROM leads l
            WHERE l.user_id = ?
              AND (l.had_contact = 1 OR l.had_reply = 1 OR EXISTS (SELECT 1 FROM wa_messages m WHERE m.lead_id = l.id AND m.user_id = l.user_id))
            ORDER BY COALESCE(last_message_at, l.updated_at) DESC, l.id DESC
            LIMIT 250
        """, (uid,))
        rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    threads = []
    for r in rows:
        if filter_type == "replied" and not r.get("had_reply") and r.get("crm_status") != "respondeu":
            continue
        if filter_type == "contacted" and r.get("had_reply"):
            continue
        if search_q:
            hay = f"{r.get('name','')} {r.get('phone','')} {r.get('category','')} {r.get('last_message','')}".lower()
            if search_q not in hay:
                continue
        threads.append(r)
    return jsonify(threads)


@app.route("/api/chat/send", methods=["POST"])
@login_required
def api_chat_send():
    uid = current_user_id()
    data = request.get_json(silent=True) or {}
    lead_id = int(data.get("lead_id", 0))
    text = (data.get("text") or "").strip()
    channel = (data.get("channel") or "auto").strip()
    if not lead_id or not text:
        return jsonify({"success": False, "error": "Selecione um contato e digite a mensagem."}), 400

    lead = next((l for l in get_leads(user_id=uid, limit=100000) if l["id"] == lead_id), None)
    if not lead or not lead.get("clean_phone"):
        return jsonify({"success": False, "error": "Lead sem telefone válido."}), 400

    cfg = get_wa_user_config(uid)
    now = time.strftime("%d/%m/%Y %H:%M")

    # 1. Tenta Baileys (WhatsApp QR) se conectado ou se canal escolhido for 'baileys'
    if channel in ("auto", "baileys"):
        st = wa.wa_request("GET", f"/status?session_id={uid}", timeout=3)
        if st.get("state") == "connected":
            res = wa.wa_request("POST", "/send", {"session_id": str(uid), "phone": lead["clean_phone"], "text": text}, timeout=60)
            if res.get("success"):
                update_lead(lead_id, {
                    "had_contact": 1,
                    "contact_date": lead.get("contact_date") or now,
                    "crm_status": "contatado" if lead["crm_status"] == "novo" else lead["crm_status"],
                    "whatsapp_status": "enviado",
                }, user_id=uid)
                wa.log_message(lead_id, lead["clean_phone"], "out", "chat", text, user_id=uid)
                broadcast_event("chat_message", {"lead_id": lead_id, "direction": "out", "text": text}, user_id=uid)
                return jsonify({"success": True, "channel": "baileys"})
            if channel == "baileys":
                return jsonify(res), 400

    # 2. Tenta API Oficial da Meta se configurada
    if channel in ("auto", "official") and cfg.get("meta_phone_number_id") and cfg.get("meta_access_token"):
        res = wa_official.send_text_message(
            cfg["meta_phone_number_id"], cfg["meta_access_token"],
            lead["clean_phone"], text, cfg.get("meta_api_version") or "v21.0"
        )
        if res.get("success"):
            update_lead(lead_id, {
                "had_contact": 1,
                "contact_date": lead.get("contact_date") or now,
                "crm_status": "contatado" if lead["crm_status"] == "novo" else lead["crm_status"],
                "whatsapp_status": "enviado",
            }, user_id=uid)
            wa.log_message(lead_id, lead["clean_phone"], "out", "official_chat", text, user_id=uid)
            broadcast_event("chat_message", {"lead_id": lead_id, "direction": "out", "text": text}, user_id=uid)
            return jsonify({"success": True, "channel": "official"})
        if channel == "official":
            return jsonify(res), 400

    # 3. Fallback: WhatsApp Web 1-Clique (registra e retorna link wa.me para abrir)
    wa.log_message(lead_id, lead["clean_phone"], "out", "web_chat", text, user_id=uid)
    update_lead(lead_id, {
        "had_contact": 1,
        "contact_date": lead.get("contact_date") or now,
        "crm_status": "contatado" if lead["crm_status"] == "novo" else lead["crm_status"],
        "whatsapp_status": "enviado",
    }, user_id=uid)
    broadcast_event("chat_message", {"lead_id": lead_id, "direction": "out", "text": text}, user_id=uid)
    return jsonify({
        "success": True,
        "channel": "web_1click",
        "wa_url": f"https://wa.me/{lead['clean_phone']}?text={cffi_requests.utils.quote(text)}"
    })


# ==================== WHATSAPP (BAILEYS MULTI-SESSÃO) ====================
campaign = wa.CampaignRunner(broadcast_event)


@app.route("/api/wa/status")
@login_required
def api_wa_status():
    uid = current_user_id()
    st = wa.wa_request("GET", f"/status?session_id={uid}", timeout=3)
    if st.get("offline"):
        started = wa.ensure_service_running()
        st = wa.wa_request("GET", f"/status?session_id={uid}", timeout=3) if started else {
            "state": "offline",
            "error": "Serviço WhatsApp QR offline no momento."
        }
    return jsonify(st)


@app.route("/api/wa/connect", methods=["POST"])
@subscription_required
def api_wa_connect():
    uid = current_user_id()
    user = get_user_by_id(uid)
    if user and user.get("role") != "admin" and user.get("plan") == "trial":
        return jsonify({
            "success": False,
            "error": "Conexão WhatsApp QR automática disponível a partir do plano Starter/PRO. No Teste Grátis use o WhatsApp Web 1-Clique!"
        }), 403
    wa.ensure_service_running()
    force = bool((request.get_json(silent=True) or {}).get("force"))
    return jsonify(wa.wa_request("POST", "/connect", {"session_id": str(uid), "force": force}, timeout=15))


@app.route("/api/wa/logout", methods=["POST"])
@login_required
def api_wa_logout():
    uid = current_user_id()
    campaign.stop()
    return jsonify(wa.wa_request("POST", "/logout", {"session_id": str(uid)}, timeout=15))


@app.route("/api/wa/config", methods=["GET", "POST"])
@login_required
def api_wa_config():
    if request.method == "POST":
        return jsonify({"success": True, "config": wa.save_config(request.get_json(silent=True) or {})})
    return jsonify(wa.get_config())


@app.route("/api/wa/queue")
@login_required
def api_wa_queue():
    cfg = wa.get_config()
    queue_items = wa.get_queue(cfg, limit=200)
    return jsonify({
        "count": len(queue_items),
        "sent_today": wa.sent_today(),
        "daily_limit": cfg["daily_limit"],
        "preview": [{"id": l["id"], "name": l["name"], "phone": l["phone"], "category": l["category"]} for l in queue_items[:15]]
    })


@app.route("/api/wa/campaign/start", methods=["POST"])
@login_required
def api_wa_campaign_start():
    return jsonify(campaign.start())


@app.route("/api/wa/campaign/stop", methods=["POST"])
@login_required
def api_wa_campaign_stop():
    campaign.stop()
    return jsonify({"success": True})


@app.route("/api/wa/campaign/status")
@login_required
def api_wa_campaign_status():
    return jsonify(campaign.state)


@app.route("/api/wa/send-one", methods=["POST"])
@login_required
def api_wa_send_one():
    uid = current_user_id()
    data = request.get_json(silent=True) or {}
    lead_id = int(data.get("lead_id", 0))
    text = (data.get("text") or "").strip()
    force = bool(data.get("force"))
    lead = next((l for l in get_leads(user_id=uid, limit=100000) if l["id"] == lead_id), None)
    if not lead or not lead.get("clean_phone") or not text:
        return jsonify({"success": False, "error": "Lead sem telefone ou mensagem vazia."}), 400

    if not force and is_phone_already_contacted(lead["clean_phone"], user_id=uid):
        return jsonify({
            "success": False,
            "already_contacted": True,
            "error": "Este telefone já recebeu mensagem anteriormente. Confirme para reenviar."
        }), 409

    res = wa.wa_request("POST", "/send", {"session_id": str(uid), "phone": lead["clean_phone"], "text": text}, timeout=60)
    if res.get("success"):
        update_lead(lead_id, {
            "had_contact": 1,
            "contact_date": time.strftime("%d/%m/%Y %H:%M"),
            "crm_status": "contatado" if lead["crm_status"] == "novo" else lead["crm_status"],
            "whatsapp_status": "enviado",
        }, user_id=uid)
        wa.log_message(lead_id, lead["clean_phone"], "out", "pitch", text, user_id=uid)
    return jsonify(res)


@app.route("/api/leads/verify-whatsapp-all", methods=["POST"])
@login_required
def api_verify_whatsapp_all():
    uid = current_user_id()
    wa.ensure_service_running()
    st = wa.wa_request("GET", f"/status?session_id={uid}", timeout=3)
    if st.get("state") != "connected":
        return jsonify({
            "success": False,
            "error": "Baileys não está conectado. Conecte na aba Configurações > Baileys antes de verificar."
        }), 409

    data = request.get_json(silent=True) or {}
    only_unverified = data.get("only_unverified", True)

    conn = get_connection()
    cur = conn.cursor()
    if only_unverified:
        cur.execute("""
            SELECT id, name, clean_phone, phone, phone_type, whatsapp_verified
            FROM leads
            WHERE user_id = ? AND clean_phone IS NOT NULL AND clean_phone != '' AND whatsapp_verified = 0
            ORDER BY id ASC
        """, (uid,))
    else:
        cur.execute("""
            SELECT id, name, clean_phone, phone, phone_type, whatsapp_verified
            FROM leads
            WHERE user_id = ? AND clean_phone IS NOT NULL AND clean_phone != ''
            ORDER BY id ASC
        """, (uid,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return jsonify({
            "success": True,
            "message": "Nenhum lead pendente de verificação no momento.",
            "total_checked": 0,
            "active": 0,
            "inactive": 0
        })

    leads_to_check = [dict(r) for r in rows]
    phones = list({l["clean_phone"] for l in leads_to_check if l.get("clean_phone")})

    broadcast_event("log", {
        "message": f"Iniciando verificação de WhatsApp em lote ({len(phones)} telefones)...",
        "time": time.strftime("%H:%M:%S")
    }, user_id=uid)

    total_active = 0
    total_inactive = 0
    batch_size = 40

    for i in range(0, len(phones), batch_size):
        chunk = phones[i:i + batch_size]
        res = wa.wa_request("POST", "/check-batch", {"session_id": str(uid), "phones": chunk}, timeout=60)
        if res.get("success"):
            batch_res = res.get("results", {})
            stats = batch_verify_whatsapp(batch_res, user_id=uid)
            total_active += stats.get("active", 0)
            total_inactive += stats.get("inactive", 0)
            time.sleep(0.3)
        else:
            broadcast_event("log", {
                "message": f"Aviso no lote {i//batch_size + 1}: {res.get('error', 'Erro desconhecido')}",
                "time": time.strftime("%H:%M:%S")
            }, user_id=uid)

    broadcast_event("log", {
        "message": f"Verificação concluída! {total_active} ativos no WhatsApp, {total_inactive} sem WhatsApp.",
        "time": time.strftime("%H:%M:%S")
    }, user_id=uid)

    return jsonify({
        "success": True,
        "total_checked": len(phones),
        "active": total_active,
        "inactive": total_inactive,
        "message": f"Verificação concluída: {total_active} ativos no WhatsApp e {total_inactive} sem WhatsApp."
    })


@app.route("/api/leads/deduplicate", methods=["POST"])
@login_required
def api_leads_deduplicate():
    res = deduplicate_database(user_id=current_user_id())
    return jsonify(res)


@app.route("/api/wa/incoming", methods=["POST"])
def api_wa_incoming():
    data = request.get_json(silent=True) or {}
    uid = int(data.get("user_id") or 1)
    threading.Thread(
        target=wa.handle_incoming,
        args=(data.get("phone", ""), data.get("text", ""), broadcast_event, uid),
        daemon=True
    ).start()
    return jsonify({"received": True})


@app.route("/api/wa/activity")
@login_required
def api_wa_activity():
    uid = current_user_id()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT m.*, l.name AS lead_name FROM wa_messages m
            LEFT JOIN leads l ON l.id = m.lead_id
            WHERE m.user_id = ?
            ORDER BY m.id DESC LIMIT 40
        """, (uid,))
        return jsonify([dict(r) for r in cur.fetchall()])
    finally:
        conn.close()


@app.route("/api/leads/<int:lead_id>/conversation")
@login_required
def api_lead_conversation(lead_id):
    return jsonify(wa.get_conversation(lead_id, user_id=current_user_id()))


def _maintenance_loop():
    """Limpeza automática de contas de teste abandonadas e backup diário do SQLite."""
    while True:
        try:
            cleanup_expired_trials(grace_days=15)
            db_dir = os.path.dirname(os.path.abspath(DB_PATH))
            backup_dir = os.path.join(db_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(backup_dir, f"mapaleads_{time.strftime('%Y%m%d')}.db")
            if os.path.exists(DB_PATH) and not os.path.exists(backup_file):
                shutil.copy2(DB_PATH, backup_file)
                # Mantém apenas os últimos 5 backups diários
                files = sorted([f for f in os.listdir(backup_dir) if f.endswith(".db")])
                for old_f in files[:-5]:
                    try:
                        os.remove(os.path.join(backup_dir, old_f))
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(12 * 3600)


threading.Thread(target=_maintenance_loop, daemon=True).start()


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5055))
    host = os.environ.get("HOST", "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
    if os.environ.get("ENABLE_BAILEYS_AUTOSTART", "1") == "1" and not os.environ.get("PORT"):
        print("Iniciando serviço WhatsApp (Baileys) na porta 5056...")
        print("  ->", "OK" if wa.ensure_service_running() else "OPCIONAL (use API Oficial Meta ou WhatsApp Web 1-Clique)")
    print(f"Iniciando MapaLeads PRO SaaS em http://{host}:{port}")
    app.run(host=host, port=port, debug=False, threaded=True)
