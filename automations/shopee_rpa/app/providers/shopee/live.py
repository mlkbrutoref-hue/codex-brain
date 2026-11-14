"""Live Shopee Product Provider connecting directly to the Affiliate Open API."""
from typing import Optional, List
from app.models.product import Product
from app.providers.shopee.base import ShopeeProductProvider
from app.providers.shopee.client import ShopeeAffiliateClient, AffiliateAPIError
from app.providers.shopee.queries import PRODUCT_OFFERS, product_details_query


class ShopeeLiveProductProvider(ShopeeProductProvider):
    """LIVE Shopee provider. Strictly calls the real API with NO silent fallback."""

    def __init__(self, client: Optional[ShopeeAffiliateClient] = None):
        self.client = client or ShopeeAffiliateClient()

    def is_available(self) -> bool:
        try:
            return self.client.check_connection()
        except Exception:
            return False

    def _map_node_to_product(self, node: dict) -> Product:
        item_id = str(node.get("itemId", ""))
        shop_id = str(node.get("shopId", ""))
        title = str(node.get("productName") or "")
        if not item_id or not shop_id or not title:
            raise AffiliateAPIError("Shopee response is missing required product identity fields.")
        def optional_float(name):
            value = node.get(name)
            return None if value in (None, "") else float(value)

        price = optional_float("price")
        discount = optional_float("priceDiscountRate")
        rating = optional_float("ratingStar")
        sales_raw = node.get("sales")
        sales = None if sales_raw in (None, "") else int(sales_raw)
        commission_rate = optional_float("commissionRate")
        img_url = node.get("imageUrl", "")
        prod_link = node.get("productLink", "")
        offer_link = node.get("offerLink", "")

        return Product(
            product_id=item_id,
            shop_id=shop_id,
            title=title,
            description=None,
            price=price,
            # priceMax is the highest current variant price, not proof of an original price.
            original_price=None,
            discount_percentage=discount,
            images=[img_url] if img_url else [],
            category=None,
            category_ids=[int(value) for value in (node.get("productCatIds") or [])],
            seller_name=(str(node["shopName"]) if node.get("shopName") else None),
            attributes=None,
            commission_rate=commission_rate,
            product_url=prod_link,
            affiliate_url=offer_link,
            rating_star=rating,
            sales_count=sales,
        )

    def get_product(self, product_id: str) -> Product:
        """Fetches product details from live Shopee Affiliate API.
        
        Accepts:
        - "item_id:shop_id" or "item_id_shop_id"
        - "item_id" (searches via productOfferV2 by itemId)
        """
        import re
        if not re.fullmatch(r'[1-9]\d*(?:[:_][1-9]\d*)?', product_id):
            raise AffiliateAPIError('EXACT_PRODUCT_ID_REQUIRED_USE_SEARCH_PRODUCTS_FOR_DISCOVERY')
        parts = re.split(r'[:_]', product_id)
        item_id = int(parts[0])
        shop_id = int(parts[1]) if len(parts)==2 else None
        if shop_id is not None:
            data = self.client.execute(product_details_query(item_id,shop_id))
        else:
            data = self.client.execute(PRODUCT_OFFERS,{'page':1,'limit':5,'itemId':item_id})
        nodes=data.get('productOfferV2',{}).get('nodes',[])
        exact=[node for node in nodes if str(node.get('itemId'))==str(item_id) and
               (shop_id is None or str(node.get('shopId'))==str(shop_id))]
        if len(exact)!=1:
            raise AffiliateAPIError('PRODUCT_IDENTITY_MISSING_OR_AMBIGUOUS')
        return self._map_node_to_product(exact[0])

    def search_products(self, keyword: str, limit: int = 5) -> List[Product]:
        """Searches live products by keyword."""
        variables = {"page": 1, "limit": limit, "keyword": keyword}
        data = self.client.execute(PRODUCT_OFFERS, variables)
        nodes = data.get("productOfferV2", {}).get("nodes", [])
        return [self._map_node_to_product(n) for n in nodes]
