import sqlite3
import os
import json
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.environ.get("DATABASE_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapaleads.db")

FOOD_KEYWORDS = (
    "restaurante", "pizzaria", "hamburgueria", "lanchonete", "padaria", "cafeteria",
    "cafe", "café", "bar", "bistro", "bistrô", "sorveteria", "açaí", "acai",
    "doceria", "confeitaria", "churrascaria", "sushi", "temakeria", "marmitaria",
    "comida", "gastronomia", "petiscaria", "cervejaria", "pastelaria", "tapiocaria"
)

DEFAULT_TEMPLATES = [
    {
        "id": "quebra_gelo_antibloqueio",
        "product": "geral",
        "title": "🧊 Quebra-Gelo Inicial (Anti-Bloqueio - 1ª Mensagem)",
        "content": (
            "Olá, pessoal da {nome}! Tudo bem? "
            "Posso tirar uma dúvida rápida com quem cuida do atendimento ou marketing aí?"
        ),
        "follow_up": (
            "Obrigado pelo retorno! Vi o perfil da {nome} no Google aqui em {bairro}. "
            "Posso te mostrar rapidinho como gerar mais avaliações no Google e organizar seus atendimentos no WhatsApp?"
        )
    },
    {
        "id": "nfc_avaliacoes_google",
        "product": "nfc",
        "title": "Plaquinha NFC + QR Code (Google, Pix, Wi-Fi & Insta)",
        "content": (
            "Olá, {nome}! Vi vocês no Google ({avaliacao}⭐). Trabalho com *Plaquinhas NFC + QR Code* personalizadas: "
            "o cliente encosta o celular e já abre sua *Avaliação 5⭐ no Google*, *Instagram*, *Pix* ou *Wi-Fi*. "
            "Posso te enviar uma foto modelo?"
        ),
        "follow_up": "Show! Consigo montar uma prévia com a logo da {nome} sem compromisso. Mando por aqui mesmo?"
    },
    {
        "id": "cardapio_digital_nfc",
        "product": "cardapio",
        "title": "Cardápio Digital + Plaquinha NFC de Mesa",
        "content": (
            "Oi, pessoal da {nome}! Vi vocês no Google em {bairro}. Vocês já usam *Cardápio Digital com Plaquinha NFC + QR* na mesa? "
            "O cliente encosta o celular, vê o cardápio e pede direto no WhatsApp. Quer ver um modelo ao vivo?"
        ),
        "follow_up": "Perfeito! Vou te mandar o link de demonstração. Em até 48h deixamos o da {nome} pronto!"
    },
    {
        "id": "whatsapp_business_setup",
        "product": "whatsapp",
        "title": "Configuração WhatsApp Business",
        "content": (
            "Olá, equipe da {nome}! Peguei o contato no Google. Eu estruturo o *WhatsApp Business* de empresas de {categoria} "
            "com catálogo, respostas rápidas e etiquetas para vocês não perderem nenhum cliente. Posso te mostrar como funciona?"
        ),
        "follow_up": "Ótimo! É bem rápido e já deixa seu atendimento organizado no mesmo dia. Quer ver os detalhes?"
    },
    {
        "id": "biossite_landing_page",
        "product": "biossite",
        "title": "Biossite & Landing Page (Sem Site)",
        "content": (
            "Olá, {nome}! Vi que no Google vocês ainda não têm um site oficial. Eu crio *Biossites e Landing Pages* rápidas "
            "com seus serviços, localização e botão direto pro WhatsApp. Posso te mandar uma prévia sem compromisso?"
        ),
        "follow_up": "Maravilha! Tenho 2 modelos prontos para {categoria}. Posso enviar os links aqui?"
    },
    {
        "id": "combo_presenca_local",
        "product": "combo",
        "title": "Combo Presença Local (WhatsApp + NFC + Biossite)",
        "content": (
            "Olá, {nome}! Ajudo negócios de {bairro} a venderem mais no Google com *Biossite + WhatsApp Business configurado + Plaquinha NFC (Avaliações/Pix/Insta)*. "
            "Posso te enviar uma apresentação rápida?"
        ),
        "follow_up": "Show! Vou te enviar exemplos reais e condições da semana. Qual melhor horário para falarmos?"
    }
]


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
    except Exception:
        pass
    return conn


