# -*- coding: utf-8 -*-
"""
Gerador nativo de Propostas Comerciais & Diagnósticos em PDF (.pdf) 100% White-Label.
Usa fpdf2 + Pillow (< 5 MB RAM, geração em ~50ms), suportando:
- Logo customizada do assinante (Base64 data URI, URL pública ou arquivo estático)
- Cor primária da marca em hex (#RRGGBB)
- Layout executivo A4 limpo em 1 página com link clicável de aprovação no WhatsApp
"""
import base64
import io
import os
import re
from typing import Dict, Any, List, Tuple, Optional

from fpdf import FPDF
from PIL import Image


def _hex_to_rgb(hex_color: str, default: Tuple[int, int, int] = (37, 99, 235)) -> Tuple[int, int, int]:
    h = (hex_color or "").strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6 or not re.match(r"^[0-9a-fA-F]{6}$", h):
        return default
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _mix_rgb(c1: Tuple[int, int, int], c2: Tuple[int, int, int], ratio: float) -> Tuple[int, int, int]:
    return (
        int(c1[0] * (1 - ratio) + c2[0] * ratio),
        int(c1[1] * (1 - ratio) + c2[1] * ratio),
        int(c1[2] * (1 - ratio) + c2[2] * ratio),
    )


def _clean_text(text: Any, unicode_font: bool) -> str:
    s = str(text or "")
    s = s.replace("⭐", " estrelas").replace("★", "*").replace("•", "-").replace("–", "-").replace("—", "-")
    if unicode_font:
        # Remove caracteres fora do BMP (emojis) que TTFs padrão não possuem glifo
        return "".join(ch for ch in s if ord(ch) <= 0xFFFF)
    return s.encode("latin-1", "replace").decode("latin-1")


def _load_logo_png_bytes(logo_src: str) -> Optional[Tuple[bytes, int, int]]:
    """Carrega a logo do assinante (data URI, arquivo /static/ ou URL http/https) e converte para PNG limpo."""
    src = (logo_src or "").strip()
    if not src:
        return None
    raw_bytes: Optional[bytes] = None
    try:
        if src.startswith("data:image/") and "," in src:
            b64 = src.split(",", 1)[1]
            raw_bytes = base64.b64decode(b64)
        elif src.startswith("/static/"):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            abs_p = os.path.join(base_dir, src.lstrip("/").replace("/", os.sep))
            if os.path.exists(abs_p):
                with open(abs_p, "rb") as f:
                    raw_bytes = f.read()
        elif src.startswith("http://") or src.startswith("https://"):
            import urllib.request
            req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                raw_bytes = resp.read(2_000_000)
        if not raw_bytes:
            return None
        img = Image.open(io.BytesIO(raw_bytes))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        # Achata transparência sobre branco para visual nítido no badge do cabeçalho
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        img.thumbnail((360, 360))
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue(), img.width, img.height
    except Exception:
        return None


def _find_ttf_pair() -> Optional[Tuple[str, str]]:
    candidates = [
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\segoeuib.ttf"),
    ]
    for reg, bold in candidates:
        if os.path.exists(reg) and os.path.exists(bold):
            return reg, bold
    return None


