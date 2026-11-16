import csv
import io
import json
from typing import List, Dict, Any

def export_to_csv_bytes(leads: List[Dict[str, Any]]) -> bytes:
    """
    Gera CSV com delimitador ';' e encoding UTF-8 com BOM (utf-8-sig),
    garantindo compatibilidade perfeita ao abrir diretamente no Microsoft Excel no Brasil.
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    
    headers = [
        "Nome da Empresa",
        "Possui Site?",
        "Tipo de Presença Web",
        "Website",
        "Telefone Formatado",
        "WhatsApp (Direto)",
        "É WhatsApp?",
        "Avaliação (Estrelas)",
        "Quantidade de Avaliações",
        "Categoria",
        "Endereço",
        "Bairro / Região",
        "Status CRM",
        "Link no Google Maps",
        "Termo Pesquisado",
        "Notas do Prospectador",
        "Data de Cadastro"
    ]
    writer.writerow(headers)
    
    for l in leads:
        web_type_pt = {
            "none": "SEM SITE (Oportunidade de Ouro)",
            "social": "Apenas Rede Social / Linktree",
            "directory": "Apenas Catálogo / Lista",
            "own": "Possui Site Próprio"
        }.get(l.get("website_type"), "Sem Site")
        
        has_site_pt = "NÃO" if l.get("website_type") in ("none", None) else ("PARCIAL (Rede Social)" if l.get("website_type") in ("social", "directory") else "SIM")
        
        clean_phone = l.get("clean_phone")
        wa_link = f"https://wa.me/{clean_phone}" if clean_phone else ""
        
        row = [
            l.get("name", ""),
            has_site_pt,
            web_type_pt,
            l.get("website") or "",
            l.get("phone") or "",
            wa_link,
            "SIM" if l.get("is_whatsapp") else "NÃO",
            str(l.get("rating") or "").replace(".", ","),
            l.get("reviews_count") or 0,
            l.get("category") or "",
            l.get("address") or "",
            l.get("neighborhood") or "",
            (l.get("crm_status") or "novo").upper(),
            l.get("maps_url") or "",
            l.get("search_query") or "",
            l.get("notes") or "",
            l.get("created_at") or ""
        ]
        writer.writerow(row)
        
    return output.getvalue().encode("utf-8-sig")

def export_to_json_bytes(leads: List[Dict[str, Any]]) -> bytes:
    return json.dumps(leads, indent=2, ensure_ascii=False).encode("utf-8")
