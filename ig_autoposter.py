import os
import time
import textwrap
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

from curl_cffi import requests as cffi_requests
from PIL import Image, ImageDraw, ImageFont

from database import (
    DB_PATH,
    get_ig_config,
    save_ig_config,
    get_site_settings,
    list_ig_queue,
    mark_ig_queue_item_status,
    record_ig_history,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_BASE = "https://graph.facebook.com/v21.0"
BRT_TZ = timezone(timedelta(hours=-3))


def get_ig_media_dir() -> str:
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    path = os.path.join(db_dir, "ig_media")
    os.makedirs(path, exist_ok=True)
    return path


def _load_font(size: int, bold: bool = True):
    candidates = (
        [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
        ]
        if bold
        else [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
        ]
    )
    for fp in candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


# Banco rotativo de ideias para geração automática contínua + legendas otimizadas
DAILY_ANGLES: List[Dict[str, str]] = [
    {
        "topic": "Prospecção Google Maps",
        "kicker": "PROSPECÇÃO LOCAL",
        "headline": "Clientes prontos\nno Google Maps.",
        "sub": "Encontre empresas sem site e com poucas avaliações na sua cidade.",
        "badge": "Contatos reais + WhatsApp válido",
        "photo": "static/img/academy/gmn-hero.jpg",
        "accent": "#34d399",
        "caption": (
            "Você não precisa ficar esperando indicação para fechar novos clientes locais.\n\n"
            "O MapaLeads PRO varre ruas, bairros e cidades no Google Maps, detecta quem está sem site oficial ou com poucas avaliações e já entrega o WhatsApp pronto com abordagem.\n\n"
            "👉 Teste grátis por 24h no link da bio (mapaleadspro.online)!"
        ),
    },
    {
        "topic": "Google Meu Negócio",
        "kicker": "GOOGLE MEU NEGÓCIO",
        "headline": "Cobre R$ 400 a\nR$ 1.200 por perfil.",
        "sub": "Empresas da sua cidade perdem ligações todo dia por ficha desatualizada.",
        "badge": "Copy de abordagem + Curso no PRO",
        "photo": "static/img/academy/gmn-hero.jpg",
        "accent": "#60a5fa",
        "caption": (
            "O serviço mais rápido para vender esta semana: Otimização de Google Meu Negócio.\n\n"
            "Mostre para comércios do seu bairro como subir para o Top 3 do mapa e gerar ligações orgânicas todos os dias sem pagar anúncio.\n\n"
            "No MapaLeads PRO você já encontra os perfis desatualizados e recebe a copy pronta. Link na bio!"
        ),
    },
    {
        "topic": "Plaquinha NFC 5 Estrelas",
        "kicker": "PLAQUINHA NFC + QR",
        "headline": "Encostou o celular,\navaliou 5 estrelas.",
        "sub": "Oferta física irresistível de R$ 150 a R$ 350 para balcão e mesas.",
        "badge": "Produto de entrada de venda rápida",
        "photo": "static/img/academy/nfc-hero.jpg",
        "accent": "#c084fc",
        "caption": (
            "Todo dono de comércio entende o valor da Plaquinha NFC em 5 segundos.\n\n"
            "O cliente encosta o celular no caixa e já cai direto na tela de avaliação 5⭐ do Google ou Instagram.\n\n"
            "Filtre empresas com poucas avaliações no MapaLeads PRO e comece a ofertar hoje mesmo. Link na bio!"
        ),
    },
    {
        "topic": "WhatsApp Business + Chat",
        "kicker": "WHATSAPP + CRM",
        "headline": "Buscou.\nMandou. Vendeu.",
        "sub": "Scripts Quebra-Gelo anti-bloqueio + atendimento integrado estilo Kommo.",
        "badge": "Remove leads sem WhatsApp em 1 clique",
        "photo": "static/img/academy/whatsapp-hero.jpg",
        "accent": "#34d399",
        "caption": (
            "Chega de planilhas soltas e contatos inválidos que só consomem seu tempo.\n\n"
            "No MapaLeads PRO você capta o contato, limpa números sem WhatsApp em 1 clique, dispara o Quebra-Gelo e acompanha tudo no Kanban até o PIX cair.\n\n"
            "Experimente grátis por 24h em mapaleadspro.online!"
        ),
    },
    {
        "topic": "Cardápio Digital Sem Taxas",
        "kicker": "GASTRONOMIA LOCAL",
        "headline": "Chega de pagar\ntaxa de aplicativo.",
        "sub": "Venda Cardápio Digital com QR na mesa e pedidos direto no WhatsApp.",
        "badge": "Receita mensal recorrente na sua cidade",
        "photo": "static/img/academy/cardapio-hero.jpg",
        "accent": "#fbbf24",
        "caption": (
            "Pizzarias, bares e restaurantes deixam até 27% do faturamento em aplicativos de entrega.\n\n"
            "Filtre negócios de gastronomia na sua região pelo MapaLeads PRO e feche contratos recorrentes de Cardápio Digital + QR Code.\n\n"
            "Comece seu teste gratuito pelo link na bio!"
        ),
    },
    {
        "topic": "Biossite Express em 48h",
        "kicker": "EMPRESAS SEM SITE",
        "headline": "Negócio sem site\né dinheiro na mesa.",
        "sub": "Filtre exatamente quem só tem Instagram e feche páginas de R$ 400 a R$ 1.500.",
        "badge": "Filtro automático de oportunidades",
        "photo": "static/img/academy/biossite-hero.jpg",
        "accent": "#60a5fa",
        "caption": (
            "Milhares de empresas boas aparecem no Google sem nenhum site oficial clicável.\n\n"
            "O MapaLeads PRO separa essas empresas automaticamente e entrega a mensagem pronta para você enviar uma prévia e fechar em 48h.\n\n"
            "Teste agora em mapaleadspro.online!"
        ),
    },
    {
        "topic": "Plano PRO + Kit VSLs",
        "kicker": "PLANO PRO · R$ 79/MÊS",
        "headline": "2.000 Leads +\nCursos + VSLs.",
        "sub": "Acesse 5 cursos completos de vendas e baixe VSLs prontas para divulgar.",
        "badge": "Bônus exclusivo do Plano PRO",
        "photo": "static/img/academy/gmn-hero.jpg",
        "accent": "#fbbf24",
        "caption": (
            "Além de 2.000 leads salvos e fila prioritária no Google Maps, o Plano PRO libera a Academia de Vendas completa e vídeos VSL prontos para você baixar e enviar aos seus clientes.\n\n"
            "Tudo que você precisa para prospectar e fechar contratos está aqui. Link na bio!"
        ),
    },
]

STATIC_STUDIO_POSTS: List[Dict[str, str]] = [
    {
        "static_rel": "static/ig_library/01-sem-indicacao-busca-local-1080x1350.jpg",
        "topic": "Criativo 01 · Prospecção Automática",
        "caption": DAILY_ANGLES[0]["caption"],
    },
    {
        "static_rel": "static/ig_library/02-ofertas-ticket-alto-1080x1350.jpg",
        "topic": "Criativo 02 · Contratos R$ 300 a R$ 1.500",
        "caption": DAILY_ANGLES[2]["caption"],
    },
    {
        "static_rel": "static/ig_library/03-funil-crm-e-chat-1080x1350.jpg",
        "topic": "Criativo 03 · Buscou, Mandou, Vendeu",
        "caption": DAILY_ANGLES[3]["caption"],
    },
    {
        "static_rel": "static/ig_library/04-gmn-e-plaquinha-nfc-1080x1350.jpg",
        "topic": "Criativo 04 · Lista de Clientes em 2 Min",
        "caption": DAILY_ANGLES[4]["caption"],
    },
    {
        "static_rel": "static/ig_library/05-oferta-plano-pro-academia-1080x1350.jpg",
        "topic": "Criativo 05 · Plano PRO + Cursos + VSLs",
        "caption": DAILY_ANGLES[6]["caption"],
    },
]


def _hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def generate_daily_creative_jpg(
    output_filename: str,
    angle_idx: int = 0,
    custom_headline: str = "",
    custom_sub: str = "",
    custom_kicker: str = "",
) -> Dict[str, Any]:
    """Gera um criativo minimalista 1080x1350 JPEG em alta qualidade no servidor."""
    spec = DAILY_ANGLES[angle_idx % len(DAILY_ANGLES)]
    headline = (custom_headline or spec["headline"]).strip()
    sub = (custom_sub or spec["sub"]).strip()
    kicker = (custom_kicker or spec["kicker"]).strip()
    badge_txt = spec["badge"]
    accent_rgb = _hex_to_rgb(spec["accent"])

    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), (6, 11, 22))
    draw = ImageDraw.Draw(canvas, "RGBA")

    # Sutil gradiente radial azul/esmeralda no fundo
    for r in range(520, 40, -24):
        alpha = int(14 * (1 - r / 520))
        draw.ellipse((180 - r, 140 - r, 180 + r, 140 + r), fill=(37, 99, 235, alpha))
        draw.ellipse((900 - r, 1180 - r, 900 + r, 1180 + r), fill=(16, 185, 129, alpha))

    f_brand = _load_font(30, bold=True)
    f_kicker = _load_font(20, bold=True)
    f_head = _load_font(76, bold=True)
    f_sub = _load_font(28, bold=False)
    f_badge = _load_font(26, bold=True)
    f_cta = _load_font(32, bold=True)

    # Logo icon + marca no topo
    icon_path = os.path.join(BASE_DIR, "app-icon-1024.png")
    if os.path.exists(icon_path):
        try:
            ico = Image.open(icon_path).convert("RGBA").resize((52, 52), Image.Resampling.LANCZOS)
            canvas.paste(ico, (64, 54), ico)
        except Exception:
            pass
    draw.text((130, 64), "MapaLeads", font=f_brand, fill=(255, 255, 255))
    ml_w = draw.textlength("MapaLeads ", font=f_brand)
    draw.text((130 + ml_w, 64), "PRO", font=f_brand, fill=(96, 165, 250))

    kw = draw.textlength(kicker, font=f_kicker)
    draw.text((W - 64 - kw, 70), kicker, font=f_kicker, fill=accent_rgb)

    # Headline em até 2-3 linhas
    y = 148
    lines = headline.split("\n")
    if len(lines) == 1:
        lines = textwrap.wrap(headline, width=18)
    for idx, line in enumerate(lines[:3]):
        color = accent_rgb if idx == len(lines) - 1 else (255, 255, 255)
        draw.text((64, y), line, font=f_head, fill=color)
        y += 84

    # Subtítulo curto
    y += 14
    for sline in textwrap.wrap(sub, width=48)[:2]:
        draw.text((64, y), sline, font=f_sub, fill=(203, 213, 225))
        y += 38

    # Área central com foto fotorrealista recortada com cantos arredondados
    box_top = max(y + 26, 440)
    box_bottom = 1140
    box_left, box_right = 64, W - 64
    bw, bh = box_right - box_left, box_bottom - box_top

    photo_path = os.path.join(BASE_DIR, spec["photo"].replace("/", os.sep))
    if os.path.exists(photo_path):
        ph = Image.open(photo_path).convert("RGB")
        # Crop central mantendo proporção do box
        target_ratio = bw / bh
        src_ratio = ph.width / ph.height
        if src_ratio > target_ratio:
            new_w = int(ph.height * target_ratio)
            left = (ph.width - new_w) // 2
            ph = ph.crop((left, 0, left + new_w, ph.height))
        else:
            new_h = int(ph.width / target_ratio)
            top = (ph.height - new_h) // 2
            ph = ph.crop((0, top, ph.width, top + new_h))
        ph = ph.resize((bw, bh), Image.Resampling.LANCZOS).convert("RGBA")

        # Gradiente escuro na base da foto para destacar selo
        grad = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(grad)
        for gy in range(int(bh * 0.45), bh):
            frac = (gy - bh * 0.45) / (bh * 0.55)
            gdraw.line([(0, gy), (bw, gy)], fill=(6, 11, 22, int(235 * frac)))
        ph = Image.alpha_composite(ph, grad)

        mask = Image.new("L", (bw, bh), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, bw, bh), radius=28, fill=255)
        canvas.paste(ph.convert("RGB"), (box_left, box_top), mask)
        draw.rounded_rectangle((box_left, box_top, box_right, box_bottom), radius=28, outline=(255, 255, 255, 65), width=2)

    # Card de destaque na base da foto
    pill_y1, pill_y2 = box_bottom - 108, box_bottom - 24
    draw.rounded_rectangle((box_left + 26, pill_y1, box_right - 26, pill_y2), radius=18, fill=(10, 17, 34, 232), outline=accent_rgb + (255,), width=2)
    draw.rounded_rectangle((box_left + 46, pill_y1 + 18, box_left + 94, pill_y1 + 66), radius=12, fill=accent_rgb + (255,))
    # Checkmark vetorial (compatível com qualquer fonte Linux/Windows)
    draw.line([(box_left + 58, pill_y1 + 43), (box_left + 67, pill_y1 + 52), (box_left + 83, pill_y1 + 32)], fill=(6, 11, 22), width=5)
    draw.text((box_left + 112, pill_y1 + 26), badge_txt, font=f_badge, fill=(255, 255, 255))

    # Botão CTA esmeralda na base
    cta_y1, cta_y2 = 1175, 1265
    draw.rounded_rectangle((64, cta_y1, W - 64, cta_y2), radius=20, fill=(16, 185, 129, 255))
    cta_txt = "TESTE GRÁTIS 24H  ·  LINK NA BIO"
    cw = draw.textlength(cta_txt, font=f_cta)
    draw.text(((W - cw) / 2, cta_y1 + 25), cta_txt, font=f_cta, fill=(255, 255, 255))

    site_txt = "mapaleadspro.online"
    sw = draw.textlength(site_txt, font=f_kicker)
    draw.text(((W - sw) / 2, 1286), site_txt, font=f_kicker, fill=(148, 163, 184))

    out_path = os.path.join(get_ig_media_dir(), output_filename)
    canvas.save(out_path, "JPEG", quality=92, optimize=True)
    return {
        "filename": output_filename,
        "local_path": out_path,
        "rel_url": f"/ig-media/{output_filename}",
        "caption": spec["caption"],
        "topic": spec["topic"],
        "media_type": "IMAGE",
    }


