import logging
from typing import Any, Dict, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


async def query_order(order_id: str) -> Dict[str, Any]:
    if not settings.order_api_base:
        return {"order_id": order_id, "status": "模拟数据-已发货", "note": "第三方API未配置，返回模拟数据"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{settings.order_api_base}/orders/{order_id}")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Order API failed: {e}")
        return {"order_id": order_id, "error": str(e)}


async def query_logistics(order_id: str) -> Dict[str, Any]:
    if not settings.logistics_api_base:
        return {"order_id": order_id, "status": "模拟数据-运输中", "note": "第三方API未配置，返回模拟数据"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{settings.logistics_api_base}/logistics/{order_id}")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Logistics API failed: {e}")
        return {"order_id": order_id, "error": str(e)}


async def process_refund(order_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
    if not settings.payment_api_base:
        return {"order_id": order_id, "status": "模拟数据-退款处理中", "note": "第三方API未配置，返回模拟数据"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{settings.payment_api_base}/refund",
                json={"order_id": order_id, "amount": amount},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"Refund API failed: {e}")
        return {"order_id": order_id, "error": str(e)}
