"""Order import adapters for different platforms."""
from abc import ABC, abstractmethod
from typing import Optional


class OrderImporter(ABC):
    """Abstract base for platform-specific order importers."""

    @abstractmethod
    async def import_order(self, external_id: str) -> dict:
        """Fetch order from external platform, return dict matching OrderCreate schema."""
        ...

    @abstractmethod
    async def sync_orders(self, start_time: Optional[str] = None) -> list[dict]:
        """Batch sync orders from external platform."""
        ...
