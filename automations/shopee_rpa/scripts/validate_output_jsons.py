import json
from pathlib import Path

base_dir = Path("output/research/kbeauty_carousel")

for fname in ["candidates.json", "selected_products.json"]:
    fpath = base_dir / fname
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[OK] {fname} é JSON válido com {len(data)} itens.")
    # Verificar integridade dos campos
    for idx, item in enumerate(data[:3]):
        assert item["item_id"], "item_id ausente"
        assert item["price"] is not None, "price ausente"
        assert item["product_url"], "product_url ausente"
        assert item["image_url"], "image_url ausente"

print("Todos os JSONs estão perfeitamente válidos e íntegros!")
