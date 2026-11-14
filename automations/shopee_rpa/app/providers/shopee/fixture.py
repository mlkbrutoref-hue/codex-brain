"""Local fixture provider for Shopee products (offline testing and fallback)."""
import json
from pathlib import Path
from typing import Optional, Union
from app.models.product import Product
from app.providers.shopee.base import ShopeeProductProvider


class LocalFixtureShopeeProvider(ShopeeProductProvider):
    """Loads product data from local JSON fixtures."""

    def __init__(self, fixtures_dir: Optional[Union[str, Path]] = None):
        if fixtures_dir is None:
            self.fixtures_dir = Path(__file__).resolve().parents[3] / "data" / "products"
        else:
            self.fixtures_dir = Path(fixtures_dir)

    def is_available(self) -> bool:
        return self.fixtures_dir.exists()

    def get_product(self, product_id: str) -> Product:
        """Looks for <product_id>.json, or sample_product.json, or raises FileNotFoundError."""
        target_file = self.fixtures_dir / f"{product_id}.json"
        if not target_file.exists():
            sample_file = self.fixtures_dir / "sample_product.json"
            if sample_file.exists():
                target_file = sample_file
            else:
                raise FileNotFoundError(
                    f"Product fixture '{product_id}' not found in {self.fixtures_dir}"
                )

        with open(target_file, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        return Product.from_dict(data)