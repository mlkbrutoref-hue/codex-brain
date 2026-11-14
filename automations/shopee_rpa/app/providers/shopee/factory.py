"""Factory for resolving Shopee product providers with strict mode boundaries."""
import os
from typing import Optional
from app.providers.shopee.base import ShopeeProductProvider
from app.providers.shopee.live import ShopeeLiveProductProvider
from app.providers.shopee.fixture import LocalFixtureShopeeProvider


def get_shopee_provider(provider_type: Optional[str] = None) -> ShopeeProductProvider:
    """Returns the requested Shopee provider based on argument or SHOPEE_PROVIDER env var.
    
    Modes:
    - 'live': Connects strictly to live Shopee Affiliate API. No fallback to fixtures.
    - 'fixture': Reads strictly from local fixtures. Never claims to be live.
    """
    mode = (provider_type or os.getenv("SHOPEE_PROVIDER", "fixture")).strip().lower()

    if mode == "live":
        return ShopeeLiveProductProvider()
    elif mode == "fixture":
        return LocalFixtureShopeeProvider()
    else:
        raise ValueError(
            f"Modo de SHOPEE_PROVIDER inválido: '{mode}'. Opções permitidas: 'live' ou 'fixture'."
        )