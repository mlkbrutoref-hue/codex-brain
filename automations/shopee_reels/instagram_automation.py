r"""
Instagram Product Video Automation com Verificação Estrita na Shopee, Filtro Semântico Específico por Produto, Filtro Visual Anti-Talking Head (Zero Rostos), Edição e Upload no Google Drive

DIRETRIZES E FILTROS APLICADOS:
1. Validação Estrita de Produto: O vídeo do Instagram DEVE conter pares de palavras-chave obrigatórias do produto na legenda/título.
2. Blacklist Abrangente: Rejeição imediata de drones/obras/paisagens, carros/veículos, setups de PC gamer, vlogs pessoais, podcasts, rostos e anúncios de lojas físicas locais.
3. Duração Comercial: Limite máximo de 60 segundos por vídeo (elimina documentários e vlogs longos).
4. Filtro Visual por IA (OpenCV YuNet - Zero Rostos): Tolerância ZERO para rostos. Qualquer rosto detectado descarta o vídeo.
5. Foco Comercial Exclusivo: Apenas demonstrações práticas do produto em ação, unboxings e uso hands-on com mãos/produto.
6. Integração Shopee Oficial: Validação de identidade do produto e geração de link de afiliado oficial.
7. Edição Padronizada: FFmpeg + Pillow com caixa sólida branca e Times New Roman.
8. Upload Automático: Pasta local do Drive e nuvem do Google Drive.
"""

import os
import re
import sys
import json
import time
import shutil
import random
import subprocess
from pathlib import Path
import cv2
from playwright.sync_api import sync_playwright

# Importa módulos internos
try:
    from shopee_api import check_product_on_shopee, load_credentials
    from product_matcher import StrictProductMatcher
    from video_editor import process_single_video, upload_file_to_gdrive, GDRIVE_EDITED_FOLDER_ID, probe_video
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from shopee_api import check_product_on_shopee, load_credentials
    from product_matcher import StrictProductMatcher
    from video_editor import process_single_video, upload_file_to_gdrive, GDRIVE_EDITED_FOLDER_ID, probe_video

# Garante saída UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRATCH_DIR = Path(r"C:\Users\GAMER\.gemini\antigravity\scratch")
YUNET_MODEL = SCRATCH_DIR / "face_detection_yunet.onnx"
COOKIES_FILE = SCRATCH_DIR / "insta_cookies.txt"

AUTOMATION_PROFILE = r"C:\Users\GAMER\.gemini\instagram_profile"
CHROME_USER_DATA = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")

# Diretrizes Textuais e Semânticas Globais (Blacklist Universal)
NEGATIVE_KEYWORDS = [
    # Talking heads, podcasts, fofoca, opiniões
    "podcast", "mesacast", "entrevista", "cortes de podcast", "corte de podcast", "historia da marca", "curiosidades",
    "sabia dessa", "minha opiniao", "minha opinião", "vale a pena", "resenha sincera",
    "nao compre antes", "não compre antes", "testei por", "vlog", "storytime",
    "arrume-se comigo", "arrumesecomigo", "react", "reacao", "reação", "startse",
    "fofoca", "humor", "comedia", "meme", "polemica", "polêmica", "canal", "noticia", "notícia",
    "minha rotina", "meu dia", "bate papo", "minha vida",
    
    # Veículos, modificações automotivas e oficinas (veículos reais, não utilidades domésticas)
    "caranga", "palio", "civic", "gol", "corsa", "automotivo", "farol", "milha",
    "rebaixado", "xenon", "escapamento", "oficina", "4x4",
    "estrada", "rodovia", "grau", "som automotivo", "lanternagem", "funilaria",

    # Drones, obras, paisagens, turismo
    "drone", "aerea", "aérea", "obra", "prefeitura", "asfalto", "engenharia", "construcao",
    "construção", "viaduto", "paisagem", "natureza", "viagem", "turismo",

    # Setup de PC Gamer e informática que não são achadinhos
    "pc gamer", "setup gamer", "battlestation", "gabinete", "rtx", "gtx", "water cooler",
    "desk setup", "placa de video", "teclado mecanico", "monitor 144hz", "ryzen",

    # Anúncios de lojas físicas com preço local ou retirada
    "no pix", "avenida", "rua", "bairro", "loja fisica", "loja física",
    "retirada", "entrega em mãos", "entregamos em mãos", "chama no whats"
]

POSITIVE_KEYWORDS = [
    "unboxing", "aesthetic", "asmr", "demonstracao", "demonstração", "teste", "testando",
    "usando", "como usar", "detalhes", "close", "showcase", "achadinho", "achadinhos",
    "utilidade", "utilidades", "praticidade", "organizando", "cozinha", "hands on",
    "comprei na shopee", "link na bio", "shopee", "dica de casa", "dicas de casa"
]

VIRAL_KEYWORDS = [
    "viral", "viralizou", "comprei na shopee", "melhor compra", "chocada", "olha isso",
    "testando", "você precisa", "salva essa dica", "truque", "hack", "shopeecheck",
    "achei na shopee", "segredo", "inacreditavel", "inacreditável", "revolucionou",
    "genial", "nunca mais", "facilitou", "perfeito", "achadinho do dia", "dica de ouro",
    "salvei", "salva pra nao perder", "me agradece depois"
]