def _build_public_url(rel_url: str, base_url: str) -> str:
    if rel_url.startswith(("http://", "https://")):
        return rel_url
    base = (base_url or "https://mapaleadspro.online").rstrip("/")
    return f"{base}{rel_url if rel_url.startswith('/') else '/' + rel_url}"


def discover_instagram_accounts(access_token: str) -> Dict[str, Any]:
    token = (access_token or "").strip()
    if not token:
        return {"success": False, "error": "Cole o Access Token da Meta primeiro."}
    try:
        r = cffi_requests.get(
            f"{GRAPH_BASE}/me/accounts",
            params={
                "fields": "id,name,instagram_business_account{id,username,name,followers_count,media_count,profile_picture_url}",
                "access_token": token,
            },
            timeout=20,
        )
        data = r.json()
        if "error" in data:
            return {"success": False, "error": data["error"].get("message", "Erro na Graph API.")}
        found = []
        for page in data.get("data", []):
            ig = page.get("instagram_business_account")
            if ig and ig.get("id"):
                found.append({
                    "ig_user_id": ig["id"],
                    "username": ig.get("username", ""),
                    "name": ig.get("name", page.get("name", "")),
                    "page_name": page.get("name", ""),
                    "followers_count": ig.get("followers_count", 0),
                    "media_count": ig.get("media_count", 0),
                    "profile_picture_url": ig.get("profile_picture_url", ""),
                })
        if not found:
            return {
                "success": False,
                "error": "Nenhuma conta Instagram Profissional vinculada às páginas deste token. Garanta que seu Instagram esteja em Conta Profissional ligado a uma Página do Facebook e marque as permissões pages_show_list + instagram_basic + instagram_content_publish.",
            }
        return {"success": True, "accounts": found}
    except Exception as e:
        return {"success": False, "error": f"Falha ao consultar Meta Graph API: {e}"}


