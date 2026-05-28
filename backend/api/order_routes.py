"""Order CRUD REST API routes."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from models.schemas_order import (
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderUpdate,
)
from tools import order_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(data: OrderCreate):
    """Import a new order."""
    existing = await order_service.get_order_by_id(data.order_id)
    if existing:
        raise HTTPException(409, f"订单 {data.order_id} 已存在")
    order = await order_service.create_order(data.model_dump())
    if not order:
        raise HTTPException(500, "创建订单失败")
    return OrderResponse.model_validate(order)


@router.get("", response_model=OrderListResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    source: Optional[str] = None,
    keyword: Optional[str] = None,
):
    """List orders with optional filters."""
    orders, total = await order_service.list_orders(
        page=page, page_size=page_size,
        status=status, source=source, keyword=keyword,
    )
    return OrderListResponse(
        total=total, page=page, page_size=page_size,
        orders=[OrderResponse.model_validate(o) for o in orders],
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """Get order detail by order_id."""
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(404, f"订单 {order_id} 不存在")
    return OrderResponse.model_validate(order)


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: str, data: OrderUpdate):
    """Update order fields."""
    filtered = data.model_dump(exclude_none=True)
    if not filtered:
        raise HTTPException(400, "没有要更新的字段")
    order = await order_service.update_order(order_id, filtered)
    if not order:
        raise HTTPException(404, f"订单 {order_id} 不存在")
    return OrderResponse.model_validate(order)


@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: str):
    """Cancel an order."""
    order = await order_service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(404, f"订单 {order_id} 不存在")
    await order_service.update_order(order_id, {"status": "cancelled"})
