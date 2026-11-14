"""Shopee providers package."""
from app.providers.shopee.base import ShopeeProductProvider
from app.providers.shopee.fixture import LocalFixtureShopeeProvider
from app.providers.shopee.live import ShopeeLiveProductProvider
from app.providers.shopee.client import ShopeeAffiliateClient, AffiliateAPIError
from app.providers.shopee.credentials import AffiliateCredentials
from app.providers.shopee.factory import get_shopee_provider

__all__ = [
    "ShopeeProductProvider",
    "LocalFixtureShopeeProvider",
    "ShopeeLiveProductProvider",
    "ShopeeAffiliateClient",
    "AffiliateAPIError",
    "AffiliateCredentials",
    "get_shopee_provider",
]