def try_exchange_long_lived_token(short_token: str) -> Optional[str]:
    cfg = get_site_settings()
    app_id = (cfg.get("meta_app_id") or "").strip()
    app_secret = (cfg.get("meta_app_secret") or "").strip()
    if not app_id or not app_secret or not short_token:
        return None
    try:
        r = cffi_requests.get(
            f"{GRAPH_BASE}/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": app_id,
                "client_secret": app_secret,
                "fb_exchange_token": short_token,
            },
            timeout=20,
        )
        d = r.json()
        return d.get("access_token")
    except Exception:
        return None


def get_ig_profile_and_media(ig_user_id: str, access_token: str, limit: int = 12) -> Dict[str, Any]:
    if not ig_user_id or not access_token:
        return {"success": False, "error": "Configure o Instagram ID e Access Token."}
    try:
        prof = cffi_requests.get(
            f"{GRAPH_BASE}/{ig_user_id}",
            params={
                "fields": "id,username,name,followers_count,follows_count,media_count,profile_picture_url",
                "access_token": access_token,
            },
            timeout=20,
        ).json()
        if "error" in prof:
            return {"success": False, "error": prof["error"].get("message", "Erro ao consultar perfil.")}

        media = cffi_requests.get(
            f"{GRAPH_BASE}/{ig_user_id}/media",
            params={
                "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
                "limit": limit,
                "access_token": access_token,
            },
            timeout=20,
        ).json()
        return {
            "success": True,
            "profile": prof,
            "media": media.get("data", []) if isinstance(media, dict) else [],
        }
    except Exception as e:
        return {"success": False, "error": f"Erro de conexão com a Graph API: {e}"}


