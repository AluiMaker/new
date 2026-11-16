import os
import sys
import time
import json
import re
import shutil
import socket
import subprocess
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional, Callable, Tuple, Set
import websocket

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BROWSER_EXECUTABLES = [
    os.environ.get("CHROME_BIN", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
]

SOCIAL_DOMAINS = [
    "facebook.com", "fb.com", "instagram.com", "linktr.ee", "linktree.com",
    "wa.me", "whatsapp.com", "api.whatsapp.com", "tiktok.com",
    "linkedin.com", "youtube.com", "twitter.com", "x.com", "bit.ly"
]

DIRECTORY_DOMAINS = [
    "guiamais.com.br", "telelistas.net", "lista11.com.br", "apontador.com.br",
    "ifood.com.br", "tripadvisor.com", "yellowpages.com", "hagah.com.br",
    "guiadebairros.com.br", "encontra", " doctoralia.com.br", "booking.com"
]

# Termos amplos para Varredura Total ("Rua Toda / Região Sem Restrições"):
# Varre todos os tipos de negócios comerciais na via ou região sem travar em 1 nicho.
SWEEP_ALL_TERMS = [
    "empresas",
    "lojas",
    "restaurantes e padarias",
    "oficina mecânica",
    "salão de beleza e barbearia",
    "clínica médica",
    "dentista",
    "clínica de estética",
    "material de construção",
    "marcenaria e vidraçaria",
    "contabilidade e advocacia",
    "pet shop e veterinária",
    "academia e pilates",
    "farmácia e ótica",
    "imobiliária",
    "supermercado e mercearia",
    "assistência técnica e informática",
    "gráfica e comunicação visual",
    "escola e cursos",
    "auto elétrica e pneus",
    "serralheria e marmoraria",
    "ar condicionado e energia solar",
    "fisioterapia e psicologia",
    "arquitetura e engenharia",
    "roupas e calçados",
    "lavanderia e chaveiro",
    "buffet e festas",
    "transportadora e frete"
]

DEFAULT_SEGMENTS = [
    # 1. Comércio & Varejo Geral (No topo por maior volume comercial nas ruas)
    {"id": "lojas_comercio", "name": "Lojas e Comércio em Geral", "icon": "store", "category": "Comércio & Varejo"},
    {"id": "roupas", "name": "Lojas de Roupas e Confecções", "icon": "shirt", "category": "Comércio & Varejo"},
    {"id": "moveis", "name": "Lojas de Móveis e Colchões", "icon": "couch", "category": "Comércio & Varejo"},
    {"id": "petshops", "name": "Pet Shops, Banho & Tosa", "icon": "paw", "category": "Comércio & Varejo"},
    {"id": "oticas", "name": "Óticas e Comércio de Óculos", "icon": "glasses", "category": "Comércio & Varejo"},
    {"id": "farmacias_manipulacao", "name": "Farmácias e Manipulação", "icon": "pills", "category": "Comércio & Varejo"},
    {"id": "floriculturas", "name": "Floriculturas e Plantas", "icon": "seedling", "category": "Comércio & Varejo"},
    {"id": "chaveiros", "name": "Chaveiros 24 Horas", "icon": "key", "category": "Comércio & Varejo"},

    # 2. Gastronomia & Alimentação
    {"id": "restaurantes", "name": "Restaurantes e Buffets", "icon": "utensils", "category": "Gastronomia"},
    {"id": "confeitarias_padarias", "name": "Padarias, Confeitarias e Docerias", "icon": "cake-candles", "category": "Gastronomia"},
    {"id": "pizzarias", "name": "Pizzarias", "icon": "pizza-slice", "category": "Gastronomia"},
    {"id": "hamburguerias", "name": "Hamburguerias e Lanchonetes", "icon": "burger", "category": "Gastronomia"},
    {"id": "cafeterias", "name": "Cafeterias", "icon": "mug-hot", "category": "Gastronomia"},
    {"id": "marmitaria", "name": "Marmitarias e Refeições", "icon": "box", "category": "Gastronomia"},
    {"id": "bares_pubs", "name": "Bares e Espetinhos", "icon": "beer-mug-empty", "category": "Gastronomia"},
    {"id": "acaiterias_sorveterias", "name": "Açaiterias e Sorveterias", "icon": "ice-cream", "category": "Gastronomia"},
    {"id": "bebidas", "name": "Distribuidoras de Bebidas e Supermercados", "icon": "wine-bottle", "category": "Gastronomia"},

    # 3. Automotivo & Transportes
    {"id": "oficinas", "name": "Oficinas Mecânicas e Auto Elétricas", "icon": "wrench", "category": "Automotivo"},
    {"id": "auto_center", "name": "Auto Centers, Pneus e Alinhamento", "icon": "car", "category": "Automotivo"},
    {"id": "funilaria_pintura", "name": "Funilaria, Pintura e Martelinho", "icon": "spray-can", "category": "Automotivo"},
    {"id": "lava_rapido", "name": "Lava Jato e Estética Automotiva", "icon": "soap", "category": "Automotivo"},
    {"id": "concessionarias_lojas", "name": "Lojas de Carros e Seminovos", "icon": "car-side", "category": "Automotivo"},
    {"id": "guincho", "name": "Guinchos e Auto Socorro", "icon": "truck-pickup", "category": "Automotivo"},
    {"id": "troca_oleo", "name": "Troca de Óleo e Autopeças", "icon": "oil-can", "category": "Automotivo"},

    # 4. Beleza, Estética & Bem-Estar
    {"id": "salao_beleza", "name": "Salões de Beleza e Cabeleireiros", "icon": "wand-magic-sparkles", "category": "Beleza & Estética"},
    {"id": "barbearias", "name": "Barbearias", "icon": "scissors", "category": "Beleza & Estética"},
    {"id": "estetica", "name": "Clínicas de Estética", "icon": "spa", "category": "Beleza & Estética"},
    {"id": "manicure_nails", "name": "Studios de Manicure e Nail Design", "icon": "hand-sparkles", "category": "Beleza & Estética"},
    {"id": "lash_design", "name": "Extensão de Cílios e Sobrancelhas", "icon": "eye", "category": "Beleza & Estética"},
    {"id": "tatuagem", "name": "Estúdios de Tatuagem", "icon": "pen-nib", "category": "Beleza & Estética"},
    {"id": "massoterapia", "name": "Massoterapia e Quiropraxia", "icon": "hands", "category": "Beleza & Estética"},

    # 5. Construção, Reformas & Manutenção
    {"id": "construcao", "name": "Materiais de Construção, Elétrica e Hidráulica", "icon": "hard-hat", "category": "Construção & Reformas"},
    {"id": "marcenarias", "name": "Marcenarias e Móveis Planejados", "icon": "hammer", "category": "Construção & Reformas"},
    {"id": "vidracarias", "name": "Vidraçarias e Box de Vidro", "icon": "border-all", "category": "Construção & Reformas"},
    {"id": "marmorarias", "name": "Marmorarias", "icon": "gem", "category": "Construção & Reformas"},
    {"id": "serralherias", "name": "Serralherias e Estruturas Metálicas", "icon": "shield-alt", "category": "Construção & Reformas"},
    {"id": "ar_condicionado", "name": "Ar Condicionado e Refrigeração", "icon": "snowflake", "category": "Construção & Reformas"},
    {"id": "energia_solar", "name": "Energia Solar Fotovoltaica", "icon": "solar-panel", "category": "Construção & Reformas"},
    {"id": "eletricistas", "name": "Eletricistas e Encanadores", "icon": "bolt", "category": "Construção & Reformas"},
    {"id": "pintores", "name": "Pintura, Gesso e Drywall", "icon": "paint-roller", "category": "Construção & Reformas"},
    {"id": "dedetizadoras", "name": "Dedetizadoras e Controle de Pragas", "icon": "bug", "category": "Construção & Reformas"},

    # 6. Saúde, Medicina & Cuidados
    {"id": "medicos", "name": "Clínicas Médicas e Consultórios", "icon": "stethoscope", "category": "Saúde & Medicina"},
    {"id": "dentistas", "name": "Dentistas e Clínicas Odontológicas", "icon": "tooth", "category": "Saúde & Medicina"},
    {"id": "fisioterapia", "name": "Fisioterapia e Reabilitação", "icon": "person-walking", "category": "Saúde & Medicina"},
    {"id": "veterinarias", "name": "Clínicas Veterinárias", "icon": "shield-dog", "category": "Saúde & Medicina"},
    {"id": "laboratorios", "name": "Laboratórios de Análises Clínicas", "icon": "flask-vial", "category": "Saúde & Medicina"},
    {"id": "psicologos", "name": "Psicólogos e Clínicas de Psicologia", "icon": "brain", "category": "Saúde & Medicina"},
    {"id": "nutricionistas", "name": "Nutricionistas", "icon": "apple-whole", "category": "Saúde & Medicina"},
    {"id": "fonoaudiologia", "name": "Fonoaudiologia e Podologia", "icon": "hand-holding-heart", "category": "Saúde & Medicina"},

    # 7. B2B, Serviços Profissionais & Corporativos
    {"id": "contabilidade", "name": "Escritórios de Contabilidade", "icon": "calculator", "category": "Serviços B2B"},
    {"id": "advocacia", "name": "Escritórios de Advocacia", "icon": "scale-balanced", "category": "Serviços B2B"},
    {"id": "engenharia_arquitetura", "name": "Engenharia e Arquitetura", "icon": "compass-drafting", "category": "Serviços B2B"},
    {"id": "grafica", "name": "Gráficas e Comunicação Visual", "icon": "print", "category": "Serviços B2B"},
    {"id": "ti_informatica", "name": "Assistência Técnica e Informática", "icon": "laptop-code", "category": "Serviços B2B"},
    {"id": "agencias_mkt", "name": "Agências de Marketing e Publicidade", "icon": "bullhorn", "category": "Serviços B2B"},
    {"id": "seguranca_patrimonial", "name": "Segurança Eletrônica e Monitoramento", "icon": "shield-halved", "category": "Serviços B2B"},
    {"id": "limpeza_conservacao", "name": "Empresas de Limpeza e Conservação", "icon": "broom", "category": "Serviços B2B"},
    {"id": "logistica_transporte", "name": "Transportadoras e Fretes", "icon": "truck-fast", "category": "Serviços B2B"},
    {"id": "despachante", "name": "Despachantes", "icon": "file-contract", "category": "Serviços B2B"},

    # 8. Imobiliário, Educação, Fitness & Eventos
    {"id": "imobiliarias", "name": "Imobiliárias e Corretoras de Seguros", "icon": "house", "category": "Imobiliário & Finanças"},
    {"id": "academias", "name": "Academias, Pilates e Crossfit", "icon": "dumbbell", "category": "Fitness & Esportes"},
    {"id": "escolas_idiomas", "name": "Escolas, Cursos e Idiomas", "icon": "graduation-cap", "category": "Educação"},
    {"id": "autoescolas", "name": "Autoescolas", "icon": "id-card", "category": "Educação"},
    {"id": "buffets_festas", "name": "Buffets, Eventos e Fotografia", "icon": "champagne-glasses", "category": "Eventos & Festas"},
]


def find_browser_executable() -> str:
    for path in BROWSER_EXECUTABLES:
        if path and os.path.exists(path):
            return path
    for cmd in ("google-chrome", "chromium", "chromium-browser", "msedge", "chrome"):
        found = shutil.which(cmd)
        if found:
            return found
    raise FileNotFoundError("Nenhum navegador compatível (Chrome, Chromium ou Edge) encontrado no sistema.")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def clean_phone_number(raw_phone: str) -> Dict[str, Any]:
    if not raw_phone:
        return {
            "phone": None,
            "clean_phone": None,
            "is_whatsapp": False,
            "phone_type": "unknown",
            "whatsapp_verified": 0
        }

    digits = re.sub(r"\D", "", str(raw_phone))

    # Rejeita 0800, 0300, 4004, 4003 (telefones de central que não têm WhatsApp)
    if digits.startswith(("0800", "0300", "0500", "4004", "4003", "3003")):
        return {
            "phone": None,
            "clean_phone": None,
            "is_whatsapp": False,
            "phone_type": "invalid",
            "whatsapp_verified": -1
        }

    # Remove DDI 55
    if digits.startswith("55") and len(digits) in (12, 13):
        digits = digits[2:]

    # Remove zero inicial antes do DDD (ex: 031999998888 -> 31999998888, 03133334444 -> 3133334444)
    if digits.startswith("0") and len(digits) in (11, 12):
        digits = digits[1:]

    if len(digits) not in (10, 11):
        return {
            "phone": None,
            "clean_phone": None,
            "is_whatsapp": False,
            "phone_type": "unknown",
            "whatsapp_verified": 0
        }

    ddd = digits[:2]
    num = digits[2:]

    # Valida DDD brasileiro (11 a 99)
    try:
        ddd_int = int(ddd)
        if ddd_int < 11 or ddd_int > 99:
            return {
                "phone": None,
                "clean_phone": None,
                "is_whatsapp": False,
                "phone_type": "unknown",
                "whatsapp_verified": 0
            }
    except ValueError:
        return {
            "phone": None,
            "clean_phone": None,
            "is_whatsapp": False,
            "phone_type": "unknown",
            "whatsapp_verified": 0
        }

    # 11 dígitos começando com 9: celular móvel
    # 10 dígitos: telefone comercial fixo (muito usado como WhatsApp Business no Brasil)
    if len(digits) == 11 and num.startswith("9"):
        formatted = f"({ddd}) {num[:5]}-{num[5:]}"
        phone_type = "mobile"
        is_whatsapp = True
    elif len(digits) == 10 and num[0] in "23456789":
        formatted = f"({ddd}) {num[:4]}-{num[4:]}"
        phone_type = "fixed"
        is_whatsapp = True
    else:
        return {
            "phone": None,
            "clean_phone": None,
            "is_whatsapp": False,
            "phone_type": "unknown",
            "whatsapp_verified": 0
        }

    return {
        "phone": formatted,
        "clean_phone": f"55{digits}",
        "is_whatsapp": is_whatsapp,
        "phone_type": phone_type,
        "whatsapp_verified": 0
    }


def is_bare_address_title(title: str, street: str = "") -> bool:
    """
    Detecta quando o card do Google Maps é apenas um endereço/lote vazio
    (ex: 'R. Jacuí, 1423 - Lj 2 - Floresta' ou '31110-822') e não uma empresa real.
    """
    if not title:
        return True
    t = title.strip()
    t_low = t.lower()

    # CEP puro
    if re.match(r"^\d{5}-?\d{3}$", t_low):
        return True

    # Começa com prefixo de logradouro seguido de número de porta/lote
    if re.match(r"^(r\.|rua |av\.|avenida |al\.|alameda |travessa |tr\.|pç\.|praça |rod\.|rodovia |estr\.|estrada )", t_low):
        if re.search(r",\s*\d+", t_low) or " - lj" in t_low or re.search(r"\b\d{5}-\d{3}\b", t_low):
            return True
        if street and t_low == street.strip().lower():
            return True

    return False


def classify_website(url: Optional[str]) -> Tuple[str, Optional[str]]:
    if not url or not url.strip() or url.strip() == "#":
        return "none", None

    u = url.strip().lower()
    # Ignora links internos do Google Maps
    if "google.com/maps" in u or "maps.google." in u:
        return "none", None

    for dom in SOCIAL_DOMAINS:
        if dom in u:
            return "social", url.strip()
    for dom in DIRECTORY_DOMAINS:
        if dom in u:
            return "directory", url.strip()

    return "own", url.strip()


PHONE_REGEX = re.compile(r'(?:0?\(?\d{2}\)?\s*(?:9\d{4}|\d{4})[-.\s]?\d{4})')


def parse_card_lines(lines: List[str], business_name: str, direct_phone: Optional[str] = None) -> Dict[str, Any]:
    phone_found = direct_phone
    address_found = None
    category_found = None

    for line in lines:
        if not line or line == business_name:
            continue

        clean_line = re.sub(r'[\ue000-\uf8ff]', '', line).strip()
        if not phone_found:
            phone_match = PHONE_REGEX.search(clean_line)
            if phone_match:
                phone_found = phone_match.group(0).strip()

        # Ignora linhas que são apenas nota de avaliação ex: "4,8(120)"
        if re.match(r"^\d[.,]\d\s*\(\d+", clean_line):
            continue

        for subline in clean_line.split("\n"):
            subline = subline.strip()
            if not subline:
                continue
            if "·" in subline:
                parts = [p.strip() for p in subline.split("·") if p.strip()]
                for idx, p in enumerate(parts):
                    p_low = p.lower()
                    if any(w in p_low for w in ("aberto", "fechado", "fecha ", "abre ", "24 horas")):
                        continue
                    if PHONE_REGEX.search(p):
                        continue
                    if idx == 0 and not category_found and len(p) < 48 and not any(c.isdigit() for c in p[:4]):
                        category_found = p
                    elif any(sk in p_low for sk in ["r.", "rua ", "av.", "avenida ", "estrada ", "estr.", "alameda ", "al.", "praça ", "travessa ", "rod."]) or re.search(r",\s*\d+", p):
                        if not address_found:
                            address_found = p
            else:
                sub_low = subline.lower()
                if not address_found and any(sk in sub_low for sk in ["r. ", "rua ", "av. ", "avenida ", "estrada ", "alameda ", "praça "]):
                    address_found = subline

    phone_info = clean_phone_number(phone_found or "")
    return {
        "category": category_found,
        "address": address_found,
        "phone": phone_info["phone"],
        "clean_phone": phone_info["clean_phone"],
        "is_whatsapp": phone_info["is_whatsapp"],
        "phone_type": phone_info["phone_type"],
        "whatsapp_verified": phone_info["whatsapp_verified"]
    }


def build_maps_search_query(term: str, street: str, neighborhood: str, city: str, place_type: str, fallback_query: str) -> str:
    """
    Constrói uma consulta limpa e direta que o Google Maps sempre abre em modo lista (feed),
    evitando travar no pino estático da rua.
    """
    t = (term or "").strip()
    if not t or t.lower() in ("todos", "todos os negócios", "qualquer", "geral"):
        t = "empresas"

    # Simplifica nomes muito longos de segmentos para melhorar o match do Google Maps
    if " e " in t and len(t) > 28:
        t = t.split(" e ")[0].strip()

    loc_type = (place_type or "street").lower()
    if loc_type == "city":
        loc = city or fallback_query
    elif loc_type == "neighborhood":
        loc = f"{neighborhood}, {city}".strip(", ") if neighborhood else (city or fallback_query)
    elif loc_type == "street":
        is_whole = not neighborhood or neighborhood.lower() in ("rua toda", "extensão completa", "extensão inteira", "todas")
        if is_whole:
            loc = f"{street}, {city}".strip(", ") if street else fallback_query
        else:
            loc = f"{street}, {neighborhood}, {city}".strip(", ") if street else fallback_query
    else:
        loc = fallback_query

    full_q = f"{t} {loc}".strip()
    return re.sub(r"\s+", " ", full_q)


class GoogleMapsScraper:
    def __init__(self, headless: bool = True, log_callback: Optional[Callable[[str], None]] = None):
        self.port = find_free_port()
        self.headless = headless
        self.log_callback = log_callback or (lambda msg: None)
        self.process: Optional[subprocess.Popen] = None
        self.ws: Optional[websocket.WebSocket] = None
        self.user_data_dir = os.path.join(os.environ.get("TEMP", "C:\\Temp"), f"chrome_gmaps_lh_{self.port}")
        self.stop_requested = False
        self._req_counter = 1

    def log(self, msg: str):
        self.log_callback(msg)

    def request_stop(self):
        """Solicita parada pelo usuário e fecha o navegador."""
        self.stop_requested = True
        self.close()

    def ensure_browser(self, initial_url: str):
        if self.process is not None and self.ws is not None:
            self.navigate(initial_url)
            return

        browser_exe = find_browser_executable()
        self.log(f"Iniciando navegador {'em segundo plano' if self.headless else 'visível'} (porta {self.port})...")

        args = [
            browser_exe,
            f"--remote-debugging-port={self.port}",
            "--remote-allow-origins=*",
            f"--user-data-dir={self.user_data_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
            "--disable-extensions",
            "--disable-background-networking",
            "--mute-audio",
            "--lang=pt-BR",
            initial_url
        ]

        if self.headless:
            if os.name != "nt":
                args.extend([
                    "--headless=new",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-software-rasterizer",
                    "--js-flags=--max-old-space-size=256",
                    "--window-size=1366,860"
                ])
            else:
                args.extend([
                    "--window-position=-32000,-32000",
                    "--window-size=1366,860"
                ])
        else:
            args.extend([
                "--window-size=1280,840",
                "--window-position=50,50"
            ])

        startupinfo = None
        creationflags = 0
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0 if self.headless else 1
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if self.headless else 0

        self.process = subprocess.Popen(
            args,
            startupinfo=startupinfo,
            creationflags=creationflags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.connect_cdp()
        self.handle_consent_and_wait()

    def start_browser(self, initial_url: str):
        self.ensure_browser(initial_url)

    def connect_cdp(self, timeout_sec: int = 25) -> bool:
        start_time = time.time()
        target_tab = None

        while time.time() - start_time < timeout_sec and not self.stop_requested:
            time.sleep(0.8)
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json", timeout=2) as resp:
                    tabs = json.loads(resp.read().decode("utf-8"))
                    for t in tabs:
                        if t.get("type") == "page":
                            target_tab = t
                            break
                    if target_tab:
                        break
            except Exception:
                pass

        if not target_tab:
            raise TimeoutError("Tempo limite esgotado ao conectar ao Chrome CDP.")

        ws_url = target_tab.get("webSocketDebuggerUrl")
        self.ws = websocket.create_connection(ws_url, timeout=15)
        self.log("Conexão com o motor do Google Maps estabelecida com sucesso.")
        return True

    def navigate(self, url: str):
        if not self.ws:
            return
        self._req_counter += 1
        req_id = self._req_counter
        payload = {
            "id": req_id,
            "method": "Page.navigate",
            "params": {"url": url}
        }
        try:
            self.ws.settimeout(8)
            self.ws.send(json.dumps(payload))
            start = time.time()
            while time.time() - start < 8:
                raw = self.ws.recv()
                resp = json.loads(raw)
                if resp.get("id") == req_id:
                    break
        except Exception:
            pass
        time.sleep(2.4)

    def eval_js(self, expression: str, timeout: int = 12) -> Any:
        if not self.ws:
            return None
        self._req_counter += 1
        req_id = self._req_counter
        payload = {
            "id": req_id,
            "method": "Runtime.evaluate",
            "params": {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True
            }
        }
        try:
            self.ws.settimeout(timeout)
            self.ws.send(json.dumps(payload))
            start = time.time()
            while time.time() - start < timeout:
                raw = self.ws.recv()
                resp = json.loads(raw)
                if resp.get("id") == req_id:
                    result = resp.get("result", {}).get("result", {})
                    return result.get("value")
            return None
        except Exception:
            return None

    def close(self):
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None

    def handle_consent_and_wait(self):
        time.sleep(1.5)
        self.eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const accept = btns.find(b => {
                const t = (b.innerText || '').toLowerCase();
                return t.includes('aceitar tudo') || t.includes('concordo') || t.includes('accept all');
            });
            if (accept) accept.click();
        })()
        """)
        time.sleep(0.8)

    def _extract_visible_cards(self) -> List[Dict[str, Any]]:
        """
        Extrai de forma ultra-rápida todos os cards visíveis na lista do Google Maps.
        Se algum card de empresa real não exibir o telefone direto na linha da listagem (.UsdlK),
        inspeciona até 2 cards por ciclo clicando neles com timeout seguro.
        """
        raw = self.eval_js("""
        (async () => {
            const cards = Array.from(document.querySelectorAll('div.Nv2PK'));
            const results = [];
            let clickedInCycle = 0;

            for (let i = 0; i < cards.length; i++) {
                const c = cards[i];
                const titleEl = c.querySelector('.qBF1Pd, .fontHeadlineSmall');
                const title = titleEl ? titleEl.innerText.trim() : '';
                if (!title) continue;

                const linkEl = c.querySelector('a.hfpxzc');
                const mapsUrl = linkEl ? linkEl.href : '';

                let website = null;
                const webBtn = c.querySelector('a[data-value="Website"], a.lcr4fd, a[aria-label*="site" i], a[aria-label*="website" i]');
                if (webBtn && webBtn.href && !webBtn.href.includes('google.com/maps')) {
                    website = webBtn.href;
                }

                const ratingEl = c.querySelector('.MW4etd');
                const rating = ratingEl ? ratingEl.innerText.trim() : null;

                const reviewsEl = c.querySelector('.UY7F9');
                const reviews = reviewsEl ? reviewsEl.innerText.trim().replace(/[()]/g, '') : null;

                const usdlkEl = c.querySelector('.UsdlK');
                let phone = usdlkEl ? usdlkEl.innerText.trim() : null;

                const lines = Array.from(c.querySelectorAll('.W4Efsd')).map(el => el.innerText.trim()).filter(Boolean);
                if (!phone) {
                    const fullText = c.innerText || '';
                    const m = fullText.match(/0?\\(?\\d{2}\\)?\\s*(?:9\\d{4}|\\d{4})[-.\\s]?\\d{4}/);
                    if (m) phone = m[0];
                }

                // Inspeciona clicando no card APENAS se ainda não tem telefone, não parece endereço puro e limite de 2 por ciclo
                const looksLikeBareAddr = /^(r\\.|rua |av\\.|avenida |al\\.|alameda |travessa |tr\\.)/i.test(title) && /,?\\s*\\d+/.test(title);
                const alreadyInspected = c.getAttribute('data-lh-inspected') === '1';

                if (!phone && !looksLikeBareAddr && !alreadyInspected && linkEl && clickedInCycle < 2) {
                    c.setAttribute('data-lh-inspected', '1');
                    clickedInCycle++;
                    try {
                        linkEl.click();
                        await new Promise(r => setTimeout(r, 420));
                        const phoneBtn = document.querySelector('button[data-item-id^="phone:"], button[aria-label*="Telefone" i], button[data-tooltip*="telefone" i]');
                        if (phoneBtn) {
                            const txt = (phoneBtn.getAttribute('aria-label') || '') + ' ' + (phoneBtn.innerText || '') + ' ' + (phoneBtn.getAttribute('data-item-id') || '');
                            const m = txt.match(/0?\\(?\\d{2}\\)?\\s*(?:9\\d{4}|\\d{4})[-.\\s]?\\d{4}/);
                            if (m) phone = m[0];
                        }
                        if (!website) {
                            const siteBtn = document.querySelector('a[data-item-id="authority"], a[aria-label*="Website" i], a[aria-label*="Site:" i]');
                            if (siteBtn && siteBtn.href && !siteBtn.href.includes('google.com/maps')) {
                                website = siteBtn.href;
                            }
                        }
                    } catch (e) {}
                }

                results.push({
                    name: title,
                    maps_url: mapsUrl,
                    website: website,
                    rating: rating,
                    reviews: reviews,
                    lines: lines,
                    phone: phone
                });
            }
            return results;
        })()
        """, timeout=12)
        return raw if isinstance(raw, list) else []

    def scrape_leads(
        self,
        query: str,
        niche: str = "",
        street: str = "",
        neighborhood: str = "",
        city: str = "",
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        target_limit: int = 50,
        place_type: str = "street",
        zoom: Optional[int] = None,
        on_lead_found: Optional[Callable[[Dict[str, Any]], None]] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        auto_close: bool = True,
        seen_urls: Optional[Set[str]] = None,
        seen_phones: Optional[Set[str]] = None,
        global_leads_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        leads_result: List[Dict[str, Any]] = []
        if seen_urls is None:
            seen_urls = set()
        if seen_phones is None:
            seen_phones = set()

        is_general = not niche or niche.strip().lower() in (
            "todos", "todos os negócios", "qualquer", "geral", "varredura total"
        )

        # Se for chamada direta sem nicho específico, usa o varredor completo de todos os negócios!
        if is_general and auto_close:
            return self.scrape_multi_segments(
                segments=SWEEP_ALL_TERMS,
                street=street,
                neighborhood=neighborhood,
                city=city,
                lat=lat,
                lon=lon,
                target_per_segment=target_limit,
                total_target_limit=target_limit,
                place_type=place_type,
                zoom=zoom,
                on_lead_found=on_lead_found,
                progress_callback=progress_callback
            )

        effective_query = build_maps_search_query(
            term=niche or query,
            street=street,
            neighborhood=neighborhood,
            city=city,
            place_type=place_type,
            fallback_query=query
        )
        encoded_query = urllib.parse.quote(effective_query)
        maps_url = f"https://www.google.com/maps/search/{encoded_query}?hl=pt-BR"

        try:
            self.log(f"Buscando no Google Maps: '{effective_query}'")
            self.ensure_browser(maps_url)

            # Aguarda os cards carregarem (até 3.5s)
            for _ in range(7):
                if self.stop_requested:
                    break
                cnt = self.eval_js('document.querySelectorAll("div.Nv2PK").length', timeout=4) or 0
                if cnt > 0:
                    break
                time.sleep(0.5)

            no_growth_count = 0
            last_card_count = 0
            scroll_attempts = 0
            max_scroll_attempts = max(12, min(35, target_limit))

            while len(leads_result) < target_limit and scroll_attempts < max_scroll_attempts and not self.stop_requested:
                scroll_attempts += 1

                raw_cards = self._extract_visible_cards()
                current_count = len(raw_cards)

                new_in_cycle = 0
                for c in raw_cards:
                    if self.stop_requested:
                        break

                    m_url = c.get("maps_url") or ""
                    name = (c.get("name") or "").strip()
                    if not name:
                        continue

                    # Ignora endereços puros (ex: "R. Jacuí, 1423 - Lj 2")
                    if is_bare_address_title(name, street):
                        continue

                    if m_url and m_url in seen_urls:
                        continue

                    lines_info = parse_card_lines(c.get("lines", []), name, direct_phone=c.get("phone"))
                    if not lines_info["is_whatsapp"] or not lines_info["clean_phone"]:
                        # Regra: Só pegar negócios com telefone válido para WhatsApp!
                        continue

                    clean_p = lines_info["clean_phone"]
                    phone_tail = clean_p[-8:]
                    if phone_tail in seen_phones:
                        if m_url:
                            seen_urls.add(m_url)
                        continue

                    if m_url:
                        seen_urls.add(m_url)
                    seen_phones.add(phone_tail)

                    web_type, clean_web = classify_website(c.get("website"))

                    rating_val = None
                    if c.get("rating"):
                        try:
                            rating_val = float(str(c["rating"]).replace(",", "."))
                        except Exception:
                            pass

                    rev_count = 0
                    if c.get("reviews"):
                        try:
                            clean_rev = re.sub(r"\D", "", str(c["reviews"]))
                            if clean_rev:
                                rev_count = int(clean_rev)
                        except Exception:
                            pass

                    lead = {
                        "name": name,
                        "category": lines_info["category"] or niche or "Comércio Local",
                        "address": lines_info["address"] or f"{street}, {neighborhood}, {city}".strip(", "),
                        "street": street,
                        "neighborhood": neighborhood or city or "Região",
                        "city": city,
                        "phone": lines_info["phone"],
                        "clean_phone": clean_p,
                        "is_whatsapp": True,
                        "phone_type": lines_info.get("phone_type", "mobile"),
                        "whatsapp_verified": lines_info.get("whatsapp_verified", 0),
                        "rating": rating_val,
                        "reviews_count": rev_count,
                        "website": clean_web,
                        "website_type": web_type,
                        "maps_url": m_url or f"https://www.google.com/maps/search/{urllib.parse.quote(name + ' ' + clean_p)}",
                        "search_query": effective_query
                    }

                    leads_result.append(lead)
                    new_in_cycle += 1
                    if global_leads_list is not None:
                        global_leads_list.append(lead)

                    if on_lead_found:
                        on_lead_found(lead)

                    if progress_callback:
                        ref_list = global_leads_list if global_leads_list is not None else leads_result
                        no_web_cnt = sum(1 for x in ref_list if x["website_type"] in ("none", "social", "directory"))
                        progress_callback({
                            "total_extracted": len(ref_list),
                            "no_website_count": no_web_cnt,
                            "current_item": name,
                            "website_type": web_type,
                            "has_whatsapp": True
                        })

                    if len(leads_result) >= target_limit:
                        break

                if len(leads_result) >= target_limit:
                    break

                # Verifica se chegou ao fim da lista no Google Maps
                is_end = self.eval_js("!!document.querySelector('.HlvSq, .PbZDve')", timeout=4)
                if is_end and new_in_cycle == 0:
                    break

                if new_in_cycle == 0:
                    no_growth_count += 1
                    if no_growth_count >= 2:
                        break
                else:
                    no_growth_count = 0
                last_card_count = current_count

                # Rola o feed para carregar mais resultados
                self.eval_js("""
                (() => {
                    const feed = document.querySelector('div[role="feed"]');
                    if (feed) {
                        feed.scrollBy(0, 1400);
                        feed.scrollTop = feed.scrollHeight;
                    } else {
                        window.scrollTo(0, document.body.scrollHeight);
                    }
                })()
                """, timeout=5)
                time.sleep(1.3)

            return leads_result
        finally:
            if auto_close:
                self.close()

    def scrape_multi_segments(
        self,
        segments: List[str],
        street: str = "",
        neighborhood: str = "",
        city: str = "",
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        target_per_segment: int = 25,
        total_target_limit: Optional[int] = None,
        place_type: str = "street",
        zoom: Optional[int] = None,
        on_lead_found: Optional[Callable[[Dict[str, Any]], None]] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_segment_change: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Varredura Contínua Multi-Termos / Rua Toda:
        Mantém o mesmo navegador aberto e varre todos os tipos de negócios com telefone válido
        ao longo da rua, bairro ou cidade, sem travar no primeiro segmento.
        """
        self.stop_requested = False
        all_leads: List[Dict[str, Any]] = []
        seen_urls: Set[str] = set()
        seen_phones: Set[str] = set()

        effective_segments = segments if segments else SWEEP_ALL_TERMS
        total_segments = len(effective_segments)

        # Se total_target_limit não foi passado, calcula meta global generosa
        global_goal = total_target_limit or max(target_per_segment * total_segments, 60)

        try:
            for idx, seg in enumerate(effective_segments, 1):
                if self.stop_requested:
                    self.log("Varredura interrompida pelo usuário.")
                    break

                if len(all_leads) >= global_goal:
                    self.log(f"Meta global de {global_goal} negócios com WhatsApp válido atingida!")
                    break

                remaining_goal = global_goal - len(all_leads)
                per_seg_limit = min(target_per_segment, remaining_goal) if total_target_limit else target_per_segment

                self.log(f"🔎 Varrendo [{idx}/{total_segments}]: '{seg}' ({len(all_leads)} negócios c/ telefone capturados)...")
                if on_segment_change:
                    on_segment_change(idx, total_segments, seg)

                leads_seg = self.scrape_leads(
                    query=seg,
                    niche=seg,
                    street=street,
                    neighborhood=neighborhood,
                    city=city,
                    lat=lat,
                    lon=lon,
                    target_limit=per_seg_limit,
                    place_type=place_type,
                    zoom=zoom,
                    on_lead_found=on_lead_found,
                    progress_callback=progress_callback,
                    auto_close=False,
                    seen_urls=seen_urls,
                    seen_phones=seen_phones,
                    global_leads_list=all_leads
                )
                if leads_seg:
                    self.log(f"  ✓ +{len(leads_seg)} novos negócios com telefone válido em '{seg}' (Total: {len(all_leads)}).")
                time.sleep(0.6)

            self.log(f"🎉 Varredura concluída! Total de {len(all_leads)} negócios únicos com telefone válido encontrados.")
            return all_leads
        finally:
            self.close()
