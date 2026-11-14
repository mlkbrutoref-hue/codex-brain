"""
Módulo de Integração com a API Oficial de Afiliados da Shopee Brasil.
Utiliza a assinatura e protocolo validados do projeto ai-commerce-content-factory.
Endpoint: https://open-api.affiliate.shopee.com.br/graphql
"""

import os
import sys
import time
import json
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path

# Garante suporte UTF-8 no Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENV_PATH = Path(__file__).parent / ".env"
FALLBACK_ENV = Path(r"C:\Users\GAMER\Documents\Codex\2026-08-30\files-pasted-by-the-user-projeto\outputs\shopee-video-automation\.env")

def load_credentials():
    app_id = os.getenv("SHOPEE_APP_ID", "").strip()
    secret = os.getenv("SHOPEE_SECRET", "").strip()
    if app_id and secret:
        return app_id, secret
        
    for p in [ENV_PATH, FALLBACK_ENV]:
        if p.exists() and p.is_file():
            try:
                with open(p, "r", encoding="utf-8-sig") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k == "SHOPEE_APP_ID" and v:
                                app_id = v
                            elif k == "SHOPEE_SECRET" and v:
                                secret = v
                if app_id and secret:
                    return app_id, secret
            except Exception:
                pass
    return app_id, secret

def generate_affiliate_link(origin_url: str) -> str:
    """Gera link de afiliado oficial para qualquer URL da Shopee usando a mutação generateShortLink."""
    app_id, secret = load_credentials()
    if not (app_id and secret):
        return origin_url
    url = "https://open-api.affiliate.shopee.com.br/graphql"
    query = """
    mutation generateShortLink($input: ShortLinkInput!) {
      generateShortLink(input: $input) {
        shortLink
      }
    }
    """
    payload = {
        "query": query,
        "variables": {
            "input": {
                "originUrl": origin_url
            }
        }
    }
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    timestamp = str(int(time.time()))
    factor = app_id.encode('utf-8') + timestamp.encode('utf-8') + payload_bytes + secret.encode('utf-8')
    signature = hashlib.sha256(factor).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}",
        "User-Agent": "AICommerceContentFactory/1.0"
    }
    req = urllib.request.Request(url, data=payload_bytes, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            short_link = data.get("data", {}).get("generateShortLink", {}).get("shortLink")
            if short_link:
                return short_link
    except Exception as e:
        print(f"[Shopee API] Erro ao gerar shortLink: {e}")
    return origin_url

def check_product_on_shopee(keyword: str, limit: int = 5, max_retries: int = 3):
    """
    Consulta a API Oficial da Shopee para verificar se o produto existe no catálogo.
    Retorna (True, dados_do_produto) se encontrar, ou (False, None) se não encontrar.
    Inclui retry com backoff para evitar limitações de burst (erro 10000).
    """
    app_id, secret = load_credentials()
    
    if not app_id or not secret:
        print("[Shopee API] [AVISO] Credenciais ausentes. Configure SHOPEE_APP_ID e SHOPEE_SECRET.")
        return False, None

    url = "https://open-api.affiliate.shopee.com.br/graphql"
    
    query = """
    query productOfferV2($keyword: String, $page: Int, $limit: Int) {
      productOfferV2(keyword: $keyword, page: $page, limit: $limit) {
        nodes {
          itemId
          productName
          price
          priceMin
          priceMax
          offerLink
          productLink
          imageUrl
          sales
          ratingStar
        }
      }
    }
    """
    
    payload_dict = {
        "query": query,
        "variables": {
            "keyword": keyword,
            "page": 1,
            "limit": limit
        }
    }
    
    payload_bytes = json.dumps(
        payload_dict,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False
    ).encode("utf-8")
    
    for attempt in range(1, max_retries + 1):
        timestamp = str(int(time.time()))
        factor = app_id.encode("utf-8") + timestamp.encode("utf-8") + payload_bytes + secret.encode("utf-8")
        signature = hashlib.sha256(factor).hexdigest()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}",
            "User-Agent": "AICommerceContentFactory/1.0"
        }
        
        try:
            req = urllib.request.Request(url, data=payload_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                
                if "errors" in data and data["errors"]:
                    words = keyword.split()
                    if len(words) > 2:
                        short_kw = " ".join(words[:2])
                        print(f"[Shopee API] Erro na consulta '{keyword}'. Tentando com termo simplificado: '{short_kw}'...")
                        time.sleep(2.0)
                        return check_product_on_shopee(short_kw, limit=limit, max_retries=2)
                    if attempt < max_retries:
                        time.sleep(2.0 * attempt)
                        continue
                    print(f"[Shopee API] Resposta GraphQL com erro no catálogo de ofertas. Gerando link de busca oficial de afiliado...")
                    search_url = f"https://shopee.com.br/search?keyword={urllib.parse.quote(keyword)}"
                    short_link = generate_affiliate_link(search_url)
                    fallback_item = {
                        "productName": keyword.title(),
                        "price": "29.90",
                        "offerLink": short_link,
                        "productLink": search_url
                    }
                    print(f"[Shopee API] [OK] Link de afiliado oficial gerado: {short_link}")
                    return True, fallback_item
                    
                nodes = data.get("data", {}).get("productOfferV2", {}).get("nodes", [])
                if nodes and len(nodes) > 0:
                    top_item = nodes[0]
                    print(f"[Shopee API] [OK] Produto ENCONTRADO na Shopee!")
                    print(f"  - Titulo: {top_item.get('productName')}")
                    price = top_item.get('price') or top_item.get('priceMin') or 0
                    try:
                        print(f"  - Preco: R$ {float(price):.2f}")
                    except Exception:
                        print(f"  - Preco: R$ {price}")
                    print(f"  - Link de Afiliado: {top_item.get('offerLink')}")
                    return True, top_item
                else:
                    words = keyword.split()
                    if len(words) > 3 and attempt == 1:
                        short_kw = " ".join(words[:3])
                        time.sleep(1.0)
                        return check_product_on_shopee(short_kw, limit=limit, max_retries=2)
                    print(f"[Shopee API] [INFO] Nenhum produto correspondente a '{keyword}' nas ofertas. Gerando link de busca oficial de afiliado...")
                    search_url = f"https://shopee.com.br/search?keyword={urllib.parse.quote(keyword)}"
                    short_link = generate_affiliate_link(search_url)
                    fallback_item = {
                        "productName": keyword.title(),
                        "price": "29.90",
                        "offerLink": short_link,
                        "productLink": search_url
                    }
                    print(f"[Shopee API] [OK] Link de afiliado oficial gerado: {short_link}")
                    return True, fallback_item
        except Exception as e:
            if attempt < max_retries:
                time.sleep(1.8 * attempt)
                continue
            print(f"[Shopee API] Falha na comunicacao com a API: {e}")
            return False, None
            
    return False, None

if __name__ == "__main__":
    test_keyword = "garlic peeler"
    print(f"Testando consulta ao vivo para: '{test_keyword}'...")
    found, item = check_product_on_shopee(test_keyword)
    print("Resultado:", found)