def compute_lead_opportunities(lead: Dict[str, Any]) -> List[str]:
    """Identifica oportunidades comerciais para o lead com base nos dados do Google."""
    opps: List[str] = []
    wtype = (lead.get("website_type") or "none").lower()
    website = (lead.get("website") or "").strip()
    reviews = int(lead.get("reviews_count") or 0)
    rating = float(lead.get("rating") or 0.0)
    category = (lead.get("category") or "").lower()
    phone_type = (lead.get("phone_type") or "").lower()

    if wtype in ("none", "social", "directory") or not website:
        opps.append("biossite")
    if reviews < 50 or (rating > 0 and rating < 4.6):
        opps.append("nfc_google")
    if any(k in category for k in FOOD_KEYWORDS):
        opps.append("cardapio_digital")
    if lead.get("clean_phone"):
        opps.append("whatsapp_biz")
    if not opps:
        opps.append("nfc_google")
    return opps


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabela de Usuários (Multi-Tenant SaaS)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        company_name TEXT DEFAULT '',
        role TEXT DEFAULT 'user',
        plan TEXT DEFAULT 'pro',
        is_active INTEGER DEFAULT 1,
        subscription_status TEXT DEFAULT 'active',
        plan_expires_at TEXT DEFAULT '',
        max_leads INTEGER DEFAULT 0,
        signup_ip TEXT DEFAULT '',
        billing_customer_id TEXT DEFAULT '',
        must_set_password INTEGER DEFAULT 0,
        verification_hint TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login_at TEXT
    )
    """)

    for col_name, col_type in [
        ("subscription_status", "TEXT DEFAULT 'active'"),
        ("plan_expires_at", "TEXT DEFAULT ''"),
        ("max_leads", "INTEGER DEFAULT 0"),
        ("signup_ip", "TEXT DEFAULT ''"),
        ("billing_customer_id", "TEXT DEFAULT ''"),
        ("must_set_password", "INTEGER DEFAULT 0"),
        ("verification_hint", "TEXT DEFAULT ''"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS billing_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gateway TEXT DEFAULT 'kiwify',
        event_type TEXT DEFAULT '',
        email TEXT DEFAULT '',
        status TEXT DEFAULT 'ok',
        details TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Garante usuário administrador padrão se não existir nenhum usuário
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_admin_email = os.environ.get("ADMIN_EMAIL", "admin@mapaleads.pro")
        default_admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123")
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, company_name, role, plan, is_active)
            VALUES (?, ?, ?, ?, 'admin', 'agency', 1)
            """,
            ("Administrador", default_admin_email, generate_password_hash(default_admin_pass), "MapaLeads PRO")
        )

    cursor.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1")
    default_user_id = cursor.fetchone()[0]

    # 2. Tabela de Leads
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        name TEXT NOT NULL,
        category TEXT,
        address TEXT,
        street TEXT,
        neighborhood TEXT,
        city TEXT,
        phone TEXT,
        clean_phone TEXT,
        is_whatsapp BOOLEAN DEFAULT 0,
        phone_type TEXT DEFAULT 'unknown',
        whatsapp_verified INTEGER DEFAULT 0,
        rating REAL,
        reviews_count INTEGER DEFAULT 0,
        website TEXT,
        website_type TEXT DEFAULT 'none',
        maps_url TEXT,
        search_query TEXT,
        crm_status TEXT DEFAULT 'novo',
        product_interest TEXT DEFAULT '',
        notes TEXT,
        had_contact INTEGER DEFAULT 0,
        contact_date TEXT,
        had_reply INTEGER DEFAULT 0,
        had_sale INTEGER DEFAULT 0,
        sale_value REAL DEFAULT 0.0,
        tags TEXT DEFAULT '',
        whatsapp_status TEXT DEFAULT 'pendente',
        lat REAL,
        lon REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Verifica se a tabela antiga tinha UNIQUE global em maps_url e migra preservando dados
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='leads'")
    leads_sql_row = cursor.fetchone()
    leads_sql = leads_sql_row[0] if leads_sql_row else ""
    if "maps_url TEXT UNIQUE" in leads_sql:
        cursor.execute("PRAGMA table_info(leads)")
        existing_cols = [r[1] for r in cursor.fetchall()]
        cursor.execute("ALTER TABLE leads RENAME TO leads_old_mig")
        cursor.execute("""
        CREATE TABLE leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            name TEXT NOT NULL,
            category TEXT,
            address TEXT,
            street TEXT,
            neighborhood TEXT,
            city TEXT,
            phone TEXT,
            clean_phone TEXT,
            is_whatsapp BOOLEAN DEFAULT 0,
            phone_type TEXT DEFAULT 'unknown',
            whatsapp_verified INTEGER DEFAULT 0,
            rating REAL,
            reviews_count INTEGER DEFAULT 0,
            website TEXT,
            website_type TEXT DEFAULT 'none',
            maps_url TEXT,
            search_query TEXT,
            crm_status TEXT DEFAULT 'novo',
            product_interest TEXT DEFAULT '',
            notes TEXT,
            had_contact INTEGER DEFAULT 0,
            contact_date TEXT,
            had_reply INTEGER DEFAULT 0,
            had_sale INTEGER DEFAULT 0,
            sale_value REAL DEFAULT 0.0,
            tags TEXT DEFAULT '',
            whatsapp_status TEXT DEFAULT 'pendente',
            lat REAL,
            lon REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        common_cols = [c for c in existing_cols if c in (
            "id", "user_id", "name", "category", "address", "street", "neighborhood", "city",
            "phone", "clean_phone", "is_whatsapp", "phone_type", "whatsapp_verified",
            "rating", "reviews_count", "website", "website_type", "maps_url", "search_query",
            "crm_status", "product_interest", "notes", "had_contact", "contact_date",
            "had_reply", "had_sale", "sale_value", "tags", "whatsapp_status", "lat", "lon",
            "created_at", "updated_at"
        )]
        cols_csv = ", ".join(common_cols)
        cursor.execute(f"INSERT INTO leads ({cols_csv}) SELECT {cols_csv} FROM leads_old_mig")
        cursor.execute("DROP TABLE leads_old_mig")

    # Migrações incrementais de colunas em leads
    columns_to_add = [
        ("user_id", f"INTEGER DEFAULT {default_user_id}"),
        ("had_contact", "INTEGER DEFAULT 0"),
        ("contact_date", "TEXT"),
        ("had_reply", "INTEGER DEFAULT 0"),
        ("had_sale", "INTEGER DEFAULT 0"),
        ("sale_value", "REAL DEFAULT 0.0"),
        ("tags", "TEXT DEFAULT ''"),
        ("whatsapp_status", "TEXT DEFAULT 'pendente'"),
        ("phone_type", "TEXT DEFAULT 'unknown'"),
        ("whatsapp_verified", "INTEGER DEFAULT 0"),
        ("product_interest", "TEXT DEFAULT ''"),
        ("lat", "REAL"),
        ("lon", "REAL"),
    ]
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE leads ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("UPDATE leads SET user_id = ? WHERE user_id IS NULL", (default_user_id,))
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_user_id ON leads(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_user_maps ON leads(user_id, maps_url)")
    except Exception:
        pass

    # Classificação de telefones fixos vs móveis existentes
    cursor.execute("""
    UPDATE leads SET phone_type = 'fixed', is_whatsapp = 1
    WHERE clean_phone IS NOT NULL AND LENGTH(clean_phone) = 12
      AND (phone_type IS NULL OR phone_type = 'unknown' OR is_whatsapp = 0)
    """)
    cursor.execute("""
    UPDATE leads SET phone_type = 'mobile', is_whatsapp = 1
    WHERE clean_phone IS NOT NULL AND LENGTH(clean_phone) = 13
      AND (phone_type IS NULL OR phone_type = 'unknown')
    """)

    # 3. Histórico de buscas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        query TEXT,
        niche TEXT,
        location TEXT,
        total_found INTEGER DEFAULT 0,
        no_website_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    try:
        cursor.execute(f"ALTER TABLE search_history ADD COLUMN user_id INTEGER DEFAULT {default_user_id}")
    except sqlite3.OperationalError:
        pass

    # 4. Modelos de Copy (por usuário)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pitch_templates (
        id TEXT NOT NULL,
        user_id INTEGER NOT NULL DEFAULT 1,
        product TEXT DEFAULT 'geral',
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        follow_up TEXT DEFAULT '',
        meta_template_name TEXT DEFAULT '',
        PRIMARY KEY (id, user_id)
    )
    """)
    # Migração de tabela antiga de pitch_templates se não tiver user_id
    cursor.execute("PRAGMA table_info(pitch_templates)")
    pt_cols = [r[1] for r in cursor.fetchall()]
    if "user_id" not in pt_cols:
        cursor.execute("ALTER TABLE pitch_templates RENAME TO pitch_templates_old")
        cursor.execute("""
        CREATE TABLE pitch_templates (
            id TEXT NOT NULL,
            user_id INTEGER NOT NULL DEFAULT 1,
            product TEXT DEFAULT 'geral',
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            follow_up TEXT DEFAULT '',
            meta_template_name TEXT DEFAULT '',
            PRIMARY KEY (id, user_id)
        )
        """)
        cursor.execute(
            "INSERT INTO pitch_templates (id, user_id, title, content, follow_up) SELECT id, ?, title, content, COALESCE(follow_up, '') FROM pitch_templates_old",
            (default_user_id,)
        )
        cursor.execute("DROP TABLE pitch_templates_old")

    for col_name, col_type in [
        ("product", "TEXT DEFAULT 'geral'"),
        ("follow_up", "TEXT DEFAULT ''"),
        ("meta_template_name", "TEXT DEFAULT ''"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE pitch_templates ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    # 5. Configurações de WhatsApp (global legado + por usuário)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS whatsapp_config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wa_user_configs (
        user_id INTEGER PRIMARY KEY,
        mode TEXT DEFAULT 'web_1click',
        meta_phone_number_id TEXT DEFAULT '',
        meta_waba_id TEXT DEFAULT '',
        meta_access_token TEXT DEFAULT '',
        meta_verify_token TEXT DEFAULT 'mapaleads_webhook_2026',
        meta_api_version TEXT DEFAULT 'v21.0',
        default_template_name TEXT DEFAULT '',
        default_template_lang TEXT DEFAULT 'pt_BR',
        delay_min INTEGER DEFAULT 45,
        delay_max INTEGER DEFAULT 90,
        auto_reply_enabled INTEGER DEFAULT 1,
        google_places_api_key TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. Mensagens WhatsApp
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wa_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        lead_id INTEGER,
        phone TEXT,
        direction TEXT,
        kind TEXT,
        text TEXT,
        status TEXT DEFAULT 'ok',
        external_id TEXT DEFAULT '',
        created_at TEXT
    )
    """)
    for col_name, col_type in [
        ("user_id", f"INTEGER DEFAULT {default_user_id}"),
        ("external_id", "TEXT DEFAULT ''"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE wa_messages ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

    # Seed templates para o usuário padrão se ele ainda não tiver
    seed_user_templates(cursor, default_user_id)

    conn.commit()

    # Limpeza básica de leads inválidos
    try:
        cursor.execute("""
            DELETE FROM leads
            WHERE clean_phone IS NULL
               OR clean_phone = ''
               OR LENGTH(clean_phone) < 12
               OR clean_phone LIKE '550800%'
               OR clean_phone LIKE '550300%'
               OR clean_phone LIKE '0800%'
        """)
        _deduplicate_with_cursor(cursor, default_user_id)
        conn.commit()
    except Exception:
        pass

    conn.close()


def seed_user_templates(cursor, user_id: int):
    cursor.execute("SELECT COUNT(*) FROM pitch_templates WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0]
    if total == 0:
        for t in DEFAULT_TEMPLATES:
            cursor.execute(
                """
                INSERT OR IGNORE INTO pitch_templates (id, user_id, product, title, content, follow_up)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (t["id"], user_id, t.get("product", "geral"), t["title"], t["content"], t.get("follow_up", ""))
            )
    else:
        # Garante que o Quebra-Gelo exista e atualiza templates padrão antigos muito longos (>280 chars)
        for t in DEFAULT_TEMPLATES:
            cursor.execute(
                """
                INSERT OR IGNORE INTO pitch_templates (id, user_id, product, title, content, follow_up)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (t["id"], user_id, t.get("product", "geral"), t["title"], t["content"], t.get("follow_up", ""))
            )
            cursor.execute(
                """
                UPDATE pitch_templates
                SET title = ?, content = ?, follow_up = ?, product = ?
                WHERE id = ? AND user_id = ? AND LENGTH(content) > 280
                """,
                (t["title"], t["content"], t.get("follow_up", ""), t.get("product", "geral"), t["id"], user_id)
            )


def reset_user_templates(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        for t in DEFAULT_TEMPLATES:
            cursor.execute(
                """
                INSERT OR REPLACE INTO pitch_templates (id, user_id, product, title, content, follow_up)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (t["id"], user_id, t.get("product", "geral"), t["title"], t["content"], t.get("follow_up", ""))
            )
        conn.commit()
    finally:
        conn.close()


# ==================== USUÁRIOS, ASSINATURAS & AUTH ====================

PLAN_DEFAULTS = {
    "trial": {"max_leads": 25, "days": 1, "status": "trial", "label": "Teste Grátis (1 dia · 25 leads salvos)"},
    "starter": {"max_leads": 500, "days": 30, "status": "active", "label": "Starter (até 500 leads salvos)"},
    "pro": {"max_leads": 2000, "days": 30, "status": "active", "label": "PRO (até 2.000 leads salvos · Prioridade)"},
    "enterprise": {"max_leads": 0, "days": 30, "status": "active", "label": "Enterprise (Ilimitado · Prioridade)"},
    "agency": {"max_leads": 0, "days": 30, "status": "active", "label": "Enterprise (Ilimitado · Prioridade)"},
}


def normalize_plan_name(plan: Optional[str]) -> str:
    p = (plan or "trial").strip().lower()
    if p in ("agency", "ent", "custom"):
        return "enterprise"
    if p in PLAN_DEFAULTS:
        return p
    return "trial"


def get_plan_defaults(plan: str) -> Dict[str, Any]:
    return PLAN_DEFAULTS.get(normalize_plan_name(plan), PLAN_DEFAULTS["trial"])


def _count_user_quota_leads(cursor, user_id: int, plan: str) -> int:
    """Conta o total de leads salvos na conta para respeitar o limite do plano (25 / 500 / 2.000)."""
    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ?", (user_id,))
    return int(cursor.fetchone()[0] or 0)


def count_recent_signups_by_ip(ip: str, hours: int = 24) -> int:
    if not ip:
        return 0
    cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM users WHERE signup_ip = ? AND created_at >= ?", (ip, cutoff))
        return int(cur.fetchone()[0] or 0)
    finally:
        conn.close()


