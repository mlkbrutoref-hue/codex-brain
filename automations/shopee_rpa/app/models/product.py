"""Product data model representing Shopee affiliate product information."""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional


@dataclass
class Product:
    """Official product entity provided by Shopee Affiliate API."""
    product_id: str
    shop_id: str
    title: str
    description: Optional[str]
    price: Optional[float]
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    images: List[str] = field(default_factory=list)
    category: Optional[str] = None
    category_ids: List[int] = field(default_factory=list)
    seller_name: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None
    commission_rate: Optional[float] = None
    product_url: str = ""
    affiliate_url: str = ""
    rating_star: Optional[float] = None
    sales_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        orig_price = data.get("original_price")
        discount = data.get("discount_percentage")
        comm_rate = data.get("commission_rate")
        rating = data.get("rating_star")
        sales = data.get("sales_count")

        return cls(
            product_id=str(data.get("product_id", "")),
            shop_id=str(data.get("shop_id", "")),
            title=str(data.get("title", "")),
            description=(str(data["description"]) if data.get("description") is not None else None),
            price=float(data["price"]) if data.get("price") is not None else None,
            original_price=float(orig_price) if orig_price is not None else None,
            discount_percentage=float(discount) if discount is not None else None,
            images=list(data.get("images", [])),
            category=(str(data["category"]) if data.get("category") is not None else None),
            category_ids=[int(value) for value in (data.get("category_ids") or [])],
            seller_name=(str(data["seller_name"]) if data.get("seller_name") is not None else None),
            attributes=(dict(data["attributes"]) if data.get("attributes") is not None else None),
            commission_rate=float(comm_rate) if comm_rate is not None else None,
            product_url=str(data.get("product_url", "")),
            affiliate_url=str(data.get("affiliate_url", "")),
            rating_star=float(rating) if rating is not None else None,
            sales_count=int(sales) if sales is not None else None,
        )
