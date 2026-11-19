import sqlite3
import os
import json
import hmac
import base64
import hashlib
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.environ.get("DATABASE_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "mapaleads.db")


def _get_Persistent_secret() -> str:
    env_key = os.environ.get("SECRET_KEY", "").strip()
    if env_key:
        return env_key
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    for candidate in (
        os.path.join(db_dir, ".secret_key"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".secret_key"),
    ):
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    val = f.read().strip()
                    if val:
                        return val
            except Exception:
                pass
    return "mapaleads-default-local-key"


def encrypt_secret(plaintext: str) -> str:
    """Criptografa tokens sensíveis antes de salvar no SQLite (prefixo ENCv1:)."""
    if not plaintext or plaintext.startswith("ENCv1:"):
        return plaintext or ""
    secret = _get_Persistent_secret()
    salt = os.urandom(8)
    key = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, 50_000, dklen=32)
    raw = plaintext.encode("utf-8")
    out = bytearray(len(raw))
    for idx, b in enumerate(raw):
        ks = hashlib.blake2s(salt + (idx // 32).to_bytes(4, "big"), key=key).digest()
        out[idx] = b ^ ks[idx % 32]
    mac = hmac.new(key, salt + bytes(out), hashlib.sha256).digest()[:16]
    token_b64 = base64.urlsafe_b64encode(salt + mac + bytes(out)).decode("ascii")
    return f"ENCv1:{token_b64}"


def decrypt_secret(value: str) -> str:
    """Descriptografa tokens salvos com ENCv1:; mantém retrocompatibilidade com valores antigos em texto."""
    if not value or not value.startswith("ENCv1:"):
        return value or ""
    try:
        blob = base64.urlsafe_b64decode(value[6:].encode("ascii"))
        salt, mac, cipher = blob[:8], blob[8:24], blob[24:]
        secret = _get_Persistent_secret()
        key = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, 50_000, dklen=32)
        expected_mac = hmac.new(key, salt + cipher, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(mac, expected_mac):
            return ""
        out = bytearray(len(cipher))
        for idx, b in enumerate(cipher):
            ks = hashlib.blake2s(salt + (idx // 32).to_bytes(4, "big"), key=key).digest()
            out[idx] = b ^ ks[idx % 32]
        return bytes(out).decode("utf-8")
    except Exception:
        return ""

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
        conn.execute("PRAGMA busy_timeout=15000")
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


def compute_lead_score(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    P1.1 — Lead Score Auditável (0 a 100) + Classificação de Oportunidade.
    Diferencia estritamente dados verificados da ficha do Google Maps de critérios heurísticos de oportunidade.
    """
    score = 0
    verified_facts: List[str] = []
    score_reasons: List[Dict[str, Any]] = []

    wtype = (lead.get("website_type") or "none").lower()
    website = (lead.get("website") or "").strip()
    clean_phone = (lead.get("clean_phone") or "").strip()
    phone_type = (lead.get("phone_type") or "unknown").lower()
    wa_verified = int(lead.get("whatsapp_verified") or 0)
    is_wa = bool(lead.get("is_whatsapp"))
    reviews = int(lead.get("reviews_count") or 0)
    rating = float(lead.get("rating") or 0.0)
    category = (lead.get("category") or "").strip()
    address = (lead.get("address") or lead.get("street") or "").strip()

    # 1. Presença de Site (Verificado)
    if not website or wtype == "none":
        score += 32
        verified_facts.append("Sem site próprio listado na ficha do Google Maps")
        score_reasons.append({"points": 32, "type": "verified", "label": "Não possui site próprio (oportunidade direta para Biossite / Landing Page)"})
    elif wtype in ("social", "directory"):
        score += 24
        verified_facts.append(f"Usa apenas link de rede social ou diretório ({website[:40]})")
        score_reasons.append({"points": 24, "type": "verified", "label": "Usa apenas Instagram/Linktree/Diretório no lugar de site próprio"})
    else:
        score += 8
        verified_facts.append(f"Possui site próprio ({website[:40]})")
        score_reasons.append({"points": 8, "type": "verified", "label": "Possui site próprio (foco em GMN / Plaquinha NFC / Automação)"})

    # 2. Canal de Contato / WhatsApp (Verificado + Heurístico)
    if clean_phone:
        if wa_verified == 1:
            score += 28
            verified_facts.append(f"WhatsApp confirmado ativo ({lead.get('phone') or clean_phone})")
            score_reasons.append({"points": 28, "type": "verified", "label": "Número verificado como ativo no WhatsApp"})
        elif phone_type == "mobile" or (len(clean_phone) == 13 and clean_phone[4] == "9"):
            score += 24
            verified_facts.append(f"Telefone celular comercial ({lead.get('phone') or clean_phone})")
            score_reasons.append({"points": 24, "type": "verified", "label": "Celular comercial de 11 dígitos (alta probabilidade de WhatsApp)"})
        elif is_wa or phone_type == "fixed":
            score += 16
            verified_facts.append(f"Telefone fixo comercial ({lead.get('phone') or clean_phone})")
            score_reasons.append({"points": 16, "type": "heuristic", "label": "Telefone fixo comercial (Elegível para WhatsApp Business ou ligação)"})

    # 3. Avaliações e Nota no Google (Verificado)
    if reviews == 0 and rating == 0:
        score += 20
        verified_facts.append("Ficha sem avaliações visíveis ou recém-criada")
        score_reasons.append({"points": 20, "type": "verified", "label": "Pouca prova social no Google (oportunidade para GMN + Plaquinha NFC)"})
    elif reviews < 35 or (0 < rating < 4.5):
        score += 22
        verified_facts.append(f"Nota {rating:.1f}⭐ com {reviews} avaliações")
        score_reasons.append({"points": 22, "type": "verified", "label": f"Volume baixo de avaliações ({reviews}) ou nota ({rating:.1f}⭐) — precisa de Plaquinha NFC e GMN"})
    elif reviews < 100 or rating < 4.8:
        score += 14
        verified_facts.append(f"Nota {rating:.1f}⭐ com {reviews} avaliações")
        score_reasons.append({"points": 14, "type": "verified", "label": f"Negócio ativo ({reviews} avaliações) com espaço para dominar o Top 3 local"})
    else:
        score += 10
        verified_facts.append(f"Forte reputação: {rating:.1f}⭐ ({reviews} avaliações)")
        score_reasons.append({"points": 10, "type": "verified", "label": f"Empresa consolidada ({reviews} avaliações) — potencial para automação e atendimento"})

    # 4. Categoria & Dados Comerciais Completos (Heurístico)
    if category:
        score += 10
        verified_facts.append(f"Categoria: {category}")
        cat_low = category.lower()
        if any(k in cat_low for k in FOOD_KEYWORDS):
            score += 8
            score_reasons.append({"points": 18, "type": "heuristic", "label": f"Nicho de gastronomia ({category}) — aderência a Cardápio Digital + NFC"})
        else:
            score_reasons.append({"points": 10, "type": "verified", "label": f"Segmento comercial identificado ({category})"})

    if address:
        score += 8
        verified_facts.append(f"Endereço: {address}")
        score_reasons.append({"points": 8, "type": "verified", "label": "Endereço físico localizado para abordagem regional"})

    final_score = max(5, min(100, score))
    if final_score >= 70:
        level = "alta"
        level_label = "Alta Oportunidade"
    elif final_score >= 45:
        level = "media"
        level_label = "Média Oportunidade"
    else:
        level = "baixa"
        level_label = "Baixa Oportunidade"

    return {
        "lead_score": final_score,
        "opportunity_level": level,
        "opportunity_label": level_label,
        "verified_facts": verified_facts,
        "score_reasons": score_reasons,
    }


def recommend_next_action(lead: Dict[str, Any]) -> Dict[str, str]:
    """P1.3 — Recomenda a próxima ação comercial com base no estágio atual do lead no CRM."""
    status = (lead.get("crm_status") or "novo").lower()
    next_fu = (lead.get("next_followup_at") or "").strip()
    today = datetime.now().strftime("%Y-%m-%d")

    if next_fu and next_fu[:10] <= today and status not in ("fechado", "perdido", "sem_whatsapp"):
        return {
            "code": "followup_due",
            "label": "Executar Follow-up Agendado Hoje",
            "priority": "urgent",
        }
    if status == "novo" and not lead.get("had_contact"):
        return {
            "code": "first_contact",
            "label": "Enviar 1ª Abordagem Quebra-Gelo",
            "priority": "high",
        }
    if status == "contatado" and not lead.get("had_reply"):
        return {
            "code": "schedule_followup",
            "label": "Enviar Follow-up de Diagnóstico (24h–48h)",
            "priority": "medium",
        }
    if status == "respondeu" or lead.get("had_reply"):
        return {
            "code": "send_proposal",
            "label": "Apresentar Prévia / Proposta Comercial",
            "priority": "urgent",
        }
    if status == "negociando":
        return {
            "code": "close_deal",
            "label": "Contornar Objeção e Fechar Venda",
            "priority": "urgent",
        }
    if status == "fechado":
        return {
            "code": "upsell",
            "label": "Oferecer Recorrência / Upsell em 15 dias",
            "priority": "low",
        }
    return {
        "code": "review",
        "label": "Revisar Ficha do Lead",
        "priority": "low",
    }


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
    except Exception:
        pass

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
        ("brand_logo_url", "TEXT DEFAULT ''"),
        ("brand_color", "TEXT DEFAULT '#2563eb'"),
        ("brand_phone", "TEXT DEFAULT ''"),
        ("brand_tagline", "TEXT DEFAULT ''"),
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
        external_id TEXT DEFAULT '',
        plan TEXT DEFAULT '',
        amount_brl REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    for col_name, col_type in [
        ("external_id", "TEXT DEFAULT ''"),
        ("plan", "TEXT DEFAULT ''"),
        ("amount_brl", "REAL DEFAULT 0.0"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE billing_events ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass

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
        ("next_followup_at", "TEXT DEFAULT ''"),
        ("followup_note", "TEXT DEFAULT ''"),
        ("last_interaction_at", "TEXT DEFAULT ''"),
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
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_user_phone ON leads(user_id, clean_phone)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_user_crm ON leads(user_id, crm_status, had_contact, had_reply)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_user_followup ON leads(user_id, next_followup_at)")
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
        script_followup TEXT DEFAULT '',
        proposal_script TEXT DEFAULT '',
        delivery_guide TEXT DEFAULT '',
        lessons_json TEXT DEFAULT '[]',
        pricing_tiers_json TEXT DEFAULT '[]',
        checklist_json TEXT DEFAULT '[]',
        target_opp TEXT DEFAULT '',
        sort_order INTEGER DEFAULT 0,
        is_published INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    for col_name, col_type in (
        ("script_followup", "TEXT DEFAULT ''"),
        ("proposal_script", "TEXT DEFAULT ''"),
        ("delivery_guide", "TEXT DEFAULT ''"),
        ("lessons_json", "TEXT DEFAULT '[]'"),
        ("pricing_tiers_json", "TEXT DEFAULT '[]'"),
        ("checklist_json", "TEXT DEFAULT '[]'"),
    ):
        try:
            cursor.execute(f"ALTER TABLE sales_academy_courses ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass
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

    # 10. Índices compostos adicionais (Fase 1.4)
    for idx_sql in (
        "CREATE INDEX IF NOT EXISTS idx_wa_messages_user_lead ON wa_messages(user_id, lead_id, id DESC)",
        "CREATE INDEX IF NOT EXISTS idx_wa_messages_user_phone ON wa_messages(user_id, phone, direction)",
        "CREATE INDEX IF NOT EXISTS idx_search_history_user ON search_history(user_id, id DESC)",
        "CREATE INDEX IF NOT EXISTS idx_users_signup_ip ON users(signup_ip, created_at)",
        "CREATE INDEX IF NOT EXISTS idx_billing_events_ext ON billing_events(external_id)",
    ):
        try:
            cursor.execute(idx_sql)
        except Exception:
            pass

    # 11. P0.1 — Onboarding Inteligente por Usuário
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_onboarding (
        user_id INTEGER PRIMARY KEY,
        step_welcome INTEGER DEFAULT 0,
        step_first_search INTEGER DEFAULT 0,
        step_view_lead INTEGER DEFAULT 0,
        step_crm INTEGER DEFAULT 0,
        step_first_contact INTEGER DEFAULT 0,
        dismissed INTEGER DEFAULT 0,
        completed_at TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 12. P0.3 — Analytics e Rastreamento de Eventos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analytics_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 0,
        event_name TEXT NOT NULL,
        metadata TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_user_event ON analytics_events(user_id, event_name, created_at)")

    # 13. P0.4 — Sequência Automática de Ativação
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activation_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trigger_key TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        enabled INTEGER DEFAULT 1,
        delay_hours INTEGER DEFAULT 1,
        channel TEXT DEFAULT 'in_app_and_wa',
        message_template TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        trigger_key TEXT NOT NULL,
        channel TEXT DEFAULT 'in_app',
        status TEXT DEFAULT 'sent',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, trigger_key)
    )
    """)
    _seed_activation_rules(cursor)

    # 14. P1.2 & P1.3 — Histórico de Interações do Lead e Uso do Copiloto IA
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lead_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        lead_id INTEGER NOT NULL,
        kind TEXT NOT NULL,
        summary TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lead_interactions_lead ON lead_interactions(user_id, lead_id, id DESC)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        lead_id INTEGER DEFAULT 0,
        action_type TEXT NOT NULL,
        provider TEXT DEFAULT 'heuristic',
        tokens_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_usage_user_date ON ai_usage_logs(user_id, created_at)")

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
            """
            SELECT id, name, email, company_name, role, plan, is_active,
                   subscription_status, plan_expires_at, max_leads,
                   brand_logo_url, brand_color, brand_phone, brand_tagline,
                   created_at, last_login_at
            FROM users WHERE id = ?
            """,
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
    allowed = {
        "name", "email", "company_name", "role", "plan", "is_active",
        "subscription_status", "plan_expires_at", "max_leads",
        "billing_customer_id", "must_set_password", "verification_hint",
        "brand_logo_url", "brand_color", "brand_phone", "brand_tagline",
    }
    updates = []
    params = []
    for k, v in fields.items():
        if k in allowed:
            if k == "email":
                clean_email = str(v or "").strip().lower()
                if not clean_email or "@" not in clean_email:
                    continue
                v = clean_email
            elif k == "plan":
                v = normalize_plan_name(str(v or "trial"))
            elif k == "plan_expires_at":
                raw_exp = str(v or "").strip()
                if len(raw_exp) == 10 and raw_exp[4] == "-" and raw_exp[7] == "-":
                    raw_exp = f"{raw_exp}T23:59:59"
                v = raw_exp
            elif k in ("max_leads", "is_active", "must_set_password"):
                v = int(v)
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


def delete_user_admin(user_id: int) -> bool:
    """Remove definitivamente uma conta de assinante e seus dados associados."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        for tbl in (
            "leads", "search_history", "pitch_templates", "wa_messages",
            "wa_user_configs", "academy_progress", "sales_academy_progress",
            "user_onboarding", "lead_interactions", "activation_logs",
            "analytics_events", "ai_usage_logs"
        ):
            try:
                cur.execute(f"DELETE FROM {tbl} WHERE user_id = ?", (user_id,))
            except sqlite3.OperationalError:
                pass
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        if deleted:
            wa_root = os.environ.get("WA_AUTH_ROOT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "whatsapp_service", "auth_sessions")
            shutil.rmtree(os.path.join(wa_root, f"user_{user_id}"), ignore_errors=True)
        return deleted
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


def is_billing_event_processed(external_id: str) -> bool:
    if not external_id or not str(external_id).strip():
        return False
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM billing_events WHERE external_id = ? AND status IN ('created', 'renewed', 'expired') LIMIT 1", (str(external_id).strip(),))
        return cur.fetchone() is not None
    finally:
        conn.close()


def log_billing_event(
    gateway: str,
    event_type: str,
    email: str,
    status: str,
    details: str = "",
    external_id: str = "",
    plan: str = "",
    amount_brl: float = 0.0,
):
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO billing_events (gateway, event_type, email, status, details, external_id, plan, amount_brl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                gateway or "kiwify",
                event_type or "",
                email or "",
                status or "ok",
                details or "",
                (external_id or "").strip(),
                (plan or "").strip(),
                float(amount_brl or 0.0),
            )
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
        "ai_provider": os.environ.get("AI_PROVIDER", "auto"),
        "ai_api_key": os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY") or "",
        "oci_backup_par_url": os.environ.get("OCI_BACKUP_PAR_URL", ""),
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
                if "plan_starter_price" not in saved and saved.get("plan_pro_price") in ("R$ 37", "37"):
                    defaults["plan_starter_price"] = "R$ 37"
                    defaults["plan_pro_price"] = "R$ 79"
            except Exception:
                pass
        defaults["meta_app_secret"] = decrypt_secret(defaults.get("meta_app_secret", ""))
        defaults["ai_api_key"] = decrypt_secret(defaults.get("ai_api_key", ""))
        defaults["oci_backup_par_url"] = decrypt_secret(defaults.get("oci_backup_par_url", ""))
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
    for k in ("checkout_url", "checkout_pro_url", "plan_starter_price", "plan_pro_price", "support_whatsapp", "meta_app_id", "meta_embedded_config_id", "ai_provider"):
        if k in data:
            curr[k] = str(data[k] or "").strip()
    for sec_key in ("meta_app_secret", "ai_api_key", "oci_backup_par_url"):
        if sec_key in data:
            sec_val = str(data[sec_key] or "").strip()
            if not sec_val.startswith("••••"):
                curr[sec_key] = sec_val
    to_store = {
        k: (encrypt_secret(curr.get(k, "")) if k in ("meta_app_secret", "ai_api_key", "oci_backup_par_url") else curr.get(k, ""))
        for k in ("checkout_url", "checkout_pro_url", "plan_starter_price", "plan_pro_price", "support_whatsapp", "meta_app_id", "meta_app_secret", "meta_embedded_config_id", "ai_provider", "ai_api_key", "oci_backup_par_url")
    }
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
        if not row:
            return {"user_id": user_id, "mode": "web_1click"}
        d = dict(row)
        d["meta_access_token"] = decrypt_secret(d.get("meta_access_token") or "")
        return d
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
                val = encrypt_secret(str(v or "")) if k == "meta_access_token" and v else v
                updates.append(f"{k} = ?")
                params.append(val)
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


def _enrich_lead_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    d["opportunities"] = compute_lead_opportunities(d)
    score_info = compute_lead_score(d)
    d["lead_score"] = score_info["lead_score"]
    d["opportunity_level"] = score_info["opportunity_level"]
    d["opportunity_label"] = score_info["opportunity_label"]
    d["verified_facts"] = score_info["verified_facts"]
    d["score_reasons"] = score_info["score_reasons"]
    d["next_action"] = recommend_next_action(d)
    return d


def get_lead_by_id(lead_id: int, user_id: int = 1) -> Optional[Dict[str, Any]]:
    """Busca 1 lead diretamente por ID + user_id (O(1) via índice primário)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM leads WHERE id = ? AND user_id = ?", (int(lead_id), int(user_id)))
        row = cur.fetchone()
        if not row:
            return None
        return _enrich_lead_dict(dict(row))
    finally:
        conn.close()


def get_leads(
    user_id: int = 1,
    website_type: Optional[str] = None,
    crm_status: Optional[str] = None,
    opportunity: Optional[str] = None,
    opportunity_level: Optional[str] = None,
    followup_filter: Optional[str] = None,
    sort_by: Optional[str] = None,
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

    if followup_filter and followup_filter != "all":
        today = datetime.now().strftime("%Y-%m-%d")
        if followup_filter == "due":
            query += " AND next_followup_at != '' AND next_followup_at IS NOT NULL AND SUBSTR(next_followup_at, 1, 10) <= ? AND crm_status NOT IN ('fechado', 'perdido', 'sem_whatsapp')"
            params.append(today)
        elif followup_filter == "scheduled":
            query += " AND next_followup_at != '' AND next_followup_at IS NOT NULL"

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
        d = _enrich_lead_dict(dict(r))
        if opportunity and opportunity != "all" and opportunity not in d["opportunities"]:
            continue
        if opportunity_level and opportunity_level != "all" and d["opportunity_level"] != opportunity_level:
            continue
        leads.append(d)

    if sort_by == "lead_score":
        leads.sort(key=lambda x: (x.get("lead_score", 0), x.get("reviews_count") or 0, x.get("id", 0)), reverse=True)
    elif sort_by == "reviews":
        leads.sort(key=lambda x: (x.get("reviews_count") or 0, x.get("id", 0)), reverse=True)
    elif sort_by == "followup":
        leads.sort(key=lambda x: (0 if x.get("next_followup_at") else 1, x.get("next_followup_at") or "9999", -x.get("id", 0)))

    return leads


def update_lead(lead_id: int, fields: Dict[str, Any], user_id: Optional[int] = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    allowed = [
        "crm_status", "notes", "had_contact", "contact_date", "had_reply",
        "had_sale", "sale_value", "tags", "whatsapp_status", "product_interest",
        "next_followup_at", "followup_note", "last_interaction_at"
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


def cleanup_leads_by_criteria(user_id: int, mode: str = "sem_whatsapp", lead_ids: Optional[List[int]] = None) -> int:
    """Remove leads de uma coluna do Kanban ou critério de limpeza, liberando cota da conta."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if lead_ids and isinstance(lead_ids, list):
            clean_ids = [int(x) for x in lead_ids if str(x).isdigit()]
            if not clean_ids:
                return 0
            placeholders = ",".join("?" * len(clean_ids))
            cur.execute(f"SELECT id FROM leads WHERE user_id = ? AND id IN ({placeholders})", [user_id] + clean_ids)
            ids = [r[0] for r in cur.fetchall()]
        elif mode == "perdido":
            cur.execute("SELECT id FROM leads WHERE user_id = ? AND crm_status = 'perdido'", (user_id,))
            ids = [r[0] for r in cur.fetchall()]
        elif mode == "all_dead":
            cur.execute(
                """
                SELECT id FROM leads
                WHERE user_id = ? AND (crm_status IN ('sem_whatsapp', 'perdido')
                   OR whatsapp_status = 'sem_whatsapp' OR whatsapp_verified = -1
                   OR clean_phone IS NULL OR TRIM(clean_phone) = '')
                """,
                (user_id,)
            )
            ids = [r[0] for r in cur.fetchall()]
        elif mode in ("novo", "contatado", "respondeu", "negociacao", "fechado"):
            cur.execute("SELECT id FROM leads WHERE user_id = ? AND crm_status = ?", (user_id, mode))
            ids = [r[0] for r in cur.fetchall()]
        else:
            cur.execute(
                """
                SELECT id FROM leads
                WHERE user_id = ? AND (crm_status = 'sem_whatsapp'
                   OR whatsapp_status = 'sem_whatsapp' OR whatsapp_verified = -1
                   OR clean_phone IS NULL OR TRIM(clean_phone) = '')
                """,
                (user_id,)
            )
            ids = [r[0] for r in cur.fetchall()]

        if not ids:
            return 0
        placeholders = ",".join("?" * len(ids))
        cur.execute(f"DELETE FROM wa_messages WHERE user_id = ? AND lead_id IN ({placeholders})", [user_id] + ids)
        cur.execute(f"DELETE FROM lead_interactions WHERE user_id = ? AND lead_id IN ({placeholders})", [user_id] + ids)
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
    {
        "slug": "aula-06-score-ia",
        "module_name": "Módulo 4 · Inteligência & Fechamento",
        "title": "Aula 06 — Lead Score (0–100) e Copiloto de Vendas com IA",
        "description": "Priorize automaticamente os leads mais quentes pela pontuação real do Google Maps e use o Copiloto IA para analisar a empresa, sugerir a melhor oferta e gerar mensagens prontas em 1 clique.",
        "duration_text": "00:24",
        "video_url": "/static/video/lessons/aula-06-score-ia.mp4",
        "target_tab": "tab-crm",
        "sort_order": 6,
    },
    {
        "slug": "aula-07-proposta-pdf",
        "module_name": "Módulo 4 · Inteligência & Fechamento",
        "title": "Aula 07 — Gerando Diagnósticos & Propostas PDF com a Sua Marca (White-Label)",
        "description": "Configure sua logo, cor primária e WhatsApp em Minha Conta e gere propostas comerciais e diagnósticos executivos em PDF 100% com a identidade da sua agência para enviar no WhatsApp do empresário.",
        "duration_text": "00:24",
        "video_url": "/static/video/lessons/aula-07-proposta-pdf.mp4",
        "target_tab": "tab-settings",
        "sort_order": 7,
    },
    {
        "slug": "aula-08-resultados",
        "module_name": "Módulo 4 · Inteligência & Fechamento",
        "title": "Aula 08 — Follow-ups no CRM, Linha do Tempo e Painel de Resultados",
        "description": "Agende lembretes de follow-up dentro da ficha de cada empresa, registre interações no histórico e acompanhe sua conversão e faturamento acumulado na Visão Geral.",
        "duration_text": "00:24",
        "video_url": "/static/video/lessons/aula-08-resultados.mp4",
        "target_tab": "tab-dashboard",
        "sort_order": 8,
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
from sales_academy_curriculum import SALES_ACADEMY_CURRICULUM as DEFAULT_SALES_ACADEMY


def _seed_sales_academy_courses(cursor):
    for item in DEFAULT_SALES_ACADEMY:
        lessons_str = json.dumps(item.get("lessons") or [], ensure_ascii=False)
        pricing_str = json.dumps(item.get("pricing_tiers") or [], ensure_ascii=False)
        checklist_str = json.dumps(item.get("checklist") or [], ensure_ascii=False)
        cursor.execute(
            """
            INSERT OR IGNORE INTO sales_academy_courses (
                slug, strategy_key, badge_label, title, subtitle, ticket_range,
                thumbnail_url, course_video_url, course_duration,
                vsl_video_url, vsl_title, vsl_duration,
                script_approach, script_objections, script_followup, proposal_script,
                delivery_guide, lessons_json, pricing_tiers_json, checklist_json,
                target_opp, sort_order, is_published
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                item["slug"], item["strategy_key"], item["badge_label"], item["title"],
                item["subtitle"], item["ticket_range"], item["thumbnail_url"],
                item["course_video_url"], item["course_duration"],
                item["vsl_video_url"], item["vsl_title"], item["vsl_duration"],
                item["script_approach"], item["script_objections"],
                item.get("script_followup", ""), item.get("proposal_script", ""),
                item.get("delivery_guide", ""), lessons_str, pricing_str, checklist_str,
                item["target_opp"], item["sort_order"],
            ),
        )
        # Atualiza cursos padrão existentes que ainda não tinham o currículo completo de 5 aulas
        cursor.execute(
            """
            UPDATE sales_academy_courses
            SET badge_label = ?,
                title = ?,
                subtitle = ?,
                ticket_range = ?,
                thumbnail_url = ?,
                course_video_url = ?,
                course_duration = ?,
                vsl_video_url = ?,
                vsl_title = ?,
                vsl_duration = ?,
                script_approach = ?,
                script_objections = ?,
                script_followup = ?,
                proposal_script = ?,
                delivery_guide = ?,
                lessons_json = ?,
                pricing_tiers_json = ?,
                checklist_json = ?,
                target_opp = ?,
                sort_order = ?
            WHERE slug = ? AND (lessons_json IS NULL OR lessons_json = '' OR lessons_json = '[]')
            """,
            (
                item["badge_label"], item["title"], item["subtitle"], item["ticket_range"],
                item["thumbnail_url"], item["course_video_url"], item["course_duration"],
                item["vsl_video_url"], item["vsl_title"], item["vsl_duration"],
                item["script_approach"], item["script_objections"],
                item.get("script_followup", ""), item.get("proposal_script", ""),
                item.get("delivery_guide", ""), lessons_str, pricing_str, checklist_str,
                item["target_opp"], item["sort_order"], item["slug"],
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
            try:
                raw_lessons = json.loads(d.get("lessons_json") or "[]")
            except Exception:
                raw_lessons = []
            try:
                raw_pricing = json.loads(d.get("pricing_tiers_json") or "[]")
            except Exception:
                raw_pricing = []
            try:
                raw_checklist = json.loads(d.get("checklist_json") or "[]")
            except Exception:
                raw_checklist = []

            if not unlocked and not include_unpublished:
                d["course_video_url"] = ""
                d["vsl_video_url"] = ""
                d["download_url"] = ""
                d["delivery_guide"] = ""
                d["script_followup"] = ""
                d["proposal_script"] = ""
                d["lessons"] = [
                    {
                        "num": l.get("num"),
                        "module": l.get("module"),
                        "title": l.get("title"),
                        "duration": l.get("duration"),
                        "summary": l.get("summary"),
                        "content_html": "",
                    }
                    for l in raw_lessons
                ]
                d["pricing_tiers"] = raw_pricing
                d["checklist"] = raw_checklist
            else:
                d["download_url"] = f"/api/sales-academy/download/{d['slug']}"
                d["lessons"] = raw_lessons
                d["pricing_tiers"] = raw_pricing
                d["checklist"] = raw_checklist
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
        script_followup = (data.get("script_followup") or "").strip()
        proposal_script = (data.get("proposal_script") or "").strip()
        delivery_guide = (data.get("delivery_guide") or "").strip()
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
                    script_approach=?, script_objections=?, script_followup=?,
                    proposal_script=?, delivery_guide=?, target_opp=?,
                    sort_order=?, is_published=?
                WHERE id=?
                """,
                (
                    strategy_key, badge_label, title, subtitle, ticket_range,
                    thumbnail_url, course_video_url, course_duration,
                    vsl_video_url, vsl_title, vsl_duration,
                    script_approach, script_objections, script_followup,
                    proposal_script, delivery_guide, target_opp,
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
                script_approach, script_objections, script_followup,
                proposal_script, delivery_guide, target_opp, sort_order, is_published
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                slug, strategy_key, badge_label, title, subtitle, ticket_range,
                thumbnail_url, course_video_url, course_duration,
                vsl_video_url, vsl_title, vsl_duration,
                script_approach, script_objections, script_followup,
                proposal_script, delivery_guide, target_opp, sort_order, is_published,
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


# ==================== P0.1 — ONBOARDING INTELIGENTE ====================

def get_user_onboarding(user_id: int) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM user_onboarding WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT OR IGNORE INTO user_onboarding (user_id) VALUES (?)", (user_id,))
            conn.commit()
            cur.execute("SELECT * FROM user_onboarding WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
        d = dict(row) if row else {
            "user_id": user_id,
            "step_welcome": 0,
            "step_first_search": 0,
            "step_view_lead": 0,
            "step_crm": 0,
            "step_first_contact": 0,
            "dismissed": 0,
            "completed_at": "",
        }

        # Sincroniza automaticamente com o progresso real que o usuário já fez no banco
        cur.execute("SELECT COUNT(*) FROM search_history WHERE user_id = ?", (user_id,))
        has_search = (cur.fetchone()[0] or 0) > 0
        cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ?", (user_id,))
        has_leads = (cur.fetchone()[0] or 0) > 0
        cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND crm_status != 'novo'", (user_id,))
        has_crm = (cur.fetchone()[0] or 0) > 0
        cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND had_contact = 1", (user_id,))
        has_contact = (cur.fetchone()[0] or 0) > 0

        dirty = False
        if (has_search or has_leads) and not d.get("step_first_search"):
            d["step_first_search"] = 1
            dirty = True
        if has_crm and not d.get("step_crm"):
            d["step_crm"] = 1
            dirty = True
        if has_contact and not d.get("step_first_contact"):
            d["step_first_contact"] = 1
            dirty = True

        steps_done = sum(1 for k in ("step_welcome", "step_first_search", "step_view_lead", "step_crm", "step_first_contact") if d.get(k))
        if steps_done == 5 and not d.get("completed_at"):
            d["completed_at"] = datetime.now().isoformat()
            dirty = True

        if dirty:
            cur.execute(
                """
                UPDATE user_onboarding SET
                    step_first_search = ?, step_crm = ?, step_first_contact = ?,
                    completed_at = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (
                    int(d["step_first_search"]),
                    int(d["step_crm"]),
                    int(d["step_first_contact"]),
                    d.get("completed_at") or "",
                    datetime.now().isoformat(),
                    user_id,
                )
            )
            conn.commit()

        d["steps_completed"] = steps_done
        d["total_steps"] = 5
        d["percent"] = int(round((steps_done / 5) * 100))
        d["is_completed"] = steps_done >= 5
        d["dismissed"] = bool(d.get("dismissed"))
        return d
    finally:
        conn.close()


def update_user_onboarding(user_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
    curr = get_user_onboarding(user_id)
    allowed = ("step_welcome", "step_first_search", "step_view_lead", "step_crm", "step_first_contact", "dismissed")
    updates = []
    params = []
    if fields.get("reset"):
        for k in allowed:
            updates.append(f"{k} = ?")
            params.append(0)
        updates.append("completed_at = ?")
        params.append("")
        track_event(user_id, "onboarding_started", {"restarted": True})
    else:
        for k in allowed:
            if k in fields:
                updates.append(f"{k} = ?")
                params.append(1 if fields[k] else 0)
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(user_id)
        conn = get_connection()
        try:
            conn.execute(f"UPDATE user_onboarding SET {', '.join(updates)} WHERE user_id = ?", params)
            conn.commit()
        finally:
            conn.close()
    res = get_user_onboarding(user_id)
    if res.get("is_completed") and not curr.get("is_completed"):
        track_event(user_id, "onboarding_completed")
    return res


# ==================== P0.3 — ANALYTICS & EVENTOS ====================

def track_event(user_id: Optional[int], event_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Registra evento de produto/conversão sem armazenar conversas privadas ou dados sensíveis."""
    if not event_name:
        return
    uid = int(user_id or 0)
    meta_str = json.dumps(metadata or {}, ensure_ascii=False) if metadata else ""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO analytics_events (user_id, event_name, metadata, created_at) VALUES (?, ?, ?, ?)",
            (uid, event_name.strip(), meta_str, datetime.now().isoformat())
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


# ==================== P0.4 — SEQUÊNCIA AUTOMÁTICA DE ATIVAÇÃO ====================

DEFAULT_ACTIVATION_RULES = [
    {
        "trigger_key": "signup_no_search",
        "name": "Cadastro sem 1ª Busca (2h)",
        "description": "Dispara quando o usuário cria a conta mas ainda não realizou a primeira busca no Google Maps.",
        "delay_hours": 2,
        "channel": "in_app_and_wa",
        "message_template": "Olá, {nome}! Sua conta no MapaLeads PRO já está liberada com 25 leads grátis. Que tal fazer sua 1ª busca na sua cidade agora em 30 segundos?",
    },
    {
        "trigger_key": "first_search_done",
        "name": "1ª Busca Concluída",
        "description": "Orienta o usuário a filtrar empresas sem site ou com poucas avaliações após sua primeira varredura.",
        "delay_hours": 0,
        "channel": "in_app",
        "message_template": "Parabéns pela 1ª busca, {nome}! Dica: ordene por Maior Lead Score para abordar primeiro as empresas com Alta Oportunidade.",
    },
    {
        "trigger_key": "first_lead_saved",
        "name": "Primeiro Lead Salvo / Movido no CRM",
        "description": "Incentiva o envio do 1º Quebra-Gelo no WhatsApp quando o usuário começa a usar o CRM.",
        "delay_hours": 0,
        "channel": "in_app",
        "message_template": "Excelente, {nome}! Use o Copiloto IA na gaveta da empresa para gerar um Quebra-Gelo personalizado em 1 clique.",
    },
    {
        "trigger_key": "near_lead_limit",
        "name": "Próximo do Limite de Leads (80%+)",
        "description": "Avisa quando o usuário atingiu 80% da franquia de leads do plano atual.",
        "delay_hours": 0,
        "channel": "in_app_and_wa",
        "message_template": "Atenção, {nome}: você já utilizou mais de 80% do limite de leads do seu plano ({leads_count}/{max_leads}). Faça upgrade para continuar prospectando sem pausas!",
    },
    {
        "trigger_key": "user_inactive_3d",
        "name": "Usuário Inativo há 3+ Dias",
        "description": "Reengaja assinantes que não acessam a plataforma há mais de 3 dias.",
        "delay_hours": 72,
        "channel": "in_app_and_wa",
        "message_template": "Oi, {nome}! Novas empresas abrem toda semana na sua região. Volte ao MapaLeads PRO e descubra oportunidades frescas hoje!",
    },
    {
        "trigger_key": "subscription_expiring_3d",
        "name": "Assinatura Próxima do Vencimento (≤ 3 dias)",
        "description": "Lembra o usuário que o período de acesso vence nos próximos 3 dias.",
        "delay_hours": 0,
        "channel": "in_app_and_wa",
        "message_template": "Olá, {nome}! Seu acesso ao plano {plano} vence em {dias_restantes} dia(s). Renove agora para manter seu CRM e suas buscas ativas!",
    },
    {
        "trigger_key": "payment_refused",
        "name": "Pagamento Recusado / Atrasado",
        "description": "Acionado quando o gateway reporta falha ou atraso na renovação.",
        "delay_hours": 0,
        "channel": "in_app_and_wa",
        "message_template": "Olá, {nome}! Identificamos uma pendência na renovação da sua assinatura do MapaLeads PRO. Regularize em 1 minuto para não pausar suas buscas.",
    },
]


def _seed_activation_rules(cursor):
    for r in DEFAULT_ACTIVATION_RULES:
        cursor.execute(
            """
            INSERT OR IGNORE INTO activation_rules (trigger_key, name, description, enabled, delay_hours, channel, message_template)
            VALUES (?, ?, ?, 1, ?, ?, ?)
            """,
            (r["trigger_key"], r["name"], r["description"], r["delay_hours"], r["channel"], r["message_template"]),
        )


def get_activation_rules() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT r.*,
                   (SELECT COUNT(*) FROM activation_logs l WHERE l.trigger_key = r.trigger_key) AS triggered_count
            FROM activation_rules r
            ORDER BY r.id ASC
        """)
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            d["enabled"] = bool(d.get("enabled"))
            rows.append(d)
        return rows
    finally:
        conn.close()


def save_activation_rule(trigger_key: str, data: Dict[str, Any]) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE activation_rules SET
                enabled = ?,
                delay_hours = ?,
                channel = ?,
                message_template = ?,
                updated_at = ?
            WHERE trigger_key = ?
            """,
            (
                1 if data.get("enabled", True) else 0,
                int(data.get("delay_hours", 0)),
                (data.get("channel") or "in_app_and_wa").strip(),
                (data.get("message_template") or "").strip(),
                datetime.now().isoformat(),
                trigger_key,
            )
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def evaluate_user_activations(user_id: int) -> List[Dict[str, Any]]:
    """
    Avalia os gatilhos de ativação para o usuário logado e retorna avisos ativos (in-app),
    registrando em activation_logs quando um novo gatilho é acionado.
    """
    user = get_user_by_id(user_id)
    if not user:
        return []
    acc = get_user_access_status(user_id)
    rules = {r["trigger_key"]: r for r in get_activation_rules() if r.get("enabled")}
    if not rules:
        return []

    conn = get_connection()
    cur = conn.cursor()
    notifications: List[Dict[str, Any]] = []
    try:
        cur.execute("SELECT COUNT(*) FROM search_history WHERE user_id = ?", (user_id,))
        searches_cnt = int(cur.fetchone()[0] or 0)
        cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ?", (user_id,))
        leads_cnt = int(cur.fetchone()[0] or 0)
        cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND (crm_status != 'novo' OR had_contact = 1)", (user_id,))
        crm_cnt = int(cur.fetchone()[0] or 0)

        active_triggers = []
        if searches_cnt == 0 and leads_cnt == 0 and "signup_no_search" in rules:
            active_triggers.append("signup_no_search")
        elif searches_cnt >= 1 and crm_cnt == 0 and "first_search_done" in rules:
            active_triggers.append("first_search_done")
        elif crm_cnt >= 1 and "first_lead_saved" in rules:
            cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND had_contact = 1", (user_id,))
            if (cur.fetchone()[0] or 0) == 0:
                active_triggers.append("first_lead_saved")

        max_l = int(acc.get("max_leads") or 0)
        if max_l > 0 and leads_cnt >= int(max_l * 0.8) and "near_lead_limit" in rules:
            active_triggers.append("near_lead_limit")

        days_left = int(acc.get("days_left") or 999)
        if 0 < days_left <= 3 and user.get("role") != "admin" and "subscription_expiring_3d" in rules:
            active_triggers.append("subscription_expiring_3d")

        for tkey in active_triggers:
            rule = rules[tkey]
            msg = (rule["message_template"] or "") \
                .replace("{nome}", user.get("name") or "Assinante") \
                .replace("{plano}", (user.get("plan") or "trial").upper()) \
                .replace("{leads_count}", str(leads_cnt)) \
                .replace("{max_leads}", str(max_l)) \
                .replace("{dias_restantes}", str(days_left))
            cur.execute(
                "INSERT OR IGNORE INTO activation_logs (user_id, trigger_key, channel, status, created_at) VALUES (?, ?, ?, 'shown', ?)",
                (user_id, tkey, rule.get("channel", "in_app"), datetime.now().isoformat())
            )
            notifications.append({
                "trigger_key": tkey,
                "title": rule["name"],
                "message": msg,
            })
        conn.commit()
        return notifications
    finally:
        conn.close()


# ==================== P0.2 — PAINEL ADMINISTRATIVO SAAS COMPLETO ====================

def _parse_brl_price(raw_price: str, fallback: float) -> float:
    if not raw_price:
        return fallback
    cleaned = "".join(c for c in str(raw_price).replace(",", ".") if c.isdigit() or c == ".")
    try:
        return float(cleaned) if cleaned else fallback
    except Exception:
        return fallback


def get_admin_saas_analytics(
    period: str = "30d",
    plan_filter: str = "all",
    status_filter: str = "all",
    search_q: str = "",
) -> Dict[str, Any]:
    """
    Calcula todos os indicadores financeiros, de retenção, funil e uso do SaaS
    usando exclusivamente dados reais do SQLite (sem dados fictícios).
    """
    days_map = {"7d": 7, "30d": 30, "90d": 90, "all": 36500}
    days_window = days_map.get((period or "30d").lower(), 30)
    cutoff_dt = datetime.now() - timedelta(days=days_window)
    cutoff_iso = cutoff_dt.isoformat()
    cutoff_7d = (datetime.now() - timedelta(days=7)).isoformat()

    settings = get_site_settings()
    price_starter = _parse_brl_price(settings.get("plan_starter_price", "37"), 37.0)
    price_pro = _parse_brl_price(settings.get("plan_pro_price", "79"), 79.0)
    price_enterprise = 197.0

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT u.*,
                   (SELECT COUNT(*) FROM leads l WHERE l.user_id = u.id) AS leads_count,
                   (SELECT COUNT(*) FROM leads l WHERE l.user_id = u.id AND l.created_at >= ?) AS leads_period_count,
                   (SELECT COUNT(*) FROM search_history s WHERE s.user_id = u.id) AS searches_count,
                   (SELECT COUNT(*) FROM wa_messages m WHERE m.user_id = u.id AND m.direction = 'out') AS messages_sent_count
            FROM users u
            ORDER BY u.id DESC
        """, (cutoff_iso,))
        all_users = [dict(r) for r in cur.fetchall()]

        now = datetime.now()
        total_users = 0
        active_users = 0
        new_signups_period = 0
        paying_subscribers = 0
        free_trial_users = 0
        canceled_subscriptions = 0
        overdue_expired_subscriptions = 0
        inactive_users_7d = 0
        mrr_brl = 0.0
        plan_distribution = {"trial": 0, "starter": 0, "pro": 0, "enterprise": 0}
        activated_users = 0  # Fez pelo menos 1 busca ou salvou pelo menos 1 lead

        filtered_users = []
        for u in all_users:
            u.pop("password_hash", None)
            is_admin = (u.get("role") == "admin")
            plan_norm = normalize_plan_name(u.get("plan"))
            sub = (u.get("subscription_status") or "active").lower()
            exp_str = (u.get("plan_expires_at") or "").strip()

            is_expired_by_date = False
            if exp_str:
                try:
                    if datetime.fromisoformat(exp_str) <= now:
                        is_expired_by_date = True
                except Exception:
                    pass

            if not u.get("is_active") or sub in ("canceled", "cancelled"):
                effective_status = "canceled"
            elif sub in ("expired", "suspended", "overdue") or is_expired_by_date:
                effective_status = "expired"
            elif plan_norm == "trial" or sub == "trial":
                effective_status = "trial"
            else:
                effective_status = "active"

            u["effective_status"] = effective_status
            u["plan_normalized"] = plan_norm

            if not is_admin:
                total_users += 1
                plan_distribution[plan_norm] = plan_distribution.get(plan_norm, 0) + 1

                created_str = (u.get("created_at") or "").replace(" ", "T")
                if created_str >= cutoff_iso:
                    new_signups_period += 1

                last_login = (u.get("last_login_at") or created_str or "").replace(" ", "T")
                if last_login and last_login < cutoff_7d:
                    inactive_users_7d += 1

                if (u.get("searches_count") or 0) > 0 or (u.get("leads_count") or 0) > 0:
                    activated_users += 1

                if effective_status == "active":
                    active_users += 1
                    paying_subscribers += 1
                    if plan_norm == "starter":
                        mrr_brl += price_starter
                    elif plan_norm == "pro":
                        mrr_brl += price_pro
                    elif plan_norm == "enterprise":
                        mrr_brl += price_enterprise
                elif effective_status == "trial":
                    active_users += 1
                    free_trial_users += 1
                elif effective_status == "canceled":
                    canceled_subscriptions += 1
                elif effective_status == "expired":
                    overdue_expired_subscriptions += 1

            # Aplica filtros da tabela Admin
            if plan_filter and plan_filter != "all" and plan_norm != plan_filter:
                continue
            if status_filter and status_filter != "all" and effective_status != status_filter:
                continue
            if search_q:
                q_low = search_q.strip().lower()
                hay = f"{u.get('name','')} {u.get('email','')} {u.get('company_name','')}".lower()
                if q_low not in hay:
                    continue
            filtered_users.append(u)

        # Receita acumulada real registrada nos eventos de billing (ou soma dos planos pagos aprovados)
        cur.execute("SELECT * FROM billing_events ORDER BY id DESC LIMIT 50")
        billing_rows = [dict(r) for r in cur.fetchall()]

        cur.execute("""
            SELECT COUNT(*), COALESCE(SUM(amount_brl), 0.0)
            FROM billing_events
            WHERE status IN ('created', 'renewed', 'approved', 'paid')
        """)
        b_cnt, b_sum = cur.fetchone()
        accumulated_revenue = float(b_sum or 0.0)
        if accumulated_revenue == 0.0 and paying_subscribers > 0:
            # Se eventos antigos não tinham amount_brl gravado, reflete pelo menos o MRR vigente comprovado
            accumulated_revenue = mrr_brl

        # Consumo de buscas e leads no período
        cur.execute("SELECT COUNT(*) FROM search_history WHERE created_at >= ?", (cutoff_iso[:19].replace("T", " "),))
        searches_period = int(cur.fetchone()[0] or 0)
        cur.execute("SELECT COUNT(*) FROM search_history")
        searches_total = int(cur.fetchone()[0] or 0)
        cur.execute("SELECT COUNT(*) FROM leads")
        leads_total = int(cur.fetchone()[0] or 0)

        # Taxas reais de conversão e churn
        conversion_trial_to_paid = round((paying_subscribers / total_users) * 100, 1) if total_users > 0 else 0.0
        activation_rate = round((activated_users / total_users) * 100, 1) if total_users > 0 else 0.0
        total_ever_paid = paying_subscribers + canceled_subscriptions
        churn_rate = round((canceled_subscriptions / total_ever_paid) * 100, 1) if total_ever_paid > 0 else 0.0

        # Funil de Eventos P0.3
        cur.execute("""
            SELECT event_name, COUNT(*) AS total_events, COUNT(DISTINCT user_id) AS unique_users
            FROM analytics_events
            WHERE created_at >= ?
            GROUP BY event_name
        """, (cutoff_iso,))
        event_breakdown = {r["event_name"]: {"events": r["total_events"], "users": r["unique_users"]} for r in cur.fetchall()}

        cur.execute("SELECT * FROM analytics_events ORDER BY id DESC LIMIT 30")
        recent_analytics = [dict(r) for r in cur.fetchall()]

        return {
            "kpis": {
                "total_users": total_users,
                "active_users": active_users,
                "new_signups_period": new_signups_period,
                "paying_subscribers": paying_subscribers,
                "free_trial_users": free_trial_users,
                "canceled_subscriptions": canceled_subscriptions,
                "overdue_expired_subscriptions": overdue_expired_subscriptions,
                "inactive_users_7d": inactive_users_7d,
                "mrr_brl": round(mrr_brl, 2),
                "accumulated_revenue_brl": round(accumulated_revenue, 2),
                "conversion_trial_to_paid_pct": conversion_trial_to_paid,
                "activation_rate_pct": activation_rate,
                "churn_rate_pct": churn_rate,
                "searches_period": searches_period,
                "searches_total": searches_total,
                "leads_total": leads_total,
            },
            "plan_distribution": plan_distribution,
            "users": filtered_users,
            "billing_events": billing_rows,
            "event_breakdown": event_breakdown,
            "recent_analytics": recent_analytics,
        }
    finally:
        conn.close()


# ==================== P1.3 — FOLLOW-UPS & HISTÓRICO DE INTERAÇÕES NO CRM ====================

def add_lead_interaction(user_id: int, lead_id: int, kind: str, summary: str) -> int:
    now = datetime.now().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO lead_interactions (user_id, lead_id, kind, summary, created_at) VALUES (?, ?, ?, ?, ?)",
            (int(user_id), int(lead_id), (kind or "note").strip(), (summary or "").strip(), now)
        )
        cur.execute("UPDATE leads SET last_interaction_at = ?, updated_at = ? WHERE id = ? AND user_id = ?", (now, now, int(lead_id), int(user_id)))
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def get_lead_interactions(user_id: int, lead_id: int, limit: int = 40) -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT * FROM lead_interactions WHERE user_id = ? AND lead_id = ? ORDER BY id DESC LIMIT ?",
            (int(user_id), int(lead_id), int(limit))
        )
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def get_followup_agenda(user_id: int) -> Dict[str, Any]:
    """Retorna oportunidades que precisam de acompanhamento hoje/atrasadas e nos próximos dias."""
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT * FROM leads
            WHERE user_id = ?
              AND crm_status NOT IN ('fechado', 'perdido', 'sem_whatsapp')
              AND (
                  (next_followup_at IS NOT NULL AND next_followup_at != '')
                  OR (crm_status IN ('contatado', 'respondeu', 'negociando'))
              )
            ORDER BY
              CASE WHEN next_followup_at IS NOT NULL AND next_followup_at != '' THEN 0 ELSE 1 END ASC,
              next_followup_at ASC,
              id DESC
            LIMIT 100
        """, (int(user_id),))
        rows = [_enrich_lead_dict(dict(r)) for r in cur.fetchall()]
        due_today = []
        upcoming = []
        needs_attention = []
        for l in rows:
            nfu = (l.get("next_followup_at") or "").strip()
            if nfu:
                if nfu[:10] <= today:
                    due_today.append(l)
                else:
                    upcoming.append(l)
            elif l.get("crm_status") in ("respondeu", "negociando"):
                needs_attention.append(l)
        return {
            "due_today_count": len(due_today),
            "upcoming_count": len(upcoming),
            "needs_attention_count": len(needs_attention),
            "due_today": due_today[:25],
            "upcoming": upcoming[:25],
            "needs_attention": needs_attention[:25],
        }
    finally:
        conn.close()


# ==================== P1.4 — DASHBOARD DE RESULTADOS DO ASSINANTE ====================

def get_user_results_dashboard(user_id: int, period: str = "30d") -> Dict[str, Any]:
    """
    Painel individual de resultados reais do assinante por período (7d, 30d, 90d, all).
    Não utiliza estimativas como resultados reais.
    """
    days_map = {"7d": 7, "30d": 30, "90d": 90, "all": 36500}
    days_window = days_map.get((period or "30d").lower(), 30)
    cutoff_iso = (datetime.now() - timedelta(days=days_window)).isoformat()

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COALESCE(SUM(total_found), 0), COUNT(*) FROM search_history WHERE user_id = ? AND created_at >= ?", (user_id, cutoff_iso[:19].replace("T", " ")))
        r_search = cur.fetchone()
        leads_found_searches = int(r_search[0] or 0)
        searches_run = int(r_search[1] or 0)

        cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND created_at >= ?", (user_id, cutoff_iso))
        leads_saved = int(cur.fetchone()[0] or 0)

        cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND crm_status != 'novo' AND updated_at >= ?", (user_id, cutoff_iso))
        in_crm = int(cur.fetchone()[0] or 0)

        cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND had_contact = 1 AND updated_at >= ?", (user_id, cutoff_iso))
        contacts_made = int(cur.fetchone()[0] or 0)

        cur.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND (had_reply = 1 OR crm_status IN ('respondeu', 'negociando')) AND updated_at >= ?", (user_id, cutoff_iso))
        in_progress = int(cur.fetchone()[0] or 0)

        cur.execute("SELECT COUNT(*), COALESCE(SUM(sale_value), 0.0) FROM leads WHERE user_id = ? AND (had_sale = 1 OR crm_status = 'fechado') AND updated_at >= ?", (user_id, cutoff_iso))
        r_sales = cur.fetchone()
        closed_sales = int(r_sales[0] or 0)
        closed_revenue = float(r_sales[1] or 0.0)

        # Se leads_found_searches for menor que leads_saved (buscas antigas), ajusta ao mínimo real salvo
        if leads_found_searches < leads_saved:
            leads_found_searches = leads_saved

        reply_rate_pct = round((in_progress / contacts_made) * 100, 1) if contacts_made > 0 else 0.0
        sales_conversion_pct = round((closed_sales / contacts_made) * 100, 1) if contacts_made > 0 else 0.0

        # Série histórica diária (últimos 7 pontos do período) para gráfico
        cur.execute("""
            SELECT SUBSTR(created_at, 1, 10) AS day,
                   COUNT(*) AS leads_saved,
                   SUM(CASE WHEN had_contact = 1 THEN 1 ELSE 0 END) AS contacted,
                   SUM(CASE WHEN had_sale = 1 OR crm_status = 'fechado' THEN 1 ELSE 0 END) AS sales
            FROM leads
            WHERE user_id = ? AND created_at >= ?
            GROUP BY SUBSTR(created_at, 1, 10)
            ORDER BY day ASC
            LIMIT 30
        """, (user_id, cutoff_iso))
        timeline = [dict(r) for r in cur.fetchall()]

        return {
            "period": period,
            "searches_run": searches_run,
            "leads_found": leads_found_searches,
            "leads_saved": leads_saved,
            "companies_in_crm": in_crm,
            "contacts_made": contacts_made,
            "opportunities_in_progress": in_progress,
            "closed_sales": closed_sales,
            "closed_revenue_brl": round(closed_revenue, 2),
            "reply_rate_pct": reply_rate_pct,
            "conversion_rate_pct": sales_conversion_pct,
            "timeline": timeline,
        }
    finally:
        conn.close()


# ==================== P1.2 — COPILOTO DE VENDAS COM IA ====================

AI_PLAN_DAILY_LIMITS = {
    "trial": 15,
    "starter": 60,
    "pro": 250,
    "enterprise": 2000,
}


def check_ai_quota(user_id: int) -> Dict[str, Any]:
    user = get_user_by_id(user_id)
    if not user:
        return {"allowed": False, "used_today": 0, "daily_limit": 0}
    if user.get("role") == "admin":
        return {"allowed": True, "used_today": 0, "daily_limit": 9999, "plan": "enterprise"}
    plan_norm = normalize_plan_name(user.get("plan"))
    daily_limit = AI_PLAN_DAILY_LIMITS.get(plan_norm, 15)
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM ai_usage_logs WHERE user_id = ? AND created_at LIKE ?", (user_id, f"{today}%"))
        used = int(cur.fetchone()[0] or 0)
        return {
            "allowed": used < daily_limit,
            "used_today": used,
            "daily_limit": daily_limit,
            "plan": plan_norm,
        }
    finally:
        conn.close()


def log_ai_usage(user_id: int, lead_id: int, action_type: str, provider: str = "heuristic", tokens_used: int = 0):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO ai_usage_logs (user_id, lead_id, action_type, provider, tokens_used, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (int(user_id), int(lead_id or 0), action_type, provider, int(tokens_used or 0), datetime.now().isoformat())
        )
        conn.commit()
    finally:
        conn.close()


def generate_ai_copilot_response(lead: Dict[str, Any], action: str) -> Dict[str, Any]:
    """
    Gera análise e scripts personalizados usando EXCLUSIVAMENTE os dados verificados disponíveis na ficha.
    Indica explicitamente quando algum dado (ex: site, nota, bairro) não está disponível.
    """
    name = (lead.get("name") or "Empresa").strip()
    cat = (lead.get("category") or "").strip()
    cat_label = cat if cat else "segmento não informado na ficha"
    loc = (lead.get("neighborhood") or lead.get("city") or lead.get("street") or "").strip()
    loc_label = loc if loc else "região local"
    rating = float(lead.get("rating") or 0.0)
    reviews = int(lead.get("reviews_count") or 0)
    wtype = (lead.get("website_type") or "none").lower()
    website = (lead.get("website") or "").strip()
    phone = (lead.get("phone") or lead.get("clean_phone") or "Não disponível").strip()

    score_data = compute_lead_score(lead)
    opps = compute_lead_opportunities(lead)

    # Identifica dados ausentes para transparência total
    missing_fields = []
    if not website or wtype == "none":
        missing_fields.append("Site próprio ausente na ficha do Google Maps")
    if not cat:
        missing_fields.append("Categoria principal não especificada")
    if rating == 0 and reviews == 0:
        missing_fields.append("Nota e contagem de avaliações não disponíveis na listagem")
    if not lead.get("neighborhood"):
        missing_fields.append("Bairro exato não detalhado (usando cidade/rua)")

    # Oferta principal recomendada com base nos dados reais
    is_food = any(k in cat.lower() for k in FOOD_KEYWORDS) if cat else False
    if is_food:
        best_offer = "Cardápio Digital Sem Taxas + Plaquinha NFC de Mesa"
        ticket = "R$ 297 de implementação + R$ 147/mês (ou R$ 197 por plaquinha NFC)"
        why_offer = f"Por atuar em gastronomia ({cat_label}), o maior ralo de margem são taxas de apps e demora no WhatsApp."
    elif not website or wtype in ("none", "social", "directory"):
        best_offer = "Combo Biossite Express (48h) + Otimização Google Meu Negócio"
        ticket = "R$ 497 a R$ 890 (setup único) + R$ 297/mês opcional"
        why_offer = "A empresa está no Google Maps mas não possui site oficial próprio para converter quem pesquisa no Google."
    elif reviews < 50 or (0 < rating < 4.7):
        best_offer = "Otimização Top 3 Google Meu Negócio + Plaquinha NFC de Avaliações 5⭐"
        ticket = "R$ 497 (Otimização GMN) + R$ 197 (Plaquinha NFC)"
        why_offer = f"Com {reviews} avaliações e nota {rating:.1f}⭐, destravar avaliações 5⭐ e SEO local multiplica ligações orgânicas."
    else:
        best_offer = "Estruturação de WhatsApp Business PRO & Catálogo + Plaquinha NFC"
        ticket = "R$ 590 a R$ 1.200"
        why_offer = f"Empresa consolidada ({reviews} avaliações) que precisa converter o alto fluxo de contatos no WhatsApp sem perder orçamentos."

    rating_str = f"{rating:.1f}⭐ ({reviews} avaliações)" if (rating > 0 or reviews > 0) else "sem nota/avaliações registradas"
    site_str = f"Ausente (tipo: {wtype})" if (not website or wtype == "none") else f"{website} ({wtype})"

    outputs = {
        "analyze": (
            f"📊 DIAGNÓSTICO COMERCIAL — {name}\n"
            f"• Lead Score: {score_data['lead_score']}/100 ({score_data['opportunity_label']})\n"
            f"• Dados Verificados na Ficha:\n"
            f"  - Segmento: {cat_label}\n"
            f"  - Localização: {loc_label}\n"
            f"  - Reputação Google: {rating_str}\n"
            f"  - Site Oficial: {site_str}\n"
            f"  - Telefone: {phone}\n\n"
            f"🎯 GARGALOS & OPORTUNIDADES DETECTADAS:\n"
            + "\n".join(f"  - [+{r['points']} pts] {r['label']}" for r in score_data["score_reasons"])
            + (f"\n\n⚠️ Dados ausentes/limitados na ficha: {'; '.join(missing_fields)}." if missing_fields else "")
            + f"\n\n💡 PRÓXIMO PASSO RECOMENDADO:\n  👉 {recommend_next_action(lead)['label']}"
        ),
        "suggest_product": (
            f"🏆 OFERTA PRINCIPAL RECOMENDADA PARA {name.upper()}:\n"
            f"👉 {best_offer}\n"
            f"💰 Ticket Sugerido: {ticket}\n"
            f"📌 Justificativa nos Dados: {why_offer}\n\n"
            f"🔄 OFERTAS SECUNDÁRIAS (UPSELL / DOWNSELL):\n"
            f"1) Entrada Rápida (Downsell): Plaquinha NFC + QR Code de Balcão (R$ 197) — encostou o celular, abriu Avaliação 5⭐ no Google ou Pix.\n"
            f"2) Recorrência Mensal (Upsell): Gestão Mensal de Google Meu Negócio + Relatório de Buscas (R$ 297 a R$ 497/mês)."
        ),
        "approach": (
            f"🎯 ESTRATÉGIA DE ABORDAGEM CONSULTIVA ({name}):\n\n"
            f"1. Ângulo de Entrada (Sem parecer vendedor): Comente sobre a ficha da {name} em {loc_label} no Google Maps.\n"
            f"2. Ponto de Alavanca: {'A ausência de um site rápido clicável na ficha' if (not website or wtype != 'own') else f'O potencial de multiplicar as {reviews} avaliações atuais para dominar o Top 3 local'}.\n"
            f"3. Pergunta de Qualificação:\n"
            f"   - 'Hoje, quando um cliente encontra a {name} no Google em {loc_label}, vocês têm um processo para transformar essa visita em orçamento no WhatsApp e pedir avaliação 5⭐?'\n"
            f"4. Argumento Comercial Central: Quem pesquisa por {cat_label} no Google Maps já tem intenção imediata de compra."
        ),
        "whatsapp": (
            f"💬 OPÇÃO 1 — QUEBRA-GELO CURTO (ANTI-BLOQUEIO / 1ª MENSAGEM):\n"
            f"\"Olá, pessoal da {name}! Tudo bem? Vi o perfil de vocês no Google aqui em {loc_label}. Posso tirar uma dúvida rápida com quem cuida do atendimento ou marketing aí?\"\n\n"
            f"💬 OPÇÃO 2 — APÓS O CLIENTE RESPONDER (DIAGNÓSTICO DE VALOR):\n"
            f"\"Obrigado pelo retorno! Analisei a ficha da {name} em {loc_label} e vi uma oportunidade rápida para vocês receberem mais contatos pelo Google {'criando uma página expressa ligada ao WhatsApp' if (not website or wtype != 'own') else 'destravando avaliações 5⭐ e posições no mapa'}. Posso te mandar uma prévia de 1 minuto sem compromisso?\""
        ),
        "call_script": (
            f"📞 ROTEIRO DE LIGAÇÃO (COLD CALL DE 45 SEGUNDOS) — {name}\n\n"
            f"[Abertura]: \"Bom dia/Boa tarde! Falo com o responsável pela {name}? Aqui é [Seu Nome], especialista em posicionamento no Google em {loc_label}.\"\n\n"
            f"[Gancho Baseado nos Dados]: \"Estava pesquisando por {cat_label} em {loc_label} no Google Maps e encontrei a ficha de vocês ({rating_str}). Notei que {'vocês ainda não têm um site rápido conectado ao botão da ficha' if (not website or wtype != 'own') else 'com 2 ajustes simples na ficha vocês conseguem capturar muito mais ligações da região'}.\"\n\n"
            f"[Perguntas de Qualificação]:\n"
            f"1) \"Hoje o Google Maps já é a principal fonte de clientes novos de vocês ou ainda dependem mais de indicação/Instagram?\"\n"
            f"2) \"Se eu montar um diagnóstico visual mostrando como ficar no topo de {loc_label}, consigo te enviar no WhatsApp {phone} para você avaliar em 2 minutos?\""
        ),
        "followup": (
            f"🔄 SEQUÊNCIA DE FOLLOW-UP & QUEBRA DE OBJEÇÕES — {name}\n\n"
            f"📅 Follow-up 1 (24h após 1º contato):\n"
            f"\"Oi, pessoal da {name}! Imagino a correria aí em {loc_label}. Separei aquela prévia rápida sobre a ficha de vocês no Google. Quer que eu mande o link por aqui mesmo?\"\n\n"
            f"📅 Follow-up 2 (72h — Fechamento suave):\n"
            f"\"Olá! Estou fechando a agenda de implementações de {cat_label} desta semana em {loc_label}. Ainda faz sentido conversarmos sobre aumentar os clientes vindos do Google ou prefere deixar para o próximo mês?\"\n\n"
            f"🛡️ RESPOSTAS PARA OBJEÇÕES COMUNS:\n"
            f"• \"Está caro / Não tenho verba agora\": \"Por isso começamos pelo setup enxuto: apenas 2 ou 3 clientes novos que encontrarem a {name} no Google já pagam 100% do investimento.\"\n"
            f"• \"Já tenho Instagram\": \"O Instagram é ótimo para quem já conhece vocês, mas quem digita '{cat_label} em {loc_label}' no Google quer comprar hoje. Nós unimos os dois canais.\""
        ),
    }

    selected_text = outputs.get(action) or outputs["analyze"]
    return {
        "success": True,
        "action": action,
        "provider": "verified_data_engine",
        "lead_id": lead.get("id"),
        "lead_name": name,
        "lead_score": score_data["lead_score"],
        "opportunity_level": score_data["opportunity_level"],
        "opportunity_label": score_data["opportunity_label"],
        "recommended_offer": best_offer,
        "missing_fields": missing_fields,
        "content": selected_text,
        "all_sections": outputs,
    }


init_db()