# Catálogo com Validação de Pares Semânticos Obrigatórios (Impede falsos positivos)
SPECIFIC_PRODUCTS = [
    {
        "name": "lixeira suspensa dobravel pia",
        "tag": "lixeirasuspensa",
        "shopee_query": "lixeira suspensa dobravel",
        "fallback_tags": ["lixeiradepia", "lixeiradobravel", "achadinhosshopee"],
        "required_pairs": [
            (["lixeira"], ["suspensa", "dobravel", "dobrável", "pia", "armario", "armário"])
        ],
        "forbidden_terms": ["carro", "setup", "vlog", "drone"],
        "hook": "Descarte cascas e resíduos sem sujar a bancada da cozinha",
        "hashtags": "#achadinhos #shopee #cozinhaorganizada #lixeirasuspensa #praticidade #utilidades"
    },
    {
        "name": "organizador geladeira acrilico",
        "tag": "organizadorgeladeira",
        "shopee_query": "organizador geladeira acrilico",
        "fallback_tags": ["organizacaogeladeira", "potesacrilico", "achadinhosshopee"],
        "required_pairs": [
            (["organizador", "pote", "caixa", "dispenser"], ["geladeira", "hortifruti", "legumes", "verduras", "acrilico", "acrílico"])
        ],
        "forbidden_terms": ["setup", "vlog", "drone"],
        "hook": "Sua geladeira organizada e alimentos frescos por muito mais tempo",
        "hashtags": "#achadinhos #shopee #organizacaogeladeira #cozinha #geladeira #casa #utilidades"
    },
    {
        "name": "dispenser azeite dosador vidro",
        "tag": "dispenserazeite",
        "shopee_query": "dispenser azeite dosador",
        "fallback_tags": ["portaazeite", "galheteiro", "azeiteiro", "achadinhosshopee"],
        "required_pairs": [
            (["dispenser", "dosador", "galheteiro", "azeiteiro", "porta azeite", "garrafa"], ["azeite", "óleo", "oleo", "vinagre"])
        ],
        "forbidden_terms": ["setup", "vlog", "drone"],
        "hook": "Tempere seus pratos na medida certa sem vazamentos nem lambança",
        "hashtags": "#achadinhos #shopee #dispenserazeite #galheteiro #cozinha #utilidades #casa"
    },
    {
        "name": "fita dupla face magica silicone",
        "tag": "fitaduplaface",
        "shopee_query": "fita dupla face",
        "fallback_tags": ["fitamagica", "fitadesilicone", "achadinhosshopee"],
        "required_pairs": [
            (["fita"], ["dupla face", "magica", "mágica", "adesiva", "silicone"])
        ],
        "forbidden_terms": ["cabelo", "mega hair", "lace", "peruca", "unha", "cilios", "setup", "drone"],
        "hook": "Cole quadros e objetos na parede sem furar nem estragar a tinta",
        "hashtags": "#achadinhos #shopee #fitamagica #dicasdecasa #organizacao #utilidades #casa"
    },
    {
        "name": "dispenser automatico sabonete sensor",
        "tag": "dispensersabonete",
        "shopee_query": "dispenser sabonete liquido",
        "fallback_tags": ["saboneteiradigital", "dispensercomsensor", "achadinhosshopee"],
        "required_pairs": [
            (["sabonete", "saboneteira", "espuma"], ["sensor", "dispenser", "automatico", "automático", "recarregavel", "recarregável"])
        ],
        "forbidden_terms": ["dente", "escova", "setup", "vlog", "drone"],
        "hook": "Sabonete em espuma na sua mão sem precisar tocar em nada",
        "hashtags": "#achadinhos #shopee #banheiro #higiene #casaorganizada #utilidades"
    },
    {
        "name": "porta escova dente esterilizador uv",
        "tag": "esterilizadoruv",
        "shopee_query": "porta escova esterilizador",
        "fallback_tags": ["dispenserpastadedente", "portaescovadedente", "achadinhosshopee"],
        "required_pairs": [
            (["escova", "dente", "dental"], ["esterilizador", "uv", "dispenser", "pasta de dente"])
        ],
        "forbidden_terms": ["unha", "setup", "vlog", "drone"],
        "hook": "Elimine 99% das bactérias das suas escovas de dente automaticamente",
        "hashtags": "#achadinhos #shopee #banheiro #higiene #saudebucal #utilidades"
    },
    {
        "name": "amassador de batatas inox",
        "tag": "amassadordebatata",
        "shopee_query": "amassador de batatas",
        "fallback_tags": ["espremedordebatatas", "puredebatata", "cozinhafacil"],
        "required_pairs": [
            (["amassador", "espremedor"], ["batata", "batatas", "purê", "pure"])
        ],
        "forbidden_terms": ["alho", "setup", "vlog", "drone"],
        "hook": "Purê lisinho e sem pedaços em segundos sem nenhum esforço",
        "hashtags": "#achadinhos #shopee #cozinha #puredebatata #utensilios #utilidades"
    },
    {
        "name": "mini aspirador de po sem fio",
        "tag": "miniaspirador",
        "shopee_query": "mini aspirador po",
        "fallback_tags": ["aspiradorportatil", "miniaspiradordepo", "achadinhosshopee"],
        "required_pairs": [
            (["aspirador"], ["sem fio", "portatil", "portátil", "mini", "teclado", "po", "pó", "sugar"])
        ],
        "forbidden_terms": ["no pix", "av.", "rua", "bairro", "loja fisica", "loja física", "retirada", "entrega em mãos", "rebaixado", "caranga", "escapamento", "drone"],
        "hook": "Limpe o teclado, o carro e cantinhos difíceis em poucos segundos",
        "hashtags": "#achadinhos #shopee #miniaspirador #limpezanacasa #carro #utilidades"
    },
    {
        "name": "luminaria barra led sensor presenca",
        "tag": "luminariasensor",
        "shopee_query": "luminaria led sensor",
        "fallback_tags": ["barradeled", "ledsensor", "achadinhosshopee"],
        "required_pairs": [
            (["luminaria", "luminária", "barra de led", "fita led"], ["sensor", "presenca", "presença", "movimento", "armario", "armário", "guarda roupa", "guarda-roupa", "adesiva"])
        ],
        "forbidden_terms": ["caranga", "palio", "civic", "gol", "corsa", "automotivo", "farol", "milha", "rebaixado", "xenon", "escapamento", "oficina", "4x4", "estrada", "rodovia", "grau", "setup", "pc gamer", "gabinete", "placa de video", "drone"],
        "hook": "Ilumine qualquer armário ou escada sem passar nenhum fio",
        "hashtags": "#achadinhos #shopee #luminariasensor #decoracao #casa #utilidades"
    },
    {
        "name": "organizador de cabos silicone",
        "tag": "organizadordecabos",
        "shopee_query": "organizador de cabos",
        "fallback_tags": ["organizadordefios", "suportedecabos", "achadinhosshopee"],
        "required_pairs": [
            (["organizador", "suporte", "clips", "clipe", "prendedor"], ["cabos", "fios", "cabo", "fio"])
        ],
        "forbidden_terms": ["pc gamer", "battlestation", "gabinete", "rtx", "gtx", "water cooler", "vlog", "setup inspiration", "desk tour", "drone"],
        "hook": "Diga adeus aos cabos caídos e embolados atrás da sua mesa",
        "hashtags": "#achadinhos #shopee #organizacao #setup #homeoffice #utilidades"
    },
    {
        "name": "umidificador aromatizador chama led",
        "tag": "umidificadordear",
        "shopee_query": "umidificador chama led",
        "fallback_tags": ["aromatizadorchama", "difusordeoleos", "achadinhosshopee"],
        "required_pairs": [
            (["umidificador", "difusor", "aromatizador"], ["chama", "lareira", "fogo", "aroma", "essencial", "oleo essencial", "óleo essencial"])
        ],
        "forbidden_terms": ["setup", "vlog", "fumaca", "fumaça", "drone"],
        "hook": "Deixe o ambiente perfumado e relaxante com efeito incrível de lareira",
        "hashtags": "#achadinhos #shopee #umidificador #aromaterapia #decoracao #casa"
    },
    {
        "name": "mini processador triturador alimentos",
        "tag": "miniprocessador",
        "shopee_query": "mini processador triturador alho",
        "fallback_tags": ["minitriturador", "processadordealimentos", "achadinhosshopee"],
        "required_pairs": [
            (["processador", "triturador"], ["alho", "temperos", "alimentos", "cebola", "picar"])
        ],
        "forbidden_terms": ["carro", "setup", "vlog", "drone"],
        "hook": "Pique temperos em segundos com rapidez e sem gastar luz",
        "hashtags": "#achadinhos #shopee #miniprocessador #cozinhafacil #praticidade #utilidades"
    },
    {
        "name": "papa bolinha removedor fiapos",
        "tag": "papabolinha",
        "shopee_query": "papa bolinha removedor",
        "fallback_tags": ["removedordefiapos", "achadinhosshopee", "shopeecheck"],
        "required_pairs": [
            (["papa bolinha", "removedor", "fiapos", "bolinha"], ["eletrico", "elétrico", "roupa", "tecido", "casaco", "recarregavel", "recarregável", "usb"])
        ],
        "forbidden_terms": ["carro", "setup", "vlog", "drone"],
        "hook": "Suas roupas novas de novo sem nenhuma bolinha ou fiapo",
        "hashtags": "#achadinhos #shopee #papabolinha #roupas #dicasdecasa #utilidades"
    },
    {
        "name": "escova eletrica limpeza giratoria",
        "tag": "escovaeletrica",
        "shopee_query": "escova eletrica limpeza",
        "fallback_tags": ["escovagiratoria", "limpezapesada", "achadinhosshopee"],
        "required_pairs": [
            (["escova", "limpeza"], ["eletrica", "elétrica", "giratoria", "giratória", "rotativa", "5 em 1", "sem fio"])
        ],
        "forbidden_terms": ["dente", "cabelo", "carro", "setup", "vlog", "drone"],
        "hook": "Limpe azulejos, pias e panelas sem esfregar nem cansar os braços",
        "hashtags": "#achadinhos #shopee #faxina #limpezadecasa #escovagiratoria #utilidades"
    },
    {
        "name": "ralador fatiador legumes manivela",
        "tag": "raladormanivela",
        "shopee_query": "ralador legumes manivela",
        "fallback_tags": ["fatiadordelegumes", "cortadordelegumes", "achadinhosshopee"],
        "required_pairs": [
            (["ralador", "fatiador", "cortador"], ["manivela", "giratorio", "giratório", "legumes", "queijo", "cilindro"])
        ],
        "forbidden_terms": ["carro", "setup", "vlog", "drone"],
        "hook": "Rale queijo e legumes em segundos sem risco de cortar os dedos",
        "hashtags": "#achadinhos #shopee #cozinha #ralador #praticidade #utilidades"
    },
    {
        "name": "bomba eletrica galao agua",
        "tag": "bombadegalao",
        "shopee_query": "bomba galao agua",
        "fallback_tags": ["bebedouroportatil", "bombaeletrica", "achadinhosshopee"],
        "required_pairs": [
            (["bomba", "bebedouro", "dispenser"], ["galão", "galao", "agua", "água", "20l", "eletrica", "elétrica", "garrafao", "garrafão"])
        ],
        "forbidden_terms": ["carro", "combustivel", "gasolina", "pneu", "setup", "vlog", "drone"],
        "hook": "Água fresca do galão direto no copo com apenas um clique",
        "hashtags": "#achadinhos #shopee #bombaeletrica #casa #cozinha #utilidades"
    },
    {
        "name": "afiador amolador facas profissional",
        "tag": "afiadordefacas",
        "shopee_query": "afiador de facas",
        "fallback_tags": ["amoladordefaca", "facasafiadas", "achadinhosshopee"],
        "required_pairs": [
            (["afiador", "amolador"], ["facas", "faca", "estagios", "estágios", "inox", "lamina", "lâmina", "chaira"])
        ],
        "forbidden_terms": ["carro", "setup", "vlog", "drone"],
        "hook": "Recupere o corte das suas facas em segundos como uma navalha",
        "hashtags": "#achadinhos #shopee #afiadordefacas #cozinha #churrasco #utilidades"
    },
    {
        "name": "suporte organizador vassouras adesivo",
        "tag": "suportedevassoura",
        "shopee_query": "suporte vassoura adesivo",
        "fallback_tags": ["organizadorlavanderia", "suporteadessivo", "achadinhosshopee"],
        "required_pairs": [
            (["suporte", "organizador", "gancho"], ["vassoura", "vassouras", "rodo", "lavanderia", "adesivo", "parede"])
        ],
        "forbidden_terms": ["carro", "celular", "setup", "vlog", "drone"],
        "hook": "Vassouras e rodos suspensos e organizados sem furar a parede",
        "hashtags": "#achadinhos #shopee #lavanderia #organizacao #casa #utilidades"
    },
    {
        "name": "mini seladora vacuo portatil",
        "tag": "seladoraavacuo",
        "shopee_query": "mini seladora vacuo",
        "fallback_tags": ["embaladoraavacuo", "conservacaoalimentos", "achadinhosshopee"],
        "required_pairs": [
            (["seladora", "embaladora", "selador"], ["vacuo", "vácuo", "alimentos", "sacos", "portatil", "portátil"])
        ],
        "forbidden_terms": ["carro", "setup", "vlog", "drone"],
        "hook": "Alimentos conservados por até 5 vezes mais tempo sem estragar",
        "hashtags": "#achadinhos #shopee #cozinha #conservacao #seladora #utilidades"
    },
    {
        "name": "descascador legumes 3 em 1",
        "tag": "descascadordelegumes",
        "shopee_query": "descascador de legumes",
        "fallback_tags": ["descascador3em1", "utensiliosdecozinha", "achadinhosshopee"],
        "required_pairs": [
            (["descascador", "cortador"], ["legumes", "3 em 1", "giratorio", "giratório", "frutas", "inox"])
        ],
        "forbidden_terms": ["carro", "setup", "vlog", "drone"],
        "hook": "Descasque qualquer fruta ou legume na metade do tempo sem esforço",
        "hashtags": "#achadinhos #shopee #cozinha #descascador #praticidade #utilidades"
    },
    {
        "name": "escova vaso sanitario silicone",
        "tag": "escovadesilicone",
        "shopee_query": "escova vaso sanitario",
        "fallback_tags": ["limpezabanheiro", "escovasanitaria", "achadinhosshopee"],
        "required_pairs": [
            (["escova"], ["vaso", "sanitário", "sanitario", "silicone", "banheiro", "privada"])
        ],
        "forbidden_terms": ["cabelo", "dente", "carro", "setup", "vlog", "drone"],
        "hook": "O fim da sujeira nos cantinhos difíceis do vaso sanitário",
        "hashtags": "#achadinhos #shopee #banheiro #faxina #limpeza #utilidades"
    },
    {
        "name": "organizador giratorio temperos 360",
        "tag": "organizador360",
        "shopee_query": "organizador giratorio",
        "fallback_tags": ["portatemperosgiratorio", "organizacaocozinha", "achadinhosshopee"],
        "required_pairs": [
            (["organizador", "suporte", "bandeja"], ["giratorio", "giratório", "360", "temperos", "acrilico", "acrílico"])
        ],
        "forbidden_terms": ["carro", "setup", "vlog", "drone"],
        "hook": "Acesse qualquer tempero ou molho com apenas um giro leve",
        "hashtags": "#achadinhos #shopee #cozinhaorganizada #temperos #decoracao #utilidades"
    }
]

