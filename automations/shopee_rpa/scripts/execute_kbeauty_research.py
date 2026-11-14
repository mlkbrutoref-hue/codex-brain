"""Script para executar pesquisa completa de K-Beauty / maquiagem asiática na Shopee Affiliate API.
Salva candidatos, executa ranking e gera saídas estruturadas.
"""
import sys
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Reconfigure stdout for utf-8
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from app.providers.shopee.client import ShopeeAffiliateClient
from app.providers.shopee.queries import PRODUCT_OFFERS

# Lista de termos de busca obrigatórios e estratégicos
SEARCH_QUERIES = [
    "maquiagem coreana",
    "k beauty maquiagem",
    "kbeauty",
    "maquiagem asiática",
    "BB cream coreano",
    "CC cream coreano",
    "cushion coreana",
    "cushion foundation",
    "base coreana",
    "maquiagem coreana viral",
    "lip tint coreano",
    "gloss tint coreano",
    "máscara cílios coreana",
    "delineador coreano",
    "delineador carimbo",
    "delineador 2 em 1",
    "corretivo coreano",
    "paleta corretivo coreano",
    "pó coreano",
    "pó facial coreano",
    "sobrancelha coreana",
    "eyebrow gel korean",
    "Korean makeup",
    "Korean cushion",
    "Korean lip tint",
    "Korean eyeliner",
    "Asian beauty makeup",
    "cushion cogumelo",
    "batom magico ph",
    "blush que muda de cor",
    "rimel 2 em 1 fibra 4d",
    "po translucido coreano",
    "caneta sobrancelha 4 pontas"
]

NEGATIVE_TERMS = [
    "capa", "case", "fone", "celular", "brinquedo", "vestido", "blusa", "sapato",
    "calça", "short", "relogio", "colar", "brinco", "anel", "adesivo de unha",
    "unha postiça", "peruca", "cilios posticos fita", "esponja sem base",
    "organizador", "pincel isolado", "pente", "necessaire vazia", "garrafa", "copo"
]

def clean_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

def search_all_products(client: ShopeeAffiliateClient) -> Dict[str, Dict[str, Any]]:
    all_products: Dict[str, Dict[str, Any]] = {}
    total_calls = 0

    print(f"Iniciando busca com {len(SEARCH_QUERIES)} termos...")
    for idx, query in enumerate(SEARCH_QUERIES, 1):
        try:
            print(f"[{idx}/{len(SEARCH_QUERIES)}] Buscando '{query}'...")
            res = client.execute(PRODUCT_OFFERS, {"page": 1, "limit": 15, "keyword": query})
            total_calls += 1
            nodes = res.get("productOfferV2", {}).get("nodes", [])
            print(f"  -> Retornou {len(nodes)} produtos.")

            for node in nodes:
                item_id = str(node.get("itemId", ""))
                shop_id = str(node.get("shopId", ""))
                if not item_id or not shop_id:
                    continue

                title = clean_text(node.get("productName", ""))
                title_lower = title.lower()

                # Filtro de termos negativos
                if any(neg in title_lower for neg in NEGATIVE_TERMS):
                    continue

                # Preço
                try:
                    price = float(node.get("price")) if node.get("price") is not None else None
                except (ValueError, TypeError):
                    price = None

                if price is None or price <= 0:
                    continue

                if item_id not in all_products:
                    # Desconto
                    try:
                        discount = float(node.get("priceDiscountRate")) if node.get("priceDiscountRate") is not None else None
                    except (ValueError, TypeError):
                        discount = None

                    # Rating
                    try:
                        rating = float(node.get("ratingStar")) if node.get("ratingStar") is not None else None
                    except (ValueError, TypeError):
                        rating = None

                    # Sales
                    try:
                        sales = int(node.get("sales")) if node.get("sales") is not None else 0
                    except (ValueError, TypeError):
                        sales = 0

                    # Commission
                    try:
                        comm = float(node.get("commission")) if node.get("commission") is not None else None
                    except (ValueError, TypeError):
                        comm = None

                    all_products[item_id] = {
                        "item_id": item_id,
                        "shop_id": shop_id,
                        "product_name": title,
                        "shop_name": node.get("shopName") or "",
                        "price": price,
                        "original_price": None,
                        "discount_percentage": discount,
                        "rating": rating,
                        "sales": sales,
                        "commission": comm,
                        "commission_rate": float(node.get("commissionRate", 0) or 0),
                        "product_url": node.get("productLink", ""),
                        "affiliate_url": node.get("offerLink", ""),
                        "image_url": node.get("imageUrl", ""),
                        "categories": node.get("productCatIds", []),
                        "matched_queries": [query]
                    }
                else:
                    if query not in all_products[item_id]["matched_queries"]:
                        all_products[item_id]["matched_queries"].append(query)

            # Delay respeitoso
            time.sleep(0.4)
        except Exception as e:
            print(f"  Erro ao buscar '{query}': {e}")
            raise RuntimeError("AFFILIATE_BATCH_STOPPED_NO_AUTOMATIC_CONTINUATION") from None

    print(f"\nTotal de produtos brutos únicos encontrados: {len(all_products)}")
    return all_products

if __name__ == "__main__":
    client = ShopeeAffiliateClient()
    products = search_all_products(client)
    output_dir = project_root / "output" / "research" / "kbeauty_carousel"
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "raw_search_dump.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"Salvo dump bruto em {output_dir / 'raw_search_dump.json'}")
