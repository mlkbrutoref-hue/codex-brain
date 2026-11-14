"""Abstract base class for Shopee product providers."""
from abc import ABC, abstractmethod
from typing import Optional
from app.models.product import Product


class ShopeeProductProvider(ABC):
    """Abstract interface for fetching product data from Shopee."""

    @abstractmethod
    def get_product(self, product_id: str) -> Product:
        """Fetches product by ID or raises ValueError/RuntimeError if not found."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is currently available and configured."""
        pass