def create_user(
    name: str,
    email: str,
    password: str,
    company_name: str = "",
    role: str = "user",
    plan: str = "pro",
    days: Optional[int] = None,
    max_leads: Optional[int] = None,
    signup_ip: str = "",
) -> Tuple[Optional[int], Optional[str]]:
    email_clean = (email or "").strip().lower()
    if not email_clean or "@" not in email_clean:
        return None, "E-mail inválido."
    if not password or len(password) < 6:
        return None, "A senha deve ter pelo menos 6 caracteres."

    plan_norm = normalize_plan_name(plan)
    p_cfg = get_plan_defaults(plan_norm)
    sub_status = "active" if role == "admin" else p_cfg["status"]
    use_days = days if days is not None else p_cfg["days"]
    use_max_leads = max_leads if max_leads is not None else (0 if role == "admin" else p_cfg["max_leads"])
    expires_at = "" if (role == "admin" or use_days <= 0) else (datetime.now() + timedelta(days=use_days)).isoformat()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM users WHERE email = ?", (email_clean,))
        if cur.fetchone():
            return None, "Este e-mail já está cadastrado."
        cur.execute(
            """
            INSERT INTO users (name, email, password_hash, company_name, role, plan, is_active, subscription_status, plan_expires_at, max_leads, signup_ip)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
            """,
            (
                name.strip() or email_clean.split("@")[0],
                email_clean,
                generate_password_hash(password),
                company_name.strip(),
                role,
                plan_norm,
                sub_status,
                expires_at,
                use_max_leads,
                signup_ip or "",
            )
        )
        uid = cur.lastrowid
        seed_user_templates(cur, uid)
        cur.execute("INSERT OR IGNORE INTO wa_user_configs (user_id) VALUES (?)", (uid,))
        conn.commit()
        return uid, None
    finally:
        conn.close()


