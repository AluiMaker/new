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
        "id": "gmn_quebra_gelo",
        "product": "gmn",
        "title": "📍 Google Meu Negócio — Destrave Ligações & Rotas",
        "content": (
            "Olá, pessoal da {nome}! Vi a ficha de vocês no Google aqui em {bairro} ({avaliacao}⭐). "
            "Percebi 3 ajustes simples no *Google Meu Negócio* que fazem a {nome} aparecer antes dos concorrentes quando buscam por {categoria}. Posso te mostrar em 1 minuto?"
        ),
        "follow_up": (
            "Show! Montei um mini-diagnóstico da ficha da {nome} (fotos, palavras-chave e plano de avaliações). "
            "Posso mandar o resumo por aqui mesmo?"
        )
    },
    {
        "id": "gmn_fechamento_top3",
        "product": "gmn",
        "title": "📈 Google Meu Negócio — Top 3 no Mapa & Gestão Mensal",
        "content": (
            "Oi, {nome}! Coloco negócios de {categoria} no *Top 3 do Google Maps* sem gastar com anúncios. "
            "Consigo otimizar a ficha da {nome} ainda esta semana para gerar mais ligações e rotas em {bairro}. Quer ver um exemplo?"
        ),
        "follow_up": (
            "Perfeito! O pacote inclui otimização completa do perfil, respostas estratégicas e rotina para multiplicar avaliações 5⭐. Qual melhor horário para falarmos?"
        )
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
    if reviews < 80 or (rating > 0 and rating < 4.7) or wtype in ("none", "social"):
        opps.append("gmn")
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

    # 8. Academia / Cursos e Progresso por Usuário
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS academy_lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE,
        module_name TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        duration_text TEXT DEFAULT '00:45',
        video_url TEXT NOT NULL,
        target_tab TEXT DEFAULT '',
        sort_order INTEGER DEFAULT 0,
        is_published INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS academy_progress (
        user_id INTEGER NOT NULL,
        lesson_id INTEGER NOT NULL,
        completed INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, lesson_id)
    )
    """)
    _seed_academy_lessons(cursor)

    # 9. Academia de Vendas PRO (Cursos por Estratégia + VSLs White-Label)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_academy_courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE,
        strategy_key TEXT NOT NULL,
        badge_label TEXT NOT NULL,
        title TEXT NOT NULL,
        subtitle TEXT DEFAULT '',
        ticket_range TEXT DEFAULT '',
        thumbnail_url TEXT DEFAULT '',
        course_video_url TEXT NOT NULL,
        course_duration TEXT DEFAULT '00:40',
        vsl_video_url TEXT DEFAULT '',
        vsl_title TEXT DEFAULT '',
        vsl_duration TEXT DEFAULT '00:30',
        script_approach TEXT DEFAULT '',
        script_objections TEXT DEFAULT '',
        target_opp TEXT DEFAULT '',
        sort_order INTEGER DEFAULT 0,
        is_published INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_academy_progress (
        user_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        completed INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, course_id)
    )
    """)
    _seed_sales_academy_courses(cursor)

    # 10. Instagram Auto-Poster 24h (Configuração, Fila & Histórico)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ig_autoposter_config (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        enabled INTEGER DEFAULT 0,
        ig_user_id TEXT DEFAULT '',
        ig_username TEXT DEFAULT '',
        ig_access_token TEXT DEFAULT '',
        post_time TEXT DEFAULT '09:00',
        public_base_url TEXT DEFAULT 'https://mapaleadspro.online',
        content_mode TEXT DEFAULT 'mixed',
        last_post_date TEXT DEFAULT '',
        rotation_index INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("INSERT OR IGNORE INTO ig_autoposter_config (id) VALUES (1)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ig_post_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        media_type TEXT DEFAULT 'IMAGE',
        media_url TEXT NOT NULL,
        caption TEXT NOT NULL,
        topic TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ig_post_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        media_type TEXT DEFAULT 'IMAGE',
        media_url TEXT DEFAULT '',
        caption TEXT DEFAULT '',
        ig_media_id TEXT DEFAULT '',
        permalink TEXT DEFAULT '',
        status TEXT DEFAULT 'ok',
        error_msg TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

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
        "meta_app_id": os.environ.get("META_APP_ID", ""),
        "meta_app_secret": os.environ.get("META_APP_SECRET", ""),
        "meta_embedded_config_id": os.environ.get("META_EMBEDDED_CONFIG_ID", ""),
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
    for k in ("checkout_url", "checkout_pro_url", "plan_starter_price", "plan_pro_price", "support_whatsapp", "meta_app_id", "meta_embedded_config_id"):
        if k in data:
            curr[k] = str(data[k] or "").strip()
    if "meta_app_secret" in data:
        sec_val = str(data["meta_app_secret"] or "").strip()
        if not sec_val.startswith("••••"):
            curr["meta_app_secret"] = sec_val
    to_store = {k: curr.get(k, "") for k in ("checkout_url", "checkout_pro_url", "plan_starter_price", "plan_pro_price", "support_whatsapp", "meta_app_id", "meta_app_secret", "meta_embedded_config_id")}
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO whatsapp_config (key, value) VALUES ('site_settings', ?)",
            (json.dumps(to_store, ensure_ascii=False),)
        )
        conn.commit()
    finally:
        conn.close()
    return get_site_settings()


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
                        crm_status = CASE WHEN crm_status IN ('novo', 'contatado') THEN 'sem_whatsapp' ELSE crm_status END,
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
    try:
        if user_id is not None:
            cursor.execute("DELETE FROM wa_messages WHERE lead_id = ? AND user_id = ?", (lead_id, user_id))
            cursor.execute("DELETE FROM leads WHERE id = ? AND user_id = ?", (lead_id, user_id))
        else:
            cursor.execute("DELETE FROM wa_messages WHERE lead_id = ?", (lead_id,))
            cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def cleanup_leads_by_criteria(user_id: int, mode: str = "sem_whatsapp") -> int:
    """Remove leads sem WhatsApp confirmado ou marcados como perdidos, liberando cota da conta."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if mode == "perdido":
            where = "user_id = ? AND crm_status = 'perdido'"
        elif mode == "all_dead":
            where = (
                "user_id = ? AND (crm_status IN ('sem_whatsapp', 'perdido') "
                "OR whatsapp_status = 'sem_whatsapp' OR whatsapp_verified = -1 "
                "OR clean_phone IS NULL OR TRIM(clean_phone) = '')"
            )
        else:
            where = (
                "user_id = ? AND (crm_status = 'sem_whatsapp' "
                "OR whatsapp_status = 'sem_whatsapp' OR whatsapp_verified = -1 "
                "OR clean_phone IS NULL OR TRIM(clean_phone) = '')"
            )

        cur.execute(f"SELECT id FROM leads WHERE {where}", (user_id,))
        ids = [r[0] for r in cur.fetchall()]
        if not ids:
            return 0
        placeholders = ",".join("?" * len(ids))
        cur.execute(f"DELETE FROM wa_messages WHERE user_id = ? AND lead_id IN ({placeholders})", [user_id] + ids)
        cur.execute(f"DELETE FROM leads WHERE user_id = ? AND id IN ({placeholders})", [user_id] + ids)
        removed = cur.rowcount
        conn.commit()
        return removed
    finally:
        conn.close()


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
    opp_counts = {"biossite": 0, "nfc_google": 0, "gmn": 0, "cardapio_digital": 0, "whatsapp_biz": 0}
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


# ==================== ACADEMIA / CURSOS & VIDEOAULAS ====================
DEFAULT_ACADEMY_LESSONS = [
    {
        "slug": "aula-01-primeira-busca",
        "module_name": "Módulo 1 · Primeiros Passos",
        "title": "Aula 01 — Como Fazer Sua Primeira Busca no Google Maps",
        "description": "Aprenda a escolher cidade, bairro ou rua, definir o modo de varredura e extrair contatos comerciais reais com oportunidades detectadas automaticamente.",
        "duration_text": "00:26",
        "video_url": "/static/video/lessons/aula-01-busca.mp4",
        "target_tab": "tab-search",
        "sort_order": 1,
    },
    {
        "slug": "aula-02-mapa-oportunidades",
        "module_name": "Módulo 1 · Primeiros Passos",
        "title": "Aula 02 — Mapa de Oportunidades e Diagnóstico Automático",
        "description": "Veja como identificar empresas sem site, com poucas avaliações ou sem WhatsApp Business diretamente no mapa e prospectar rua por rua.",
        "duration_text": "00:24",
        "video_url": "/static/video/lessons/aula-02-mapa.mp4",
        "target_tab": "tab-map",
        "sort_order": 2,
    },
    {
        "slug": "aula-03-crm-limpeza",
        "module_name": "Módulo 2 · CRM & Limpeza de Base",
        "title": "Aula 03 — Dominando o CRM Kanban, Gaveta e Limpeza Sem WhatsApp",
        "description": "Organize seu funil de vendas por etapas, edite anotações na gaveta do lead, verifique números em lote e remova leads sem WhatsApp para liberar espaço.",
        "duration_text": "00:28",
        "video_url": "/static/video/lessons/aula-03-crm.mp4",
        "target_tab": "tab-crm",
        "sort_order": 3,
    },
    {
        "slug": "aula-04-conexao-whatsapp",
        "module_name": "Módulo 3 · WhatsApp & Conversão",
        "title": "Aula 04 — Conectando WhatsApp Oficial (1-Clique), QR Code e Regras Anti-Bloqueio",
        "description": "Compare a conexão oficial da Meta em 1 clique com o QR Code e o WhatsApp Web 1-Clique, além de configurar cadência segura de envios.",
        "duration_text": "00:23",
        "video_url": "/static/video/lessons/aula-04-whatsapp.mp4",
        "target_tab": "tab-settings",
        "sort_order": 4,
    },
    {
        "slug": "aula-05-copy-e-chat",
        "module_name": "Módulo 3 · WhatsApp & Conversão",
        "title": "Aula 05 — Modelos de Copy que Convertem e Atendimento no Chat",
        "description": "Personalize variáveis dinâmicas de abordagem para NFC, Cardápio Digital, Biossite ou WhatsApp Business e conduza respostas pelo Chat integrado.",
        "duration_text": "00:22",
        "video_url": "/static/video/lessons/aula-05-chat-copy.mp4",
        "target_tab": "tab-chat",
        "sort_order": 5,
    },
]


def _seed_academy_lessons(cursor):
    for item in DEFAULT_ACADEMY_LESSONS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO academy_lessons
                (slug, module_name, title, description, duration_text, video_url, target_tab, sort_order, is_published)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                item["slug"],
                item["module_name"],
                item["title"],
                item["description"],
                item["duration_text"],
                item["video_url"],
                item["target_tab"],
                item["sort_order"],
            ),
        )


def get_academy_lessons_for_user(user_id: int, include_unpublished: bool = False) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        where = "" if include_unpublished else "WHERE l.is_published = 1"
        cur.execute(
            f"""
            SELECT l.*, COALESCE(p.completed, 0) AS completed
            FROM academy_lessons l
            LEFT JOIN academy_progress p
              ON p.lesson_id = l.id AND p.user_id = ?
            {where}
            ORDER BY l.sort_order ASC, l.id ASC
            """,
            (user_id,),
        )
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            d["completed"] = bool(d.get("completed"))
            d["is_published"] = bool(d.get("is_published"))
            rows.append(d)
        return rows
    finally:
        conn.close()


def set_academy_lesson_progress(user_id: int, lesson_id: int, completed: bool) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        now = datetime.now().isoformat()
        cur.execute(
            """
            INSERT INTO academy_progress (user_id, lesson_id, completed, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, lesson_id) DO UPDATE SET completed = excluded.completed, updated_at = excluded.updated_at
            """,
            (user_id, lesson_id, 1 if completed else 0, now),
        )
        conn.commit()
    finally:
        conn.close()
    lessons = get_academy_lessons_for_user(user_id, include_unpublished=False)
    done = sum(1 for x in lessons if x["completed"])
    total = len(lessons)
    pct = int(round((done / total) * 100)) if total else 0
    return {"completed_count": done, "total_count": total, "percent": pct}


def upsert_academy_lesson(data: Dict[str, Any], lesson_id: Optional[int] = None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        title = (data.get("title") or "").strip() or "Nova Videoaula"
        module_name = (data.get("module_name") or "").strip() or "Módulo Geral"
        description = (data.get("description") or "").strip()
        duration_text = (data.get("duration_text") or "").strip() or "01:00"
        video_url = (data.get("video_url") or "").strip()
        target_tab = (data.get("target_tab") or "").strip()
        sort_order = int(data.get("sort_order") or 0)
        is_published = 1 if data.get("is_published", True) else 0
        if lesson_id:
            cur.execute(
                """
                UPDATE academy_lessons
                SET module_name = ?, title = ?, description = ?, duration_text = ?,
                    video_url = ?, target_tab = ?, sort_order = ?, is_published = ?
                WHERE id = ?
                """,
                (module_name, title, description, duration_text, video_url, target_tab, sort_order, is_published, lesson_id),
            )
            conn.commit()
            return lesson_id
        slug = (data.get("slug") or "").strip() or f"aula-{int(datetime.now().timestamp() * 1000)}"
        cur.execute(
            """
            INSERT INTO academy_lessons (slug, module_name, title, description, duration_text, video_url, target_tab, sort_order, is_published)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (slug, module_name, title, description, duration_text, video_url, target_tab, sort_order, is_published),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def delete_academy_lesson(lesson_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM academy_progress WHERE lesson_id = ?", (lesson_id,))
        cur.execute("DELETE FROM academy_lessons WHERE id = ?", (lesson_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ==================== ACADEMIA DE VENDAS PRO (EXCLUSIVO PRO/ENTERPRISE) ====================
DEFAULT_SALES_ACADEMY = [
    {
        "slug": "estrategia-gmn",
        "strategy_key": "gmn",
        "badge_label": "Google Meu Negócio",
        "title": "Como Vender Otimização & Top 3 no Google Meu Negócio",
        "subtitle": "Audite fichas desatualizadas em 2 minutos e feche setup de R$ 400 a R$ 1.200 + recorrência mensal de gestão.",
        "ticket_range": "R$ 400 a R$ 1.200 + mensalidade",
        "thumbnail_url": "/static/img/academy/gmn-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-gmn.mp4",
        "course_duration": "00:34",
        "vsl_video_url": "/static/video/sales-academy/vsl-gmn.mp4",
        "vsl_title": "VSL Pronta para Divulgar · Google Meu Negócio",
        "vsl_duration": "00:26",
        "script_approach": (
            "1) Quebra-Gelo: 'Olá, pessoal da {nome}! Vi a ficha de vocês no Google aqui em {bairro}. Notei 3 ajustes simples no Google Meu Negócio que colocam vocês na frente dos concorrentes sem pagar anúncio. Posso enviar um áudio rápido mostrando?'\n"
            "2) Diagnóstico em 2 min: Mostre 3 falhas reais da ficha (poucas fotos recentes, categorias secundárias vazias e falta de respostas com palavras-chave).\n"
            "3) Oferta: Otimização Completa em 48h (R$ 497) ou Pacote Mensal Top 3 + Gestão de Avaliações (R$ 397/mês)."
        ),
        "script_objections": (
            "• 'Já temos agência / já estamos no Google': 'Estar no Google é diferente de aparecer entre os 3 primeiros quando alguém digita o serviço no seu bairro. Meu trabalho é destravar ligações e pedidos de rota orgânicos sem depender de tráfego pago.'\n"
            "• 'Vou pensar e te aviso': 'Consigo fazer a auditoria completa da {nome} e entregar o plano pronto até sexta com garantia de melhoria visual na primeira semana.'"
        ),
        "target_opp": "gmn",
        "sort_order": 1,
    },
    {
        "slug": "estrategia-nfc",
        "strategy_key": "nfc",
        "badge_label": "Plaquinha NFC + QR",
        "title": "Como Vender Plaquinha NFC + QR Code de Avaliações 5⭐",
        "subtitle": "Produto físico de entrada irresistível: encostou o celular, avaliou no Google. Ticket rápido de R$ 150 a R$ 350 por unidade.",
        "ticket_range": "R$ 150 a R$ 350 / plaquinha",
        "thumbnail_url": "/static/img/academy/nfc-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-nfc.mp4",
        "course_duration": "00:33",
        "vsl_video_url": "/static/video/sales-academy/vsl-nfc.mp4",
        "vsl_title": "VSL Pronta para Divulgar · Plaquinha NFC & QR",
        "vsl_duration": "00:26",
        "script_approach": (
            "1) Quebra-Gelo: 'Oi, {nome}! Vi vocês no Google com {avaliacao}⭐. Trabalho com Plaquinhas NFC de balcão: seu cliente encosta o celular e já cai direto na tela de avaliação 5 estrelas, Instagram ou Pix. Posso te mandar uma foto modelo com a sua logo?'\n"
            "2) Demonstração: Envie a VSL pronta junto com uma prévia visual da plaquinha.\n"
            "3) Combo Upsell: 1 plaquinha por R$ 197 ou kit com 3 plaquinhas de mesa/caixa por R$ 447 + otimização do Google de bônus."
        ),
        "script_objections": (
            "• 'Cliente não costuma avaliar': 'Exatamente porque ninguém lembra! Quando você coloca a placa no caixa e o atendente diz só \"encosta aqui se gostou\", suas avaliações multiplicam sem esforço.'\n"
            "• 'É caro?': 'Com apenas 2 clientes novos que escolherem vocês no Google por terem mais avaliações, a plaquinha já se pagou para sempre — sem mensalidade.'"
        ),
        "target_opp": "nfc_google",
        "sort_order": 2,
    },
    {
        "slug": "estrategia-whatsapp",
        "strategy_key": "whatsapp",
        "badge_label": "WhatsApp Business",
        "title": "Como Vender Estruturação de WhatsApp Business & Catálogo",
        "subtitle": "Transforme atendimento bagunçado em máquina organizada com etiquetas, catálogo de serviços e respostas instantâneas.",
        "ticket_range": "R$ 500 a R$ 1.500",
        "thumbnail_url": "/static/img/academy/whatsapp-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-whatsapp.mp4",
        "course_duration": "00:32",
        "vsl_video_url": "/static/video/sales-academy/vsl-whatsapp.mp4",
        "vsl_title": "VSL Pronta para Divulgar · WhatsApp Business PRO",
        "vsl_duration": "00:25",
        "script_approach": (
            "1) Quebra-Gelo: 'Olá, equipe da {nome}! Peguei o contato no Google. Eu estruturo o WhatsApp Business de empresas de {categoria} com catálogo, mensagens de boas-vindas e etiquetas de funil para nenhum orçamento esfriar. Posso mostrar como funciona?'\n"
            "2) Diagnóstico: Pergunte quantos orçamentos ficam sem resposta no fim de semana.\n"
            "3) Fechamento: Setup completo em 24h com catálogo visual + 10 scripts prontos por R$ 590."
        ),
        "script_objections": (
            "• 'Já usamos WhatsApp normal': 'Justamente por usar o comum você perde histórico, não tem catálogo clicável nem mensagem automática quando está ocupado. No Business profissional o cliente já escolhe e pede sozinho.'"
        ),
        "target_opp": "whatsapp_biz",
        "sort_order": 3,
    },
    {
        "slug": "estrategia-cardapio",
        "strategy_key": "cardapio",
        "badge_label": "Cardápio Digital",
        "title": "Como Vender Cardápio Digital + QR na Mesa Sem Taxas",
        "subtitle": "Ajude restaurantes, pizzarias e hamburguerias a economizar até 27% de comissão de aplicativos recebendo pedidos direto no WhatsApp.",
        "ticket_range": "R$ 297 setup + R$ 97 a R$ 297/mês",
        "thumbnail_url": "/static/img/academy/cardapio-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-cardapio.mp4",
        "course_duration": "00:33",
        "vsl_video_url": "/static/video/sales-academy/vsl-cardapio.mp4",
        "vsl_title": "VSL Pronta para Divulgar · Cardápio Digital & QR",
        "vsl_duration": "00:26",
        "script_approach": (
            "1) Quebra-Gelo: 'Oi, pessoal da {nome}! Vi vocês aqui em {bairro}. Vocês já trabalham com Cardápio Digital próprio sem pagar comissão por pedido, ligado direto no WhatsApp? Quer ver um modelo ao vivo funcionando?'\n"
            "2) Gancho Financeiro: Mostre quanto R$ 5.000 em apps custam de taxa todo mês vs um link próprio com QR Code na mesa.\n"
            "3) Oferta: Cardápio montado com fotos + QR Code para imprimir nas mesas em 48h."
        ),
        "script_objections": (
            "• 'Não temos tempo para cadastrar produtos': 'Nós cadastramos todo o seu cardápio inicial com fotos e preços em até 48 horas; você só recebe o pedido mastigado no WhatsApp.'"
        ),
        "target_opp": "cardapio_digital",
        "sort_order": 4,
    },
    {
        "slug": "estrategia-biossite",
        "strategy_key": "biossite",
        "badge_label": "Biossite & Landing Page",
        "title": "Como Vender Biossites & Landing Pages para Quem Não Tem Site",
        "subtitle": "Feche vendas rápidas em 48 horas para empresas que só têm link do Instagram ou nenhum site listado no Google Maps.",
        "ticket_range": "R$ 400 a R$ 1.500",
        "thumbnail_url": "/static/img/academy/biossite-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-biossite.mp4",
        "course_duration": "00:32",
        "vsl_video_url": "/static/video/sales-academy/vsl-biossite.mp4",
        "vsl_title": "VSL Pronta para Divulgar · Biossite & Site Rápido",
        "vsl_duration": "00:25",
        "script_approach": (
            "1) Quebra-Gelo: 'Olá, {nome}! Vi que no Google vocês ainda não têm um site oficial clicável. Eu crio páginas rápidas com seus serviços, avaliações 5⭐ e botão direto para o WhatsApp. Posso te mandar uma prévia sem compromisso?'\n"
            "2) Técnica da Prévia: Envie um mockup personalizado usando o nome e fotos do negócio.\n"
            "3) Fechamento: Entrega expressa em 48h conectada direto ao perfil do Google Maps."
        ),
        "script_objections": (
            "• 'Instagram já basta': 'Quem pesquisa no Google já está com o cartão na mão pronto para comprar hoje e muitas vezes não entra no Instagram. Um Biossite oficial no Google passa confiança imediata.'"
        ),
        "target_opp": "biossite",
        "sort_order": 5,
    },
]


def _seed_sales_academy_courses(cursor):
    for item in DEFAULT_SALES_ACADEMY:
        cursor.execute(
            """
            INSERT OR IGNORE INTO sales_academy_courses (
                slug, strategy_key, badge_label, title, subtitle, ticket_range,
                thumbnail_url, course_video_url, course_duration,
                vsl_video_url, vsl_title, vsl_duration,
                script_approach, script_objections, target_opp, sort_order, is_published
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                item["slug"], item["strategy_key"], item["badge_label"], item["title"],
                item["subtitle"], item["ticket_range"], item["thumbnail_url"],
                item["course_video_url"], item["course_duration"],
                item["vsl_video_url"], item["vsl_title"], item["vsl_duration"],
                item["script_approach"], item["script_objections"],
                item["target_opp"], item["sort_order"],
            ),
        )


def has_pro_sales_access(user_id: int) -> bool:
    user = get_user_by_id(user_id)
    if not user:
        return False
    if user.get("role") == "admin":
        return True
    acc = get_user_access_status(user_id)
    if not acc.get("active"):
        return False
    return normalize_plan_name(acc.get("plan")) in ("pro", "enterprise")


def get_sales_academy_for_user(user_id: int, include_unpublished: bool = False) -> Dict[str, Any]:
    unlocked = has_pro_sales_access(user_id)
    conn = get_connection()
    cur = conn.cursor()
    try:
        where = "" if include_unpublished else "WHERE c.is_published = 1"
        cur.execute(
            f"""
            SELECT c.*, COALESCE(p.completed, 0) AS completed
            FROM sales_academy_courses c
            LEFT JOIN sales_academy_progress p
              ON p.course_id = c.id AND p.user_id = ?
            {where}
            ORDER BY c.sort_order ASC, c.id ASC
            """,
            (user_id,),
        )
        items = []
        for r in cur.fetchall():
            d = dict(r)
            d["completed"] = bool(d.get("completed"))
            d["is_published"] = bool(d.get("is_published"))
            if not unlocked and not include_unpublished:
                d["course_video_url"] = ""
                d["vsl_video_url"] = ""
                d["download_url"] = ""
            else:
                d["download_url"] = f"/api/sales-academy/download/{d['slug']}"
            items.append(d)
        done = sum(1 for x in items if x["completed"])
        total = len(items)
        return {
            "unlocked": unlocked,
            "items": items,
            "completed_count": done,
            "total_count": total,
            "percent": int(round((done / total) * 100)) if total else 0,
        }
    finally:
        conn.close()


def get_sales_academy_course_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM sales_academy_courses WHERE slug = ?", (slug,))
        r = cur.fetchone()
        return dict(r) if r else None
    finally:
        conn.close()


def set_sales_academy_progress(user_id: int, course_id: int, completed: bool) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        now = datetime.now().isoformat()
        cur.execute(
            """
            INSERT INTO sales_academy_progress (user_id, course_id, completed, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, course_id) DO UPDATE SET completed = excluded.completed, updated_at = excluded.updated_at
            """,
            (user_id, course_id, 1 if completed else 0, now),
        )
        conn.commit()
    finally:
        conn.close()
    res = get_sales_academy_for_user(user_id, include_unpublished=False)
    return {
        "completed_count": res["completed_count"],
        "total_count": res["total_count"],
        "percent": res["percent"],
    }


def upsert_sales_academy_course(data: Dict[str, Any], course_id: Optional[int] = None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        strategy_key = (data.get("strategy_key") or "gmn").strip()
        badge_label = (data.get("badge_label") or "Estratégia").strip()
        title = (data.get("title") or "Novo Curso").strip()
        subtitle = (data.get("subtitle") or "").strip()
        ticket_range = (data.get("ticket_range") or "").strip()
        thumbnail_url = (data.get("thumbnail_url") or "/static/img/academy/gmn-hero.jpg").strip()
        course_video_url = (data.get("course_video_url") or "").strip()
        course_duration = (data.get("course_duration") or "01:00").strip()
        vsl_video_url = (data.get("vsl_video_url") or "").strip()
        vsl_title = (data.get("vsl_title") or "VSL Pronta para Divulgar").strip()
        vsl_duration = (data.get("vsl_duration") or "00:30").strip()
        script_approach = (data.get("script_approach") or "").strip()
        script_objections = (data.get("script_objections") or "").strip()
        target_opp = (data.get("target_opp") or "").strip()
        sort_order = int(data.get("sort_order") or 0)
        is_published = 1 if data.get("is_published", True) else 0
        if course_id:
            cur.execute(
                """
                UPDATE sales_academy_courses SET
                    strategy_key=?, badge_label=?, title=?, subtitle=?, ticket_range=?,
                    thumbnail_url=?, course_video_url=?, course_duration=?,
                    vsl_video_url=?, vsl_title=?, vsl_duration=?,
                    script_approach=?, script_objections=?, target_opp=?,
                    sort_order=?, is_published=?
                WHERE id=?
                """,
                (
                    strategy_key, badge_label, title, subtitle, ticket_range,
                    thumbnail_url, course_video_url, course_duration,
                    vsl_video_url, vsl_title, vsl_duration,
                    script_approach, script_objections, target_opp,
                    sort_order, is_published, course_id,
                ),
            )
            conn.commit()
            return course_id
        slug = (data.get("slug") or "").strip() or f"curso-{int(datetime.now().timestamp() * 1000)}"
        cur.execute(
            """
            INSERT INTO sales_academy_courses (
                slug, strategy_key, badge_label, title, subtitle, ticket_range,
                thumbnail_url, course_video_url, course_duration,
                vsl_video_url, vsl_title, vsl_duration,
                script_approach, script_objections, target_opp, sort_order, is_published
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                slug, strategy_key, badge_label, title, subtitle, ticket_range,
                thumbnail_url, course_video_url, course_duration,
                vsl_video_url, vsl_title, vsl_duration,
                script_approach, script_objections, target_opp, sort_order, is_published,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def delete_sales_academy_course(course_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM sales_academy_progress WHERE course_id = ?", (course_id,))
        cur.execute("DELETE FROM sales_academy_courses WHERE id = ?", (course_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ==================== INSTAGRAM AUTO-POSTER 24H ====================
def get_ig_config() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM ig_autoposter_config WHERE id = 1")
        row = cur.fetchone()
        if not row:
            return {
                "id": 1, "enabled": False, "ig_user_id": "", "ig_username": "",
                "ig_access_token": "", "post_time": "09:00",
                "public_base_url": "https://mapaleadspro.online",
                "content_mode": "mixed", "last_post_date": "", "rotation_index": 0,
            }
        d = dict(row)
        d["enabled"] = bool(d.get("enabled"))
        return d
    finally:
        conn.close()


def save_ig_config(data: Dict[str, Any]) -> Dict[str, Any]:
    curr = get_ig_config()
    enabled = 1 if data.get("enabled", curr["enabled"]) else 0
    ig_user_id = (data.get("ig_user_id") if "ig_user_id" in data else curr["ig_user_id"] or "").strip()
    ig_username = (data.get("ig_username") if "ig_username" in data else curr["ig_username"] or "").strip()
    ig_access_token = (data.get("ig_access_token") if "ig_access_token" in data else curr["ig_access_token"] or "").strip()
    if ig_access_token.startswith("****") and curr.get("ig_access_token"):
        ig_access_token = curr["ig_access_token"]
    post_time = (data.get("post_time") if "post_time" in data else curr["post_time"] or "09:00").strip()
    public_base_url = (data.get("public_base_url") if "public_base_url" in data else curr["public_base_url"] or "https://mapaleadspro.online").strip().rstrip("/")
    content_mode = (data.get("content_mode") if "content_mode" in data else curr["content_mode"] or "mixed").strip()
    last_post_date = (data.get("last_post_date") if "last_post_date" in data else curr.get("last_post_date", "")).strip()
    rotation_index = int(data.get("rotation_index") if "rotation_index" in data else curr.get("rotation_index", 0))

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE ig_autoposter_config SET
                enabled=?, ig_user_id=?, ig_username=?, ig_access_token=?,
                post_time=?, public_base_url=?, content_mode=?,
                last_post_date=?, rotation_index=?, updated_at=?
            WHERE id = 1
            """,
            (
                enabled, ig_user_id, ig_username, ig_access_token,
                post_time, public_base_url, content_mode,
                last_post_date, rotation_index, datetime.now().isoformat(),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    return get_ig_config()


def list_ig_queue(status: Optional[str] = "pending") -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        if status:
            cur.execute("SELECT * FROM ig_post_queue WHERE status = ? ORDER BY id ASC", (status,))
        else:
            cur.execute("SELECT * FROM ig_post_queue ORDER BY id DESC LIMIT 50")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def add_ig_queue_item(media_url: str, caption: str, media_type: str = "IMAGE", topic: str = "") -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO ig_post_queue (media_type, media_url, caption, topic, status) VALUES (?, ?, ?, ?, 'pending')",
            (media_type, media_url, caption, topic),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def delete_ig_queue_item(item_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM ig_post_queue WHERE id = ?", (item_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def mark_ig_queue_item_status(item_id: int, status: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE ig_post_queue SET status = ? WHERE id = ?", (status, item_id))
        conn.commit()
    finally:
        conn.close()


def record_ig_history(media_type: str, media_url: str, caption: str, status: str, ig_media_id: str = "", permalink: str = "", error_msg: str = "") -> int:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO ig_post_history (media_type, media_url, caption, ig_media_id, permalink, status, error_msg)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (media_type, media_url, caption, ig_media_id, permalink, status, error_msg),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_ig_history(limit: int = 25) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM ig_post_history ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


init_db()
