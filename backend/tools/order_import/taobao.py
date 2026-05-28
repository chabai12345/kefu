"""Taobao order importer (stub for future integration)."""

import logging
from typing import Optional

from tools.order_import import OrderImporter

logger = logging.getLogger(__name__)


class TaobaoImporter(OrderImporter):
    """Taobao Open API order importer.

    TODO: Implement Taobao Open Platform integration:
    - OAuth 2.0 authentication
    - taobao.trade.fullinfo.get API call
    - Field mapping from Taobao order model → internal Order model
    - Batched sync via taobao.trades.sold.get
    """

    async def import_order(self, trade_id: str) -> dict:
        raise NotImplementedError("Taobao integration pending")

    async def sync_orders(self, start_time: Optional[str] = None) -> list[dict]:
        raise NotImplementedError("Taobao integration pending")
