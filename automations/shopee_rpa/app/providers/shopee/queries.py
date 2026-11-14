"""GraphQL queries and helpers matching the official Shopee Affiliate schema."""

PRODUCT_OFFERS = """query ProductOffers(
  $page: Int, $limit: Int, $keyword: String, $itemId: Int64, $shopId: Int64,
  $productCatId: Int, $sortType: Int
) {
  productOfferV2(page: $page, limit: $limit, keyword: $keyword, itemId: $itemId,
                 shopId: $shopId, productCatId: $productCatId, sortType: $sortType) {
    nodes {
      itemId shopId productName shopName price priceMin priceMax priceDiscountRate
      sales ratingStar commissionRate commission productLink offerLink imageUrl productCatIds
    }
    pageInfo { page limit hasNextPage }
  }
}"""

SHORT_LINK = """mutation AffiliateShortLink($input: ShortLinkInput!) {
  generateShortLink(input: $input) { shortLink }
}"""


def product_details_query(item_id: int, shop_id: int) -> str:
    """Builds a query for a specific product using numeric literals for Int64.
    
    The Brazilian live API rejects JSON numeric variables for Int64 with 10010 'wrong type'.
    The official Shopee Explorer emits numeric GraphQL literals.
    """
    for value in (item_id, shop_id):
        if not isinstance(value, int) or not (0 < value < 2**63):
            raise ValueError(f"IDs must be positive Int64 integers, got: {value}")

    selection = (
        "itemId shopId productName shopName price priceMin priceMax priceDiscountRate "
        "sales ratingStar commissionRate commission productLink offerLink imageUrl productCatIds"
    )

    return (
        f"query ProductDetails {{ "
        f"productOfferV2(itemId: {item_id}, shopId: {shop_id}, page: 1, limit: 1) {{ "
        f"nodes {{ {selection} }} "
        f"pageInfo {{ page limit hasNextPage }} "
        f"}} }}"
    )