def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    email_clean = (email or "").strip().lower()
    if not email_clean:
        return None
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, company_name, role, plan, is_active, subscription_status, plan_expires_at, max_leads FROM users WHERE email = ?", (email_clean,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    email_clean = (email or "").strip().lower()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE email = ?", (email_clean,))
        row = cur.fetchone()
        if not row:
            return None
        user = dict(row)
        if not user.get("is_active"):
            return None
        if not check_password_hash(user["password_hash"], password or ""):
            return None
        cur.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (datetime.now().isoformat(), user["id"]))
        conn.commit()
        user.pop("password_hash", None)
        return user
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, name, email, company_name, role, plan, is_active, subscription_status, plan_expires_at, max_leads, created_at, last_login_at FROM users WHERE id = ?",
            (user_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_access_status(user_id: int) -> Dict[str, Any]:
    """Verifica validade da assinatura/trial e limite de leads do usuário."""
    user = get_user_by_id(user_id)
    if not user or not user.get("is_active"):
        return {"active": False, "reason": "inactive", "days_left": 0, "leads_count": 0, "max_leads": 0, "plan": "none"}

    plan_name = normalize_plan_name(user.get("plan"))
    conn = get_connection()
    cur = conn.cursor()
    try:
        leads_count = _count_user_quota_leads(cur, user_id, plan_name)
    finally:
        conn.close()

    if user.get("role") == "admin":
        return {"active": True, "reason": "admin", "days_left": 9999, "leads_count": leads_count, "max_leads": 0, "plan": plan_name or "enterprise", "subscription_status": "active"}

    sub_status = (user.get("subscription_status") or "active").lower()
    if sub_status in ("suspended", "expired", "canceled"):
        return {
            "active": False,
            "reason": sub_status,
            "days_left": 0,
            "leads_count": leads_count,
            "max_leads": int(user.get("max_leads") or 0),
            "plan": user.get("plan", "trial"),
            "expires_at": user.get("plan_expires_at", ""),
            "subscription_status": sub_status,
        }

    exp_str = (user.get("plan_expires_at") or "").strip()
    days_left = 999
    hours_left = 999
    if exp_str:
        try:
            exp_dt = datetime.fromisoformat(exp_str)
            delta = exp_dt - datetime.now()
            if delta.total_seconds() <= 0:
                update_user(user_id, {"subscription_status": "expired"})
                return {
                    "active": False,
                    "reason": "expired",
                    "days_left": 0,
                    "hours_left": 0,
                    "leads_count": leads_count,
                    "max_leads": int(user.get("max_leads") or 0),
                    "plan": user.get("plan", "trial"),
                    "expires_at": exp_str,
                    "subscription_status": "expired",
                }
            days_left = max(1, int(delta.total_seconds() // 86400) + 1)
            hours_left = max(1, int(delta.total_seconds() // 3600) + 1)
        except Exception:
            pass

    max_leads = int(user.get("max_leads") or 0)
    return {
        "active": True,
        "reason": "ok",
        "days_left": days_left,
        "hours_left": hours_left,
        "leads_count": leads_count,
        "max_leads": max_leads,
        "leads_limit_reached": (max_leads > 0 and leads_count >= max_leads),
        "plan": user.get("plan", "trial"),
        "expires_at": exp_str,
        "subscription_status": sub_status,
    }


def extend_user_subscription(user_id: int, days: int = 30, plan: Optional[str] = None, max_leads: Optional[int] = None) -> Optional[Dict[str, Any]]:
    user = get_user_by_id(user_id)
    if not user:
        return None
    now = datetime.now()
    base = now
    exp_str = (user.get("plan_expires_at") or "").strip()
    if exp_str and (user.get("subscription_status") in ("active", "trial")):
        try:
            curr_exp = datetime.fromisoformat(exp_str)
            if curr_exp > now:
                base = curr_exp
        except Exception:
            pass

    new_exp = (base + timedelta(days=int(days))).isoformat()
    raw_plan = plan or (user.get("plan") if user.get("plan") != "trial" else "starter")
    new_plan = normalize_plan_name(raw_plan)
    p_cfg = get_plan_defaults(new_plan)
    use_max = max_leads if max_leads is not None else p_cfg["max_leads"]

    update_user(user_id, {
        "plan": new_plan,
        "subscription_status": "active",
        "plan_expires_at": new_exp,
        "max_leads": use_max,
        "is_active": 1,
    })
    return get_user_by_id(user_id)


def list_users() -> List[Dict[str, Any]]:
    cutoff_30d = (datetime.now() - timedelta(days=30)).isoformat()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT u.id, u.name, u.email, u.company_name, u.role, u.plan, u.is_active,
                   u.subscription_status, u.plan_expires_at, u.max_leads,
                   u.created_at, u.last_login_at,
                   (SELECT COUNT(*) FROM leads l WHERE l.user_id = u.id) as leads_count,
                   (SELECT COUNT(*) FROM leads l WHERE l.user_id = u.id AND l.created_at >= ?) as leads_30d_count
            FROM users u
            ORDER BY u.id ASC
        """, (cutoff_30d,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def update_user(user_id: int, fields: Dict[str, Any]) -> bool:
    allowed = {"name", "company_name", "role", "plan", "is_active", "subscription_status", "plan_expires_at", "max_leads", "billing_customer_id", "must_set_password", "verification_hint"}
    updates = []
    params = []
    for k, v in fields.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            params.append(v)
    if fields.get("password") and len(str(fields["password"])) >= 6:
        updates.append("password_hash = ?")
        params.append(generate_password_hash(str(fields["password"])))
    if not updates:
        return False
    params.append(user_id)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def cleanup_expired_trials(grace_days: int = 15) -> int:
    """Remove contas de teste abandonadas vencidas há mais de grace_days para não acumular lixo no servidor."""
    cutoff = (datetime.now() - timedelta(days=grace_days)).isoformat()
    conn = get_connection()
    cur = conn.cursor()
    removed = 0
    try:
        cur.execute(
            """
            SELECT id FROM users
            WHERE role != 'admin'
              AND plan = 'trial'
              AND plan_expires_at != ''
              AND plan_expires_at < ?
            """,
            (cutoff,)
        )
        ids = [r[0] for r in cur.fetchall()]
        for uid in ids:
            cur.execute("DELETE FROM leads WHERE user_id = ?", (uid,))
            cur.execute("DELETE FROM search_history WHERE user_id = ?", (uid,))
            cur.execute("DELETE FROM pitch_templates WHERE user_id = ?", (uid,))
            cur.execute("DELETE FROM wa_messages WHERE user_id = ?", (uid,))
            cur.execute("DELETE FROM wa_user_configs WHERE user_id = ?", (uid,))
            cur.execute("DELETE FROM users WHERE id = ?", (uid,))
            wa_root = os.environ.get("WA_AUTH_ROOT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_service", "auth_sessions")
            shutil.rmtree(os.path.join(wa_root, f"user_{uid}"), ignore_errors=True)
            removed += 1
        conn.commit()
    finally:
        conn.close()
    return removed


def log_billing_event(gateway: str, event_type: str, email: str, status: str, details: str = ""):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO billing_events (gateway, event_type, email, status, details) VALUES (?, ?, ?, ?, ?)",
            (gateway or "kiwify", event_type or "", email or "", status or "ok", details or "")
        )
        conn.commit()
    finally:
        conn.close()


def complete_first_access(email: str, hint_digits: str, new_password: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Permite que comprador da Kiwify defina sua senha no primeiro acesso validando e-mail + últimos 4 dígitos do CPF/WhatsApp."""
    email_clean = (email or "").strip().lower()
    hint_clean = "".join(c for c in str(hint_digits or "") if c.isdigit())[-4:]
    if not email_clean or not new_password or len(new_password) < 6:
        return None, "Informe um e-mail válido e senha com no mínimo 6 caracteres."

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE email = ?", (email_clean,))
        row = cur.fetchone()
        if not row:
            return None, "Nenhuma assinatura encontrada com esse e-mail."
        user = dict(row)
        if not user.get("must_set_password"):
            return None, "Esta conta já possui senha definida. Faça login normalmente."
        saved_hint = (user.get("verification_hint") or "").strip()
        if saved_hint and hint_clean not in saved_hint.split(","):
            return None, "Os últimos 4 dígitos do CPF ou WhatsApp não conferem com o cadastro da compra."

        cur.execute(
            "UPDATE users SET password_hash = ?, must_set_password = 0, last_login_at = ? WHERE id = ?",
            (generate_password_hash(new_password), datetime.now().isoformat(), user["id"])
        )
        conn.commit()
        return get_user_by_id(user["id"]), None
    finally:
        conn.close()


def get_admin_dashboard_stats() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, role, plan, is_active, subscription_status, plan_expires_at FROM users")
        users = [dict(r) for r in cur.fetchall()]
        now = datetime.now()
        paid_active = 0
        trial_active = 0
        expired_count = 0
        for u in users:
            if u.get("role") == "admin":
                continue
            sub = (u.get("subscription_status") or "active").lower()
            exp_str = (u.get("plan_expires_at") or "").strip()
            is_expired = (not u.get("is_active")) or sub in ("expired", "suspended", "canceled")
            if not is_expired and exp_str:
                try:
                    if datetime.fromisoformat(exp_str) <= now:
                        is_expired = True
                except Exception:
                    pass
            if is_expired:
                expired_count += 1
            elif u.get("plan") == "trial" or sub == "trial":
                trial_active += 1
            else:
                paid_active += 1

        cur.execute("SELECT COUNT(*) FROM leads")
        total_leads = int(cur.fetchone()[0] or 0)

        cur.execute("SELECT * FROM billing_events ORDER BY id DESC LIMIT 20")
        events = [dict(r) for r in cur.fetchall()]

        return {
            "paid_active": paid_active,
            "trial_active": trial_active,
            "expired_count": expired_count,
            "total_clients": paid_active + trial_active + expired_count,
            "total_leads": total_leads,
            "recent_events": events,
        }
    finally:
        conn.close()


def get_site_settings() -> Dict[str, str]:
    defaults = {
        "checkout_url": os.environ.get("CHECKOUT_URL", ""),
        "checkout_pro_url": os.environ.get("CHECKOUT_PRO_URL", ""),
        "plan_starter_price": os.environ.get("PLAN_STARTER_PRICE", "R$ 37"),
        "plan_pro_price": os.environ.get("PLAN_PRO_PRICE", "R$ 79"),
        "support_whatsapp": os.environ.get("SUPPORT_WHATSAPP", ""),
    }
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT value FROM whatsapp_config WHERE key = 'site_settings'")
        row = cur.fetchone()
        if row and row[0]:
            try:
                saved = json.loads(row[0])
                for k, v in saved.items():
                    if k in defaults and v is not None:
                        defaults[k] = str(v)
                # Migração suave caso o DB tenha sido salvo antes da separação Starter/PRO
                if "plan_starter_price" not in saved and saved.get("plan_pro_price") in ("R$ 37", "37"):
                    defaults["plan_starter_price"] = "R$ 37"
                    defaults["plan_pro_price"] = "R$ 79"
            except Exception:
                pass
        wa_digits = "".join(c for c in defaults.get("support_whatsapp", "") if c.isdigit())
        defaults["support_whatsapp_digits"] = wa_digits
        if wa_digits:
            from urllib.parse import quote
            msg = quote("Olá! Tenho interesse no plano Enterprise do MapaLeads PRO para fechamento personalizado.")
            defaults["enterprise_wa_url"] = f"https://wa.me/{wa_digits}?text={msg}"
        else:
            defaults["enterprise_wa_url"] = ""
        return defaults
    finally:
        conn.close()


def save_site_settings(data: Dict[str, Any]) -> Dict[str, str]:
    curr = get_site_settings()
    for k in ("checkout_url", "checkout_pro_url", "plan_starter_price", "plan_pro_price", "support_whatsapp"):
        if k in data:
            curr[k] = str(data[k] or "").strip()
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO whatsapp_config (key, value) VALUES ('site_settings', ?)",
            (json.dumps(curr, ensure_ascii=False),)
        )
        conn.commit()
    finally:
        conn.close()
    return curr


# ==================== CONFIGURAÇÃO WHATSAPP POR USUÁRIO ====================

def get_wa_user_config(user_id: int) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM wa_user_configs WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT OR IGNORE INTO wa_user_configs (user_id) VALUES (?)", (user_id,))
            conn.commit()
            cur.execute("SELECT * FROM wa_user_configs WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
        return dict(row) if row else {"user_id": user_id, "mode": "web_1click"}
    finally:
        conn.close()


def save_wa_user_config(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    allowed = {
        "mode", "meta_phone_number_id", "meta_waba_id", "meta_access_token",
        "meta_verify_token", "meta_api_version", "default_template_name",
        "default_template_lang", "delay_min", "delay_max", "auto_reply_enabled",
        "google_places_api_key"
    }
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT OR IGNORE INTO wa_user_configs (user_id) VALUES (?)", (user_id,))
        updates = []
        params = []
        for k, v in data.items():
            if k in allowed:
                updates.append(f"{k} = ?")
                params.append(v)
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(user_id)
            cur.execute(f"UPDATE wa_user_configs SET {', '.join(updates)} WHERE user_id = ?", params)
            conn.commit()
    finally:
        conn.close()
    return get_wa_user_config(user_id)


def find_user_by_phone_number_id(phone_number_id: str) -> Optional[Dict[str, Any]]:
    if not phone_number_id:
        return None
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM wa_user_configs WHERE meta_phone_number_id = ? LIMIT 1", (phone_number_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# ==================== DEDUPLICAÇÃO & VERIFICAÇÃO ====================

def _deduplicate_with_cursor(cursor, user_id: int = 1) -> int:
    cursor.execute("""
        SELECT clean_phone FROM leads
        WHERE user_id = ? AND clean_phone IS NOT NULL AND clean_phone != ''
        GROUP BY clean_phone
        HAVING COUNT(*) > 1
    """, (user_id,))
    dup_phones = [r[0] for r in cursor.fetchall()]
    removed_count = 0
    for phone in dup_phones:
        cursor.execute("""
            SELECT id, name, had_contact, crm_status, reviews_count, notes, tags, maps_url
            FROM leads
            WHERE user_id = ? AND clean_phone = ?
            ORDER BY had_contact DESC, (CASE WHEN crm_status != 'novo' THEN 1 ELSE 0 END) DESC, reviews_count DESC, id ASC
        """, (user_id, phone))
        rows = cursor.fetchall()
        if len(rows) > 1:
            master = rows[0]
            master_id = master["id"]
            duplicates = rows[1:]
            merged_notes = master["notes"] or ""
            merged_tags = master["tags"] or ""
            for dup in duplicates:
                if dup["notes"] and dup["notes"] not in merged_notes:
                    merged_notes = f"{merged_notes}\n{dup['notes']}".strip()
                if dup["tags"]:
                    for t in dup["tags"].split(","):
                        t_clean = t.strip()
                        if t_clean and t_clean not in merged_tags:
                            merged_tags = f"{merged_tags}, {t_clean}".strip(", ")
            cursor.execute("UPDATE leads SET notes = ?, tags = ? WHERE id = ?", (merged_notes, merged_tags, master_id))
            dup_ids = [d["id"] for d in duplicates]
            cursor.execute(f"DELETE FROM leads WHERE id IN ({','.join(['?']*len(dup_ids))})", dup_ids)
            removed_count += len(dup_ids)
    return removed_count


def deduplicate_database(user_id: int = 1) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        count = _deduplicate_with_cursor(cur, user_id)
        conn.commit()
        return {"success": True, "duplicates_removed": count}
    finally:
        conn.close()


def is_phone_already_contacted(clean_phone: Optional[str], user_id: int = 1) -> bool:
    if not clean_phone:
        return False
    digits = "".join(c for c in str(clean_phone) if c.isdigit())
    if len(digits) < 8:
        return False
    tail = digits[-8:]
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM wa_messages WHERE user_id = ? AND phone LIKE ? AND direction = 'out' LIMIT 1", (user_id, f"%{tail}"))
        if cur.fetchone():
            return True
        cur.execute("SELECT 1 FROM leads WHERE user_id = ? AND (clean_phone LIKE ? OR phone LIKE ?) AND (had_contact = 1 OR whatsapp_status IN ('enviado', 'ja_contatado')) LIMIT 1", (user_id, f"%{tail}", f"%{tail}"))
        if cur.fetchone():
            return True
    finally:
        conn.close()
    return False


def batch_verify_whatsapp(results: Dict[str, Dict[str, Any]], user_id: int = 1) -> Dict[str, int]:
    if not results:
        return {"updated": 0, "active": 0, "inactive": 0}
    conn = get_connection()
    cur = conn.cursor()
    active_count = 0
    inactive_count = 0
    try:
        now = datetime.now().isoformat()
        for phone, info in results.items():
            digits = "".join(c for c in str(phone) if c.isdigit())
            if len(digits) < 8:
                continue
            tail = digits[-8:]
            exists = bool(info.get("exists"))
            full_p = f"55{digits}" if not digits.startswith("55") else digits
            if exists:
                active_count += 1
                cur.execute("""
                    UPDATE leads SET
                        is_whatsapp = 1,
                        whatsapp_verified = 1,
                        whatsapp_status = CASE WHEN whatsapp_status = 'pendente' THEN 'verificado' ELSE whatsapp_status END,
                        updated_at = ?
                    WHERE user_id = ? AND (clean_phone = ? OR clean_phone LIKE ?)
                """, (now, user_id, full_p, f"%{tail}"))
            else:
                inactive_count += 1
                cur.execute("""
                    UPDATE leads SET
                        is_whatsapp = 0,
                        whatsapp_verified = -1,
                        whatsapp_status = 'sem_whatsapp',
                        updated_at = ?
                    WHERE user_id = ? AND (clean_phone = ? OR clean_phone LIKE ?)
                """, (now, user_id, full_p, f"%{tail}"))
        conn.commit()
    finally:
        conn.close()
    return {"updated": active_count + inactive_count, "active": active_count, "inactive": inactive_count}


# ==================== LEADS CRUD (ESCOPO POR USUÁRIO) ====================

def upsert_lead(lead_data: Dict[str, Any], user_id: int = 1) -> Tuple[int, bool]:
    conn = get_connection()
    cursor = conn.cursor()

    maps_url = lead_data.get("maps_url")
    name = lead_data.get("name")
    clean_p = lead_data.get("clean_phone")
    phone = lead_data.get("phone")

    existing = None
    if maps_url:
        cursor.execute(
            "SELECT id, crm_status, notes, had_contact, had_reply, had_sale, sale_value, tags, clean_phone, whatsapp_status, phone_type, whatsapp_verified FROM leads WHERE user_id = ? AND maps_url = ?",
            (user_id, maps_url)
        )
        existing = cursor.fetchone()

    if not existing and clean_p and len(clean_p) >= 10:
        tail = clean_p[-8:]
        cursor.execute(
            "SELECT id, crm_status, notes, had_contact, had_reply, had_sale, sale_value, tags, clean_phone, whatsapp_status, phone_type, whatsapp_verified FROM leads WHERE user_id = ? AND (clean_phone = ? OR clean_phone LIKE ?) LIMIT 1",
            (user_id, clean_p, f"%{tail}")
        )
        existing = cursor.fetchone()

    if not existing and name and phone:
        cursor.execute(
            "SELECT id, crm_status, notes, had_contact, had_reply, had_sale, sale_value, tags, clean_phone, whatsapp_status, phone_type, whatsapp_verified FROM leads WHERE user_id = ? AND name = ? AND phone = ?",
            (user_id, name, phone)
        )
        existing = cursor.fetchone()

    now = datetime.now().isoformat()
    already_contacted = is_phone_already_contacted(clean_p, user_id=user_id)
    phone_type = lead_data.get("phone_type") or ("mobile" if (clean_p and len(clean_p) == 13 and clean_p[4] == "9") else "fixed")
    wa_verified = lead_data.get("whatsapp_verified", 0)

    if existing:
        lead_id = existing["id"]
        had_contact_val = 1 if (existing["had_contact"] == 1 or already_contacted) else 0
        wa_status_val = existing["whatsapp_status"] if existing["whatsapp_status"] else ("ja_contatado" if already_contacted else "pendente")
        crm_status_val = existing["crm_status"]
        if already_contacted and crm_status_val == "novo":
            crm_status_val = "contatado"

        cursor.execute("""
        UPDATE leads SET
            name = COALESCE(?, name),
            category = COALESCE(?, category),
            address = COALESCE(?, address),
            street = COALESCE(?, street),
            neighborhood = COALESCE(?, neighborhood),
            city = COALESCE(?, city),
            phone = COALESCE(?, phone),
            clean_phone = COALESCE(?, clean_phone),
            is_whatsapp = COALESCE(?, is_whatsapp),
            phone_type = COALESCE(?, phone_type),
            whatsapp_verified = CASE WHEN whatsapp_verified != 0 THEN whatsapp_verified ELSE ? END,
            rating = COALESCE(?, rating),
            reviews_count = COALESCE(?, reviews_count),
            website = ?,
            website_type = ?,
            search_query = COALESCE(?, search_query),
            had_contact = ?,
            whatsapp_status = ?,
            crm_status = ?,
            lat = COALESCE(?, lat),
            lon = COALESCE(?, lon),
            updated_at = ?
        WHERE id = ? AND user_id = ?
        """, (
            lead_data.get("name"),
            lead_data.get("category"),
            lead_data.get("address"),
            lead_data.get("street"),
            lead_data.get("neighborhood"),
            lead_data.get("city"),
            lead_data.get("phone"),
            clean_p,
            lead_data.get("is_whatsapp"),
            phone_type,
            wa_verified,
            lead_data.get("rating"),
            lead_data.get("reviews_count"),
            lead_data.get("website"),
            lead_data.get("website_type", "none"),
            lead_data.get("search_query"),
            had_contact_val,
            wa_status_val,
            crm_status_val,
            lead_data.get("lat"),
            lead_data.get("lon"),
            now,
            lead_id,
            user_id
        ))
        conn.commit()
        conn.close()
        return lead_id, False
    else:
        # Garante respeito ao limite de leads do plano (25 no Trial; mensal nos planos Starter/PRO)
        cursor.execute("SELECT role, plan, max_leads FROM users WHERE id = ?", (user_id,))
        urow = cursor.fetchone()
        if urow and urow["role"] != "admin" and int(urow["max_leads"] or 0) > 0:
            curr_cnt = _count_user_quota_leads(cursor, user_id, urow["plan"] or "trial")
            if curr_cnt >= int(urow["max_leads"]):
                conn.close()
                return 0, False

        tags_list = []
        if lead_data.get("website_type") == "none":
            tags_list.append("Sem Site")
        elif lead_data.get("website_type") == "social":
            tags_list.append("Só Rede Social")
        if int(lead_data.get("reviews_count") or 0) < 50:
            tags_list.append("Poucas Avaliações")
        cat_lower = (lead_data.get("category") or "").lower()
        if any(k in cat_lower for k in FOOD_KEYWORDS):
            tags_list.append("Gastronomia")
        if already_contacted:
            tags_list.append("Já Contatado")

        tags_initial = ", ".join(tags_list)
        had_contact_val = 1 if already_contacted else 0
        wa_status_val = "ja_contatado" if already_contacted else "pendente"
        crm_status_val = "contatado" if already_contacted else "novo"

        cursor.execute("""
        INSERT INTO leads (
            user_id, name, category, address, street, neighborhood, city,
            phone, clean_phone, is_whatsapp, phone_type, whatsapp_verified,
            rating, reviews_count, website, website_type, maps_url, search_query,
            crm_status, notes, tags, had_contact, had_reply, had_sale, sale_value, whatsapp_status,
            lat, lon, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', ?, ?, 0, 0, 0.0, ?, ?, ?, ?, ?)
        """, (
            user_id,
            lead_data.get("name"),
            lead_data.get("category"),
            lead_data.get("address"),
            lead_data.get("street"),
            lead_data.get("neighborhood"),
            lead_data.get("city"),
            lead_data.get("phone"),
            clean_p,
            lead_data.get("is_whatsapp", 0),
            phone_type,
            wa_verified,
            lead_data.get("rating"),
            lead_data.get("reviews_count", 0),
            lead_data.get("website"),
            lead_data.get("website_type", "none"),
            maps_url,
            lead_data.get("search_query"),
            crm_status_val,
            tags_initial,
            had_contact_val,
            wa_status_val,
            lead_data.get("lat"),
            lead_data.get("lon"),
            now,
            now
        ))
        lead_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return lead_id, True


def get_leads(
    user_id: int = 1,
    website_type: Optional[str] = None,
    crm_status: Optional[str] = None,
    opportunity: Optional[str] = None,
    tag: Optional[str] = None,
    has_contact: Optional[str] = None,
    has_reply: Optional[str] = None,
    has_sale: Optional[str] = None,
    has_phone: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM leads WHERE user_id = ?"
    params: List[Any] = [user_id]

    if website_type and website_type != "all":
        if website_type == "no_website":
            query += " AND (website_type = 'none' OR website_type IS NULL OR website IS NULL OR website = '')"
        elif website_type == "social_or_none":
            query += " AND (website_type IN ('none', 'social', 'directory') OR website IS NULL OR website = '')"
        else:
            query += " AND website_type = ?"
            params.append(website_type)

    if crm_status and crm_status != "all":
        query += " AND crm_status = ?"
        params.append(crm_status)

    if tag and tag != "all":
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")

    if has_contact in ("1", "true", True):
        query += " AND had_contact = 1"
    elif has_contact in ("0", "false", False):
        query += " AND had_contact = 0"

    if has_reply in ("1", "true", True):
        query += " AND had_reply = 1"

    if has_sale in ("1", "true", True):
        query += " AND had_sale = 1"

    if has_phone:
        query += " AND clean_phone IS NOT NULL AND clean_phone != ''"

    if search:
        search_like = f"%{search.strip()}%"
        query += " AND (name LIKE ? OR category LIKE ? OR address LIKE ? OR neighborhood LIKE ? OR street LIKE ? OR tags LIKE ? OR city LIKE ?)"
        params.extend([search_like] * 7)

    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    leads = []
    for r in rows:
        d = dict(r)
        d["opportunities"] = compute_lead_opportunities(d)
        if opportunity and opportunity != "all" and opportunity not in d["opportunities"]:
            continue
        leads.append(d)
    return leads


def update_lead(lead_id: int, fields: Dict[str, Any], user_id: Optional[int] = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    allowed = [
        "crm_status", "notes", "had_contact", "contact_date", "had_reply",
        "had_sale", "sale_value", "tags", "whatsapp_status", "product_interest"
    ]
    updates = []
    params = []

    for k, v in fields.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            params.append(v)

    if not updates:
        conn.close()
        return False

    now = datetime.now().isoformat()
    updates.append("updated_at = ?")
    params.append(now)
    params.append(lead_id)

    if user_id is not None:
        params.append(user_id)
        sql = f"UPDATE leads SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
    else:
        sql = f"UPDATE leads SET {', '.join(updates)} WHERE id = ?"

    cursor.execute(sql, params)
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    return affected


def delete_lead(lead_id: int, user_id: Optional[int] = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    if user_id is not None:
        cursor.execute("DELETE FROM leads WHERE id = ? AND user_id = ?", (lead_id, user_id))
    else:
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    return affected


def get_stats(user_id: int = 1) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND (website_type IN ('none', 'social') OR website IS NULL OR website = '')", (user_id,))
    no_website = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND COALESCE(reviews_count, 0) < 50", (user_id,))
    low_reviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND had_contact = 1", (user_id,))
    contacted = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND had_reply = 1", (user_id,))
    replied = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(sale_value), 0.0) FROM leads WHERE user_id = ? AND had_sale = 1", (user_id,))
    sales_row = cursor.fetchone()
    sales_count = sales_row[0]
    sales_total_val = sales_row[1]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND is_whatsapp = 1", (user_id,))
    with_whatsapp = cursor.fetchone()[0]

    cursor.execute("SELECT crm_status, COUNT(*) as cnt FROM leads WHERE user_id = ? GROUP BY crm_status", (user_id,))
    status_counts = {r["crm_status"]: r["cnt"] for r in cursor.fetchall()}

    # Contagem de oportunidades por oferta
    cursor.execute("SELECT website_type, website, reviews_count, rating, category, clean_phone, phone_type FROM leads WHERE user_id = ?", (user_id,))
    opp_counts = {"biossite": 0, "nfc_google": 0, "cardapio_digital": 0, "whatsapp_biz": 0}
    for row in cursor.fetchall():
        for o in compute_lead_opportunities(dict(row)):
            opp_counts[o] = opp_counts.get(o, 0) + 1

    conn.close()
    return {
        "total": total,
        "no_website": no_website,
        "low_reviews": low_reviews,
        "contacted": contacted,
        "replied": replied,
        "sales_count": sales_count,
        "sales_revenue": sales_total_val,
        "with_whatsapp": with_whatsapp,
        "crm_status": status_counts,
        "opportunities": opp_counts
    }


def record_search(query: str, niche: str, location: str, total_found: int, no_website_count: int, user_id: int = 1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO search_history (user_id, query, niche, location, total_found, no_website_count)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, query, niche, location, total_found, no_website_count))
    conn.commit()
    conn.close()


def get_search_history(user_id: int = 1, limit: int = 15) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM search_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_pitch_templates(user_id: int = 1) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    seed_user_templates(cursor, user_id)
    conn.commit()
    cursor.execute("SELECT * FROM pitch_templates WHERE user_id = ? ORDER BY CASE WHEN id = 'quebra_gelo_antibloqueio' THEN 0 ELSE 1 END, rowid ASC", (user_id,))
    templates = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return templates


def save_pitch_template(template_id: str, title: str, content: str, follow_up: str = "", product: str = "geral", meta_template_name: str = "", user_id: int = 1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT OR REPLACE INTO pitch_templates (id, user_id, product, title, content, follow_up, meta_template_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (template_id, user_id, product, title, content, follow_up, meta_template_name)
    )
    conn.commit()
    conn.close()


def delete_pitch_template(template_id: str, user_id: int = 1) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pitch_templates WHERE id = ? AND user_id = ?", (template_id, user_id))
    conn.commit()
    affected = cursor.rowcount > 0
    conn.close()
    return affected


init_db()