def build_proposal_pdf_bytes(
    *,
    lead: Dict[str, Any],
    brand: Dict[str, Any],
    score: Dict[str, Any],
    offer: Dict[str, Any],
    audit_points: List[Dict[str, Any]],
    setup_price_display: str,
    monthly_price_display: str,
    payment_terms: str,
    custom_notes: str,
    issue_date: str,
    valid_until: str,
    validity_days: int,
    proposal_code: str,
    approve_wa_link: str = "",
) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False, margin=10)
    pdf.add_page()

    ttf = _find_ttf_pair()
    if ttf:
        pdf.add_font("BrandFont", "", ttf[0])
        pdf.add_font("BrandFont", "B", ttf[1])
        font_family = "BrandFont"
        unicode_ok = True
    else:
        font_family = "Helvetica"
        unicode_ok = False

    t = lambda s: _clean_text(s, unicode_ok)

    brand_rgb = _hex_to_rgb(brand.get("color", "#2563eb"))
    dark_header_rgb = _mix_rgb((15, 23, 42), brand_rgb, 0.42)
    soft_brand_rgb = _mix_rgb((255, 255, 255), brand_rgb, 0.08)
    ink = (15, 23, 42)
    muted = (71, 85, 105)
    border = (226, 232, 240)
    emerald = (5, 150, 105)

    # ==================== 1. CABEÇALHO WHITE-LABEL ====================
    pdf.set_fill_color(*dark_header_rgb)
    pdf.rect(0, 0, 210, 36, style="F")
    # Faixa sutil na cor exata da marca na base do header
    pdf.set_fill_color(*brand_rgb)
    pdf.rect(0, 34.5, 210, 1.8, style="F")

    # Box branco para Logo do Assinante (18x18mm)
    logo_x, logo_y, logo_box = 14, 8.5, 19
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(logo_x, logo_y, logo_box, logo_box, style="F")

    logo_loaded = _load_logo_png_bytes(brand.get("logo_url", ""))
    if logo_loaded:
        png_bytes, iw, ih = logo_loaded
        pad = 1.6
        avail = logo_box - pad * 2
        ratio = min(avail / max(iw, 1), avail / max(ih, 1))
        dw, dh = iw * ratio, ih * ratio
        dx = logo_x + (logo_box - dw) / 2.0
        dy = logo_y + (logo_box - dh) / 2.0
        pdf.image(io.BytesIO(png_bytes), x=dx, y=dy, w=dw, h=dh)
    else:
        pdf.set_xy(logo_x, logo_y + 5.5)
        pdf.set_font(font_family, "B", 13)
        pdf.set_text_color(*brand_rgb)
        pdf.cell(logo_box, 8, t(brand.get("initials", "CD")), align="C")

    # Nome da Agência & Slogan
    pdf.set_xy(37, 10)
    pdf.set_font(font_family, "B", 14.5)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(105, 7, t(brand.get("company_name", "Consultoria Digital"))[:46])

    pdf.set_xy(37, 18)
    pdf.set_font(font_family, "", 8.5)
    pdf.set_text_color(226, 232, 240)
    pdf.cell(105, 5, t(brand.get("tagline", "Posicionamento Local & Vendas Digitais"))[:68])

    # Metadados à direita
    pdf.set_xy(142, 9)
    pdf.set_font(font_family, "B", 8.5)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(54, 5.2, t(f"PROPOSTA #{proposal_code}"), align="R")
    pdf.set_xy(142, 15.2)
    pdf.set_font(font_family, "", 8)
    pdf.set_text_color(226, 232, 240)
    pdf.cell(54, 4.5, t(f"Emissão: {issue_date}"), align="R")
    pdf.set_xy(142, 20.2)
    pdf.cell(54, 4.5, t(f"Validade: {valid_until} ({validity_days} dias)"), align="R")

    # ==================== 2. CLIENTE + SCORE ====================
    y = 42
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(*border)
    pdf.rect(14, y, 182, 25, style="FD")

    pdf.set_xy(18, y + 3)
    pdf.set_font(font_family, "B", 7.5)
    pdf.set_text_color(*brand_rgb)
    pdf.cell(125, 4, t("DIAGNÓSTICO & PROPOSTA PREPARADA EXCLUSIVAMENTE PARA"))

    pdf.set_xy(18, y + 7.5)
    pdf.set_font(font_family, "B", 13)
    pdf.set_text_color(*ink)
    pdf.cell(125, 6.5, t(lead.get("name", "Empresa"))[:52])

    pdf.set_xy(18, y + 14.8)
    pdf.set_font(font_family, "", 8)
    pdf.set_text_color(*muted)
    cat_addr = f"Segmento: {lead.get('category') or 'Comércio Local'}  |  Local: {(lead.get('address') or lead.get('city') or 'Região Local')[:56]}"
    pdf.cell(128, 4.5, t(cat_addr))

    # Caixa de Score à direita
    sx, sy, sw, sh = 152, y + 3.2, 40, 18.6
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*brand_rgb)
    pdf.set_line_width(0.5)
    pdf.rect(sx, sy, sw, sh, style="FD")
    pdf.set_line_width(0.2)

    pdf.set_xy(sx, sy + 1.5)
    pdf.set_font(font_family, "B", 6.5)
    pdf.set_text_color(*muted)
    pdf.cell(sw, 3.5, t("POTENCIAL DE GANHO"), align="C")

    pdf.set_xy(sx, sy + 5.2)
    pdf.set_font(font_family, "B", 14)
    pdf.set_text_color(*brand_rgb)
    pdf.cell(sw, 7.5, t(f"{score.get('score', 80)}/100"), align="C")

    pdf.set_xy(sx, sy + 13.5)
    pdf.set_font(font_family, "B", 6.8)
    pdf.set_text_color(*emerald)
    pdf.cell(sw, 3.8, t(score.get("tier_label", "Alta Oportunidade"))[:22], align="C")

    # ==================== 3. 4 MÉTRICAS REAIS DO GOOGLE MAPS ====================
    y = 71
    rating_str = f"{float(lead['rating']):.1f} / 5.0" if lead.get("rating") else "Não avaliada"
    rev_str = f"{int(lead.get('reviews_count') or 0)} avaliações"
    wtype = (lead.get("website_type") or "none").lower()
    site_str = "Site Ativo" if (wtype in ("own", "real_site") and lead.get("website")) else ("Só Rede Social" if wtype == "social" else "Não detectado")
    kpis = [
        ("Nota no Google Maps", rating_str, ink),
        ("Total de Avaliações", rev_str, ink),
        ("Site / Página Própria", site_str, (185, 28, 28) if site_str != "Site Ativo" else emerald),
        ("Prazo de Entrega", offer.get("delivery_time", "48 horas úteis"), emerald),
    ]
    cw = 43.25
    gap = 3.0
    for idx, (lbl, val, col) in enumerate(kpis):
        cx = 14 + idx * (cw + gap)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(*border)
        pdf.rect(cx, y, cw, 15, style="FD")
        pdf.set_xy(cx + 3, y + 2.5)
        pdf.set_font(font_family, "", 7.2)
        pdf.set_text_color(*muted)
        pdf.cell(cw - 6, 4, t(lbl))
        pdf.set_xy(cx + 3, y + 7.5)
        pdf.set_font(font_family, "B", 9.5)
        pdf.set_text_color(*col)
        pdf.cell(cw - 6, 5.5, t(val)[:22])

    # ==================== 4. RAIO-X ATUAL (DIAGNÓSTICO 2x2) ====================
    y = 91
    pdf.set_xy(14, y)
    pdf.set_font(font_family, "B", 10.5)
    pdf.set_text_color(*ink)
    pdf.cell(182, 6, t("1. Raio-X Atual & Oportunidades Identificadas"))
    y += 7

    col_w = 89.0
    box_h = 19.0
    for i, ap in enumerate(audit_points[:4]):
        col = i % 2
        row = i // 2
        bx = 14 + col * (col_w + 4.0)
        by = y + row * (box_h + 3.0)
        is_ok = bool(ap.get("ok"))
        if is_ok:
            pdf.set_fill_color(236, 253, 245)
            pdf.set_draw_color(167, 243, 208)
            title_c = (6, 95, 70)
            body_c = (6, 78, 59)
            prefix = "[OK] "
        else:
            pdf.set_fill_color(254, 242, 242)
            pdf.set_draw_color(254, 202, 202)
            title_c = (153, 27, 27)
            body_c = (127, 29, 29)
            prefix = "[!] "
        pdf.rect(bx, by, col_w, box_h, style="FD")
        pdf.set_xy(bx + 3, by + 2.2)
        pdf.set_font(font_family, "B", 8.0)
        pdf.set_text_color(*title_c)
        pdf.cell(col_w - 6, 4.2, t(prefix + (ap.get("title") or ""))[:48])
        pdf.set_xy(bx + 3, by + 6.8)
        pdf.set_font(font_family, "", 7.4)
        pdf.set_text_color(*body_c)
        pdf.multi_cell(col_w - 6, 3.6, t(ap.get("detail") or "")[:135])

    # ==================== 5. SOLUÇÃO RECOMENDADA & ENTREGÁVEIS ====================
    y = 145
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*border)
    sol_h = 68
    pdf.rect(14, y, 182, sol_h, style="FD")
    pdf.set_fill_color(*brand_rgb)
    pdf.rect(14, y, 2.2, sol_h, style="F")

    pdf.set_xy(19.5, y + 3.5)
    pdf.set_font(font_family, "B", 10.5)
    pdf.set_text_color(*ink)
    pdf.cell(173, 5.5, t(f"2. Solução Recomendada: {offer.get('title', '')}")[:82])

    pdf.set_xy(19.5, y + 9.5)
    pdf.set_font(font_family, "", 8.0)
    pdf.set_text_color(*muted)
    pdf.multi_cell(172, 4.0, t(offer.get("summary", ""))[:220])

    # Entregáveis em 2 colunas
    delivs = list(offer.get("deliverables") or [])[:8]
    dy_start = y + 20.5
    d_col_w = 84.0
    for idx, d_text in enumerate(delivs):
        dc = idx % 2
        dr = idx // 2
        dx = 19.5 + dc * (d_col_w + 4.5)
        dy = dy_start + dr * 11.2
        pdf.set_xy(dx, dy)
        pdf.set_font(font_family, "B", 8.0)
        pdf.set_text_color(*emerald)
        pdf.cell(4.5, 3.8, t("+"))
        pdf.set_xy(dx + 4.0, dy)
        pdf.set_font(font_family, "", 7.6)
        pdf.set_text_color(*ink)
        pdf.multi_cell(d_col_w - 4.5, 3.6, t(d_text)[:108])

    # ==================== 6. BLOCO DE INVESTIMENTO & GARANTIA ====================
    y = 218
    inv_h = 44
    pdf.set_fill_color(*soft_brand_rgb)
    pdf.set_draw_color(*brand_rgb)
    pdf.set_line_width(0.55)
    pdf.rect(14, y, 182, inv_h, style="FD")
    pdf.set_line_width(0.2)

    pdf.set_xy(19, y + 3.5)
    pdf.set_font(font_family, "B", 7.8)
    pdf.set_text_color(*muted)
    pdf.cell(102, 4.2, t(f"INVESTIMENTO ESPECIAL PARA {str(lead.get('name', '')).upper()}")[:54])

    pdf.set_xy(19, y + 8.5)
    pdf.set_font(font_family, "B", 16.5)
    pdf.set_text_color(*brand_rgb)
    pdf.cell(102, 8.5, t(setup_price_display)[:34])

    cur_y = y + 18.0
    if monthly_price_display:
        pdf.set_xy(19, cur_y)
        pdf.set_font(font_family, "B", 8.6)
        pdf.set_text_color(*emerald)
        pdf.cell(102, 4.8, t(f"Acompanhamento / Mensalidade: {monthly_price_display}")[:58])
        cur_y += 5.8

    pdf.set_xy(19, cur_y)
    pdf.set_font(font_family, "", 7.8)
    pdf.set_text_color(*muted)
    terms_full = f"Condição de Pagamento: {payment_terms}"
    if custom_notes:
        terms_full += f"\nObs.: {custom_notes}"
    pdf.multi_cell(100, 3.9, t(terms_full)[:190])

    # Caixa de garantia à direita
    gx, gy, gw, gh = 123, y + 4.5, 68, inv_h - 9
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*border)
    pdf.rect(gx, gy, gw, gh, style="FD")
    pdf.set_xy(gx + 3.5, gy + 3)
    pdf.set_font(font_family, "B", 8.2)
    pdf.set_text_color(*emerald)
    pdf.cell(gw - 7, 4.5, t("Garantia & Próximo Passo"))
    pdf.set_xy(gx + 3.5, gy + 8.5)
    pdf.set_font(font_family, "", 7.5)
    pdf.set_text_color(*muted)
    g_text = (
        f"- Entrega garantida em {offer.get('delivery_time', '48h úteis')}.\n"
        "- Sem multa de fidelidade ou burocracia.\n"
        "- Responda no WhatsApp abaixo para aprovar e iniciarmos hoje."
    )
    pdf.multi_cell(gw - 7, 4.1, t(g_text))

    # ==================== 7. RODAPÉ WHITE-LABEL + BOTÃO CLICÁVEL WHATSAPP ====================
    fy = 268
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(*border)
    pdf.rect(0, fy, 210, 29, style="F")
    pdf.line(0, fy, 210, fy)

    pdf.set_xy(14, fy + 6)
    pdf.set_font(font_family, "B", 9.5)
    pdf.set_text_color(*ink)
    pdf.cell(115, 5, t(f"{brand.get('consultant_name', '')}  |  {brand.get('company_name', '')}")[:62])

    pdf.set_xy(14, fy + 12)
    pdf.set_font(font_family, "", 8.0)
    pdf.set_text_color(*muted)
    contact_parts = []
    if brand.get("phone_display"):
        contact_parts.append(f"WhatsApp: {brand['phone_display']}")
    if brand.get("email"):
        contact_parts.append(brand["email"])
    pdf.cell(115, 4.5, t("   |   ".join(contact_parts))[:72])

    if approve_wa_link:
        bx, by, bw, bh = 132, fy + 6.5, 64, 11.5
        pdf.set_fill_color(16, 185, 129)
        pdf.rect(bx, by, bw, bh, style="F")
        pdf.set_xy(bx, by + 2.8)
        pdf.set_font(font_family, "B", 8.5)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(bw, 6, t("Aprovar Proposta no WhatsApp"), align="C", link=approve_wa_link)

    out_bytes = pdf.output()
    return bytes(out_bytes)