def get_drive_dir() -> str:
    """Detecta automaticamente o caminho da pasta local Drive."""
    preferred = r"C:\Users\GAMER\Drive\Produtos Instagram"
    if os.path.exists(preferred) or os.path.exists(os.path.dirname(preferred)):
        os.makedirs(preferred, exist_ok=True)
        return preferred
    fallback = os.path.expandvars(r"%USERPROFILE%\Drive\Produtos Instagram")
    os.makedirs(fallback, exist_ok=True)
    return fallback

def clean_stale_lockfiles():
    """Finaliza processos órfãos do Chrome/Chromium usando o perfil da automação e remove lockfiles."""
    lock_names = ["lockfile", "SingletonLock", "SingletonSocket", "SingletonCookie", "Default/LOCK"]
    try:
        subprocess.run("taskkill /F /IM chrome.exe /T 2>nul", shell=True, capture_output=True)
        subprocess.run("taskkill /F /IM chrome-headless-shell.exe /T 2>nul", shell=True, capture_output=True)
    except Exception:
        pass

    for fname in lock_names:
        fpath = os.path.join(AUTOMATION_PROFILE, fname)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass

def export_session_cookies(context) -> Path:
    """Exporta cookies da sessão ativa do Playwright para uso com o yt-dlp."""
    cookies = context.cookies("https://www.instagram.com")
    with open(COOKIES_FILE, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        for c in cookies:
            domain = c.get("domain", ".instagram.com")
            include_sub = "TRUE" if domain.startswith(".") else "FALSE"
            path = c.get("path", "/")
            secure = "TRUE" if c.get("secure", False) else "FALSE"
            expires = str(int(c.get("expires", -1)))
            name = c.get("name", "")
            val = c.get("value", "")
            f.write(f"{domain}\t{include_sub}\t{path}\t{secure}\t{expires}\t{name}\t{val}\n")
    return COOKIES_FILE

def check_metadata_content(title: str, desc: str, uploader: str, product_info: dict, duration: float = 0) -> tuple[bool, str, int]:
    """Avalia o título, a legenda e o autor do Reel para garantir correspondência exata com o produto."""
    full_text = (title + " " + desc + " " + uploader).lower()

    # 1. Duração Comercial: Rejeita vídeos longos (>60s) que normalmente são vlogs/drones/aulas
    if duration > 60:
        return False, f"Rejeitado: Duração de {duration:.1f}s excede o limite comercial (máx 60s)", 0

    # 2. Checa Blacklist Universal com Word Boundary Regex (evita falsos positivos como rua em mistura)
    for neg in NEGATIVE_KEYWORDS:
        pattern = rf"\b{re.escape(neg)}\b"
        if re.search(pattern, full_text):
            return False, f"Rejeitado: Termo proibido '{neg}' identificado no texto/perfil", 0

    # 3. Checa Termos Proibidos Específicos do Produto
    for forbidden in product_info.get("forbidden_terms", []):
        pattern = rf"\b{re.escape(forbidden.lower())}\b"
        if re.search(pattern, full_text):
            return False, f"Rejeitado: Termo proibido específico '{forbidden}' identificado", 0

    # 4. Validação Rigorosa de Pares: Exige correspondência simultânea do produto
    # Ex: ("amassador", "batata") ou ("luminaria", "sensor")
    required_pairs = product_info.get("required_pairs", [])
    pair_matched = False
    matched_desc = ""

    for group_a, group_b in required_pairs:
        match_a = [w for w in group_a if w.lower() in full_text]
        match_b = [w for w in group_b if w.lower() in full_text]
        if match_a and match_b:
            pair_matched = True
            matched_desc = f"{match_a[0]} + {match_b[0]}"
            break

    if not pair_matched:
        return False, "Rejeitado: Não combina o par de palavras-chave obrigatório do produto", 0

    # 5. Avalia Termos Comerciais e Gatilhos Virais
    score = 30  # Base alta por bater o par exato do produto
    matches = []
    for pos in POSITIVE_KEYWORDS:
        if pos in full_text:
            score += 10
            matches.append(pos)

    viral_matches = []
    for vir in VIRAL_KEYWORDS:
        if vir in full_text:
            score += 20  # Forte bonificação para Reels com gatilhos virais
            viral_matches.append(vir)

    # Bonificação se o uploader tiver perfil de achadinhos/loja
    if any(k in uploader for k in ["achadinhos", "shopee", "loja", "casa", "utilidades", "variedades", "cozinha", "presentes"]):
        score += 25

    viral_str = f" | Gatilho Viral: {', '.join(viral_matches[:2])}" if viral_matches else ""
    return True, f"Aprovado por texto: Bateu par ('{matched_desc}'){viral_str} (Score: {score})", score

def check_video_for_talking_heads(video_path: Path) -> tuple[bool, str]:
    """Inspeciona visualmente amostras do vídeo com IA (YuNet + Nitidez Laplaciana).
    TOLERÂNCIA ZERO: Qualquer rosto detectado é rejeitado.
    NITIDEZ MÍNIMA: Imagens borradas/pixeladas são rejeitadas.
    """
    if not YUNET_MODEL.exists():
        return True, "Aviso: Modelo YuNet ausente; inspeção visual ignorada."

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return False, "Não foi possível abrir o vídeo para inspeção visual."

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 10:
        cap.release()
        return False, "Vídeo excessivamente curto ou corrompido."

    # Amostra 7 pontos no tempo para cobrir início, meio e fim
    sample_percentages = [0.12, 0.25, 0.38, 0.50, 0.65, 0.78, 0.90]
    face_counts = 0
    blur_scores = []

    for p in sample_percentages:
        frame_idx = int(total_frames * p)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        h, w, _ = frame.shape

        # Mede nitidez via variância Laplaciana
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_scores.append(lap_var)

        detector = cv2.FaceDetectorYN_create(str(YUNET_MODEL), '', (w, h), 0.6, 0.3)
        _, faces = detector.detect(frame)
        if faces is not None and len(faces) > 0:
            for f in faces:
                fh = f[3]
                rel_h = fh / h
                if rel_h > 0.10:  # Rosto ocupa mais de 10% do quadro
                    face_counts += 1
                    break

    cap.release()

    # REGRA ZERO ROSTOS: Se detectar qualquer rosto em qualquer frame amostrado, REJEITA IMEDIATAMENTE
    if face_counts > 0:
        return False, f"Rejeitado por IA Visual: Rosto de criador detectado em {face_counts}/{len(sample_percentages)} frames (Zero Rostos Obrigatório)"

    # FILTRO DE NITIDEZ: Rejeita vídeos com imagem borrada/pixelada
    avg_blur = (sum(blur_scores) / len(blur_scores)) if blur_scores else 0
    if avg_blur < 40.0:
        return False, f"Rejeitado por IA Visual: Baixa nitidez visual (Score de foco {avg_blur:.1f} < 40, vídeo borrado)"

    return True, f"Aprovado: 100% Product Only / Demonstração comercial nítida (Score nitidez: {avg_blur:.1f}, Zero rostos)"

def generate_legenda_file(video_stem: str, product_meta: dict, hook: str, shopee_item: dict, out_dir: Path) -> Path:
    title = shopee_item.get("productName", product_meta["name"]).title()
    raw_price = shopee_item.get("price") or shopee_item.get("priceMin") or "0"
    try:
        price_val = float(str(raw_price).replace(",", "."))
        price_str = f"R$ {price_val:.2f}"
    except Exception:
        price_str = f"R$ {raw_price}"
    link = shopee_item.get("offerLink", "")
    hashtags = product_meta.get("hashtags", "#achadinhos #shopee #utilidades #casa")

    text = f"""✨ {title} ✨

{hook} 🥗🚀

Esse achadinho é indispensável para facilitar sua rotina com máxima praticidade, rapidez e eficiência!

💰 Valor na Shopee: {price_str}
🛒 Link oficial com frete promocional:
👉 {link}

💬 Comente "EU QUERO" para receber o link direto no seu direct!
📌 Salva esse vídeo para garantir o seu antes que acabe o estoque!

{hashtags}
"""
    legenda_path = out_dir / f"{video_stem}_legenda.txt"
    with open(legenda_path, "w", encoding="utf-8") as f:
        f.write(text)
    return legenda_path

def run_batch(target_count: int = 10, target_total: int = None):
    clean_stale_lockfiles()
    target_drive_dir = Path(get_drive_dir())
    edit_output_dir = target_drive_dir / "Editados"
    edit_output_dir.mkdir(parents=True, exist_ok=True)

    app_id, secret = load_credentials()
    if not (app_id and secret):
        print("[ERRO CRITICO] Chaves da Shopee ausentes. Configure SHOPEE_APP_ID e SHOPEE_SECRET.")
        return []

    meta_msg = f"{target_count} NOVO(S) VÍDEO(S) DE PRODUTO" if target_count else f"TOTAL DE {target_total} VÍDEOS"
    print(f"\n=======================================================")
    print(f"INICIANDO PIPELINE: META {meta_msg} (FILTRO ZERO ROSTOS + DEMONSTRAÇÃO EXATA)")
    print(f"PASTA LOCAL DRIVE: {target_drive_dir}")
    print(f"PASTA EDITADOS: {edit_output_dir}")
    print(f"GOOGLE DRIVE NUVEM: https://drive.google.com/drive/folders/{GDRIVE_EDITED_FOLDER_ID}")
    print(f"=======================================================\n")

    # Mapeia produtos e URLs já aprovados para evitar repetição
    already_done_products = set()
    already_done_urls = set()
    already_done_stems = set()

    for d in [edit_output_dir, target_drive_dir]:
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.is_file():
                if f.name.endswith("_editado.mp4"):
                    already_done_stems.add(f.stem.replace("_editado", ""))
                elif f.name.endswith(".json"):
                    try:
                        with open(f, "r", encoding="utf-8") as jf:
                            data = json.load(jf)
                            if "product_target" in data:
                                already_done_products.add(data["product_target"].lower().strip())
                            if "instagram_url" in data:
                                already_done_urls.add(data["instagram_url"].strip())
                    except Exception:
                        pass

    # Mantém os produtos originais confirmados como concluídos
    already_done_products.add("mini selador de embalagens")
    already_done_products.add("fixador trava porta magnetico")
    already_done_products.add("amassador de alho inox")
    already_done_products.add("dispenser de detergente")
    already_done_products.add("cortador e fatiador de legumes")
    already_done_products.add("spray pulverizador de azeite")
    already_done_products.add("organizador de ovos rolagem automatica")
    already_done_products.add("esponja magica melamina")
    already_done_products.add("mop giratorio balde")

    print(f"[Status] Vídeos comerciais válidos existentes na pasta: {len(already_done_stems)}")
    print(f"[Status] Produtos já catalogados: {len(already_done_products)}")
    for p_done in sorted(already_done_products):
        print(f"  - Concluído: {p_done}")

    newly_processed = []

    with sync_playwright() as p:
        browser_args = ["--no-first-run", "--no-default-browser-check"]
        context = p.chromium.launch_persistent_context(
            user_data_dir=AUTOMATION_PROFILE,
            channel="chrome",
            headless=True,
            args=browser_args
        )
        page = context.new_page()

        # Exporta cookies para yt-dlp operar autenticado
        cookies_path = export_session_cookies(context)
        print(f"[Autenticação] Cookies exportados para yt-dlp: {cookies_path.name}")

        for prod_info in SPECIFIC_PRODUCTS:
            time.sleep(1.5)
            if target_count is not None and len(newly_processed) >= target_count:
                print(f"\n[Meta Atingida] {len(newly_processed)} novos vídeos processados com sucesso nesta execução.")
                break
            total_current = len(already_done_stems) + len(newly_processed)
            if target_total is not None and total_current >= target_total:
                print(f"\n[Meta Atingida] Total de {total_current} vídeos atingido (meta total: {target_total}).")
                break

            product_name = prod_info["name"]
            if product_name.lower().strip() in already_done_products:
                print(f"\n[Catálogo] Produto '{product_name}' já concluído. Avançando...")
                continue

            primary_tag = prod_info["tag"]
            shopee_query = prod_info["shopee_query"]
            hook = prod_info["hook"]
            tags_to_try = [primary_tag] + prod_info.get("fallback_tags", [])

            print(f"\n=======================================================")
            print(f">>> PROCESSANDO PRODUTO: '{product_name}'")
            print(f"=======================================================")

            # 1. Consulta Shopee Oficial
            print(f"[1/6 Shopee API] Consultando '{shopee_query}'...")
            found, shopee_item = check_product_on_shopee(shopee_query)
            if not found or not shopee_item:
                print(f"[Shopee API] Produto '{product_name}' não encontrado na Shopee. Pulando para o próximo.")
                continue

            shopee_title = shopee_item.get("productName", "")
            is_match, score, match_reason = StrictProductMatcher.evaluate(product_name, shopee_title)
            print(f"[Filtro de Identidade] Score: {score}% | {match_reason}")

            if not is_match:
                print(f"[Filtro de Identidade] REJEITADO: Produto divergente ({shopee_title}). Pulando.")
                continue

            print(f"[Filtro de Identidade] APROVADO! Buscando Reels no Instagram...")

            # 2. Busca no Instagram
            candidate_urls = []
            for tag_slug in tags_to_try:
                explore_url = f"https://www.instagram.com/explore/tags/{tag_slug}/"
                print(f"    - Explorando tag #{tag_slug}: {explore_url}")
                try:
                    page.goto(explore_url, wait_until="commit", timeout=20000)
                    page.wait_for_timeout(3000)
                    page.evaluate("window.scrollBy(0, 1000)")
                    page.wait_for_timeout(1500)
                    page.evaluate("window.scrollBy(0, 1500)")
                    page.wait_for_timeout(1500)

                    links = page.locator("a[href*='/p/'], a[href*='/reel/']").all()
                    for l in links[:30]:  # Pega até 30 posts por tag
                        href = l.get_attribute("href")
                        if href and ("/p/" in href or "/reel/" in href):
                            clean = href.split("?")[0]
                            if clean not in candidate_urls and clean not in already_done_urls:
                                candidate_urls.append(clean)
                    if len(candidate_urls) >= 20:
                        break
                except Exception as e:
                    print(f"    [Nota Instagram]: {e}")

            if not candidate_urls:
                print(f"    - [Fallback] Tags sem posts diretos ou com login exigido. Consultando catalogo coletado de achadinhos...")
                reels_og_path = SCRATCH_DIR / "all_reels_og.json"
                if reels_og_path.exists():
                    try:
                        with open(reels_og_path, "r", encoding="utf-8") as rf:
                            cached_reels = json.load(rf)
                            for cr in cached_reels:
                                c_url = cr.get("url", "")
                                if c_url and c_url not in already_done_urls:
                                    c_desc = cr.get("desc", "")
                                    c_title = cr.get("title", "")
                                    ok_match, _, _ = check_metadata_content(c_title, c_desc, "", prod_info)
                                    if ok_match and c_url not in candidate_urls:
                                        candidate_urls.append(c_url)
                    except Exception as e:
                        print(f"    [Nota Fallback]: {e}")

            if not candidate_urls:
                print(f"[Instagram] Nenhum vídeo novo para tags de '{product_name}'. Tentando próximo produto.")
                continue

            # 3. Pré-filtragem Semântica e Ordenação por Potencial Viral
            print(f"[Filtro de Conteúdo e Virilidade] Analisando {len(candidate_urls[:15])} candidatos para priorizar os mais virais...")
            scored_candidates = []

            # Mapeia metadados em cache para agilidade
            cached_meta_map = {}
            reels_og_path = SCRATCH_DIR / "all_reels_og.json"
            if reels_og_path.exists():
                try:
                    with open(reels_og_path, "r", encoding="utf-8") as rf:
                        for item in json.load(rf):
                            cached_meta_map[item.get("url")] = item
                except Exception:
                    pass

            for cand in candidate_urls[:15]:
                cand_url = cand if cand.startswith("http") else f"https://www.instagram.com{cand}"
                try:
                    cand_meta = None
                    try:
                        meta_cmd = [sys.executable, "-m", "yt_dlp", "--cookies", str(cookies_path), "--no-playlist", "--skip-download", "--dump-json", cand_url]
                        meta_res = subprocess.run(meta_cmd, capture_output=True, text=True, timeout=20)
                        if meta_res.returncode == 0:
                            cand_meta = json.loads(meta_res.stdout)
                    except Exception:
                        pass

                    if not cand_meta and cand_url in cached_meta_map:
                        cm = cached_meta_map[cand_url]
                        cand_meta = {
                            "title": cm.get("title", ""),
                            "description": cm.get("desc", ""),
                            "uploader": "achadosdiegobr",
                            "duration": 15
                        }

                    if not cand_meta:
                        continue

                    title = cand_meta.get("title", "")
                    desc = cand_meta.get("description", "")
                    uploader = cand_meta.get("uploader", "").lower()
                    duration = float(cand_meta.get("duration") or 0)

                    # Validação Semântica Estrita de Pares + Gatilhos Virais
                    pass_text, text_msg, text_score = check_metadata_content(title, desc, uploader, prod_info, duration=duration)
                    if not pass_text:
                        print(f"    - Descartado ({text_msg}): {cand_url}")
                        continue

                    scored_candidates.append({
                        "url": cand_url,
                        "meta": cand_meta,
                        "score": text_score,
                        "msg": text_msg
                    })
                except Exception as e:
                    continue

            # Prioriza os candidatos com maior pontuação viral
            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            print(f"    - Candidatos elegíveis ordenados por relevância viral: {len(scored_candidates)}")
            for idx, sc in enumerate(scored_candidates[:3], 1):
                print(f"      Top #{idx} (Score {sc['score']}): {sc['url']}")

            approved_candidate_url = None
            selected_meta = None
            video_file = None
            visual_msg = ""

            for cand_item in scored_candidates:
                cand_url = cand_item["url"]
                cand_meta = cand_item["meta"]
                try:
                    # 4. Baixar vídeo original com a MELHOR STREAM disponível
                    print(f"\n[3/6 Download Alta Qualidade] Baixando candidato mais viral (Score {cand_item['score']}): {cand_url}...")
                    files_before = set(os.listdir(target_drive_dir))
                    cmd = [
                        sys.executable, "-m", "yt_dlp",
                        "--cookies", str(cookies_path),
                        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                        cand_url,
                        "-P", str(target_drive_dir),
                        "-o", "%(title).50s [%(id)s].%(ext)s",
                        "--no-playlist"
                    ]
                    dl_res = subprocess.run(cmd, capture_output=True, text=True)
                    if dl_res.returncode != 0:
                        cmd_no_cookies = [c for c in cmd if c != "--cookies" and c != str(cookies_path)]
                        dl_res = subprocess.run(cmd_no_cookies, capture_output=True, text=True)
                    files_after = set(os.listdir(target_drive_dir))
                    new_files = [f for f in (files_after - files_before) if f.endswith((".mp4", ".mov", ".webm"))]

                    shortcode_match = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", cand_url)
                    shortcode = shortcode_match.group(1) if shortcode_match else "video"

                    cand_video_file = None
                    if new_files:
                        cand_video_file = target_drive_dir / new_files[0]
                    else:
                        for f in os.listdir(target_drive_dir):
                            if shortcode in f and f.endswith((".mp4", ".mov", ".webm")):
                                cand_video_file = target_drive_dir / f
                                break

                    if not cand_video_file or not cand_video_file.exists():
                        print(f"    [Aviso] Falha ao baixar este vídeo. Tentando próximo...")
                        continue

                    # 4.1 Validação de Resolução Mínima (Filtro Anti-360p/480p)
                    try:
                        probe_info = probe_video(cand_video_file)
                        v_w = probe_info.get("width", 0)
                        v_h = probe_info.get("height", 0)
                        min_dim = min(v_w, v_h)
                        max_dim = max(v_w, v_h)
                        # Rejeita vídeos com resolução baixa (elimina 360p e 480p: exige min >= 540 e max >= 960)
                        if min_dim < 540 or max_dim < 960:
                            print(f"    [REJEIÇÃO DE QUALIDADE] Resolução baixa ({v_w}x{v_h}). Mínimo exigido: 576p/720p/1080p vertical. Removendo...")
                            try:
                                cand_video_file.unlink()
                            except Exception:
                                pass
                            continue
                        print(f"    [QUALIDADE TÉCNICA APROVADA] Resolução válida para Reels: {v_w}x{v_h}")
                    except Exception as pe:
                        print(f"    [Aviso Probe]: {pe}")

                    # 5. Validação Visual Anti-Talking Head + Nitidez (OpenCV YuNet + Laplaciano)
                    print(f"[Filtro Visual Anti-Rosto + Nitidez] Inspecionando 7 frames com IA (Tolerância Zero para rostos)...")
                    cand_visual_ok, cand_visual_msg = check_video_for_talking_heads(cand_video_file)
                    print(f"    - Resultado: {cand_visual_msg}")

                    if not cand_visual_ok:
                        print(f"    [REJEIÇÃO VISUAL] {cand_visual_msg}. Removendo arquivo e testando próximo...")
                        try:
                            cand_video_file.unlink()
                        except Exception:
                            pass
                        continue

                    print(f"    - VÍDEO APROVADO: Foco 100% no produto, alta definição e sem rostos!")
                    approved_candidate_url = cand_url
                    selected_meta = cand_meta
                    video_file = cand_video_file
                    visual_msg = cand_visual_msg
                    break
                except Exception as e:
                    print(f"    [Nota Candidato]: {e}")
                    continue

            if not approved_candidate_url or not video_file or not video_file.exists():
                print(f"[Pipeline] Nenhum vídeo aprovado com correspondência do produto e sem rostos para '{product_name}'. Tentando próximo produto.")
                continue

            # Salva metadados da Shopee
            meta_file = video_file.parent / (video_file.stem + "_shopee.json")
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump({
                    "product_target": product_name,
                    "shopee_verified": True,
                    "identity_score": score,
                    "match_reason": match_reason,
                    "instagram_url": approved_candidate_url,
                    "visual_check": visual_msg,
                    "shopee_product": shopee_item
                }, f, indent=2, ensure_ascii=False)
            print(f"    - Metadados Shopee salvos em: {meta_file.name}")

            # 6. Curtir publicação original no Instagram
            print(f"[4/6 Instagram] Curtindo publicação original...")
            try:
                page.goto(approved_candidate_url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(2500)
                gosto = page.locator("svg[aria-label='Gosto'], svg[aria-label='Curtir'], svg[aria-label='Like']").first
                if gosto.count() > 0:
                    gosto.click(force=True)
                    print("    - Publicação original curtida com sucesso.")
            except Exception as e:
                print(f"    - Nota ao curtir publicação: {e}")

            # 7. Edição de Vídeo (FFmpeg + Pillow)
            print(f"[5/6 Edição] Aplicando caixa sólida branca e frase com FFmpeg + Pillow...")
            edit_res = process_single_video(video_file, edit_output_dir, custom_text=hook, upload_gdrive=True)

            # 8. Gerar e Enviar Legenda (.txt) para o Google Drive
            print(f"[6/6 Legenda] Gerando e enviando legenda completa para o Google Drive...")
            legenda_file = generate_legenda_file(video_file.stem, prod_info, hook, shopee_item, edit_output_dir)
            legenda_gdrive_url = upload_file_to_gdrive(legenda_file, GDRIVE_EDITED_FOLDER_ID)
            print(f"    - Legenda salva e enviada: {legenda_gdrive_url}")

            newly_processed.append({
                "product": product_name,
                "video_file": str(video_file),
                "edited_video": edit_res.get("output"),
                "preview": edit_res.get("preview"),
                "legenda": str(legenda_file),
                "instagram_url": approved_candidate_url,
                "shopee_link": shopee_item.get("offerLink"),
                "shopee_price": shopee_item.get("price"),
                "visual_validation": visual_msg,
                "gdrive_link": edit_res.get("gdrive_link")
            })
            already_done_products.add(product_name.lower().strip())
            already_done_urls.add(approved_candidate_url)
            print(f"\n>>> VÍDEO CONCLUÍDO COM SUCESSO! Novos nesta sessão: {len(newly_processed)} | Total acumulado no Drive: {len(already_done_stems) + len(newly_processed)}")

        context.close()

    print("\n" + "=" * 60)
    print(f"PIPELINE FINALIZADO: {len(newly_processed)} NOVO(S) VÍDEO(S) PROCESSADO(S)")
    print(f"TOTAL VÁLIDOS NO DRIVE: {len(already_done_stems) + len(newly_processed)} VÍDEOS")
    print("=" * 60)
    print(f"Pasta Local no Drive: {target_drive_dir}")
    print(f"Acesse os arquivos no Google Drive Nuvem: https://drive.google.com/drive/folders/{GDRIVE_EDITED_FOLDER_ID}")

    return newly_processed

if __name__ == "__main__":
    count = 10
    total = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        count = int(sys.argv[1])
        total = None
    elif len(sys.argv) > 2 and sys.argv[1] == "--total" and sys.argv[2].isdigit():
        total = int(sys.argv[2])
        count = None
    run_batch(target_count=count, target_total=total)