def publish_instagram_media(
    ig_user_id: str,
    access_token: str,
    public_media_url: str,
    caption: str,
    media_type: str = "IMAGE",
) -> Dict[str, Any]:
    if not ig_user_id or not access_token:
        return {"success": False, "error": "Instagram Account ID ou Access Token não configurados."}

    payload: Dict[str, Any] = {"caption": caption or "", "access_token": access_token}
    if (media_type or "").upper() == "REELS":
        payload["media_type"] = "REELS"
        payload["video_url"] = public_media_url
        payload["share_to_feed"] = "true"
        max_wait = 120
    else:
        payload["image_url"] = public_media_url
        max_wait = 60

    try:
        c_res = cffi_requests.post(f"{GRAPH_BASE}/{ig_user_id}/media", data=payload, timeout=30).json()
        if "error" in c_res or not c_res.get("id"):
            err = (c_res.get("error") or {}).get("message", str(c_res))
            return {"success": False, "error": f"Erro ao criar container de mídia: {err}"}

        container_id = c_res["id"]
        deadline = time.time() + max_wait
        while time.time() < deadline:
            st = cffi_requests.get(
                f"{GRAPH_BASE}/{container_id}",
                params={"fields": "status_code,status", "access_token": access_token},
                timeout=15,
            ).json()
            code = st.get("status_code")
            if code == "FINISHED":
                break
            if code in ("ERROR", "EXPIRED"):
                return {"success": False, "error": f"Instagram rejeitou mídia ({code}): {st.get('status', '')}"}
            time.sleep(3)

        p_res = cffi_requests.post(
            f"{GRAPH_BASE}/{ig_user_id}/media_publish",
            data={"creation_id": container_id, "access_token": access_token},
            timeout=30,
        ).json()
        if "error" in p_res or not p_res.get("id"):
            err = (p_res.get("error") or {}).get("message", str(p_res))
            return {"success": False, "error": f"Erro ao publicar mídia: {err}"}

        ig_media_id = p_res["id"]
        permalink = ""
        try:
            info = cffi_requests.get(
                f"{GRAPH_BASE}/{ig_media_id}",
                params={"fields": "permalink", "access_token": access_token},
                timeout=15,
            ).json()
            permalink = info.get("permalink", "")
        except Exception:
            pass

        return {"success": True, "ig_media_id": ig_media_id, "permalink": permalink}
    except Exception as e:
        return {"success": False, "error": f"Falha na requisição para o Instagram: {e}"}


