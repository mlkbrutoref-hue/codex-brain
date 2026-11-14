"""Fetch Escova Elétrica de Limpeza 12 em 1 live from Shopee API."""
import time
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.providers.shopee.live import ShopeeLiveProductProvider
from app.providers.shopee.client import ShopeeAffiliateClient

def main():
    t0 = time.time()
    client = ShopeeAffiliateClient()
    provider = ShopeeLiveProductProvider(client)

    # First try by item_id/shop_id if known
    prod = None
    item_id = "20599839417"
    shop_id = "1243683750"
    print(f"Trying to get product by ID: {item_id}, shop: {shop_id}...")
    try:
        prod = provider.get_product_by_id(item_id, shop_id)
    except Exception as e:
        print(f"Direct ID lookup failed: {e}")

    if not prod:
        print("Searching product by keyword: 'escova eletrica limpeza 12 em 1'...")
        results = provider.search_products("escova eletrica limpeza 12 em 1", limit=5)
        if results:
            prod = results[0]
            print(f"Found {len(results)} products. Selected top result: {prod.title}")
        else:
            print("Searching product by keyword: 'escova eletrica limpeza'...")
            results = provider.search_products("escova eletrica limpeza", limit=5)
            if results:
                prod = results[0]

    shopee_time = time.time() - t0

    if not prod:
        print("ERROR: Could not retrieve product from Shopee live API!")
        sys.exit(1)

    print("\n=== SHOPEE_LIVE_PRODUCT ===")
    print(f"PRODUCT_ID: {prod.product_id}")
    print(f"SHOP_ID: {prod.shop_id}")
    print(f"TITLE: {prod.title}")
    print(f"PRICE: {prod.price}")
    print(f"RATING: {prod.rating_star}")
    print(f"SALES: {prod.sales_count}")
    print(f"IMAGES: {prod.images}")
    print(f"PRODUCT_URL: {prod.product_url}")
    print(f"AFFILIATE_URL: {prod.affiliate_url}")
    print(f"SHOPEE_TIME: {shopee_time:.2f}s")

    # Save to json file for pipeline reuse
    out_data = {
        "product": prod.to_dict(),
        "shopee_time": shopee_time,
    }
    out_file = ROOT / "output" / "live_escova_product.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
    print(f"Saved product info to {out_file}")

if __name__ == "__main__":
    main()