def prepare_next_post_asset(mode: str = "mixed", rotation_index: int = 0) -> Dict[str, Any]:
    """Escolhe entre os criativos prontos de estúdio, Reels e geração dinâmica diária em Pillow."""
    mode = (mode or "mixed").lower()
    if mode == "reels":
        return {
            "media_type": "REELS",
            "rel_url": "/static/video/vsl-mapaleads-mobile.mp4",
            "caption": DAILY_ANGLES[rotation_index % len(DAILY_ANGLES)]["caption"],
            "topic": "Reels 9:16 · Apresentação MapaLeads PRO",
        }
    if mode == "studio" or (mode == "mixed" and rotation_index % 2 == 0):
        idx = (rotation_index // (2 if mode == "mixed" else 1)) % len(STATIC_STUDIO_POSTS)
        st = STATIC_STUDIO_POSTS[idx]
        if os.path.exists(os.path.join(BASE_DIR, st["static_rel"].replace("/", os.sep))):
            return {
                "media_type": "IMAGE",
                "rel_url": "/" + st["static_rel"],
                "caption": st["caption"],
                "topic": st["topic"],
            }
    # Gera criativo inédito 1080x1350 JPEG via Pillow
    fname = f"ig_auto_{int(time.time())}_{rotation_index}.jpg"
    gen = generate_daily_creative_jpg(fname, angle_idx=rotation_index)
    return {
        "media_type": "IMAGE",
        "rel_url": gen["rel_url"],
        "caption": gen["caption"],
        "topic": gen["topic"],
    }


def execute_post_now(
    rel_or_url: Optional[str] = None,
    caption: Optional[str] = None,
    media_type: str = "IMAGE",
    queue_item_id: Optional[int] = None,
) -> Dict[str, Any]:
    cfg = get_ig_config()
    if not cfg.get("ig_user_id") or not cfg.get("ig_access_token"):
        return {"success": False, "error": "Conecte primeiro seu Access Token e Conta do Instagram no Painel Admin."}

    rot = int(cfg.get("rotation_index") or 0)
    if not rel_or_url:
        pending = list_ig_queue(status="pending")
        if pending:
            q = pending[0]
            queue_item_id = q["id"]
            rel_or_url = q["media_url"]
            caption = caption if caption is not None else q["caption"]
            media_type = q.get("media_type") or "IMAGE"
        else:
            asset = prepare_next_post_asset(cfg.get("content_mode", "mixed"), rot)
            rel_or_url = asset["rel_url"]
            caption = caption if caption is not None else asset["caption"]
            media_type = asset["media_type"]

    public_url = _build_public_url(rel_or_url, cfg.get("public_base_url", "https://mapaleadspro.online"))
    res = publish_instagram_media(
        cfg["ig_user_id"],
        cfg["ig_access_token"],
        public_url,
        caption or "",
        media_type=media_type,
    )

    if res.get("success"):
        if queue_item_id:
            mark_ig_queue_item_status(queue_item_id, "posted")
        today_str = datetime.now(BRT_TZ).strftime("%Y-%m-%d")
        save_ig_config({"last_post_date": today_str, "rotation_index": rot + 1})
        record_ig_history(
            media_type,
            public_url,
            caption or "",
            status="posted",
            ig_media_id=res.get("ig_media_id", ""),
            permalink=res.get("permalink", ""),
        )
    else:
        record_ig_history(
            media_type,
            public_url,
            caption or "",
            status="error",
            error_msg=res.get("error", "Erro desconhecido"),
        )
    return {**res, "public_url": public_url}


def autoposter_background_loop():
    """Executa 24h no servidor verificando a cada 60s se chegou o horário diário de postar."""
    while True:
        try:
            cfg = get_ig_config()
            if cfg.get("enabled") and cfg.get("ig_user_id") and cfg.get("ig_access_token"):
                now_brt = datetime.now(BRT_TZ)
                today_str = now_brt.strftime("%Y-%m-%d")
                target_hhmm = (cfg.get("post_time") or "09:00").strip()
                curr_hhmm = now_brt.strftime("%H:%M")
                if cfg.get("last_post_date") != today_str and curr_hhmm >= target_hhmm:
                    execute_post_now()
        except Exception:
            pass
        time.sleep(60)
