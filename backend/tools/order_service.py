"""Order service: database operations for orders."""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import Order, async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

logger = logging.getLogger(__name__)


async def _get_session():
    """Create an async session."""
    Session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with Session() as session:
        yield session


async def get_order_by_id(order_id: str) -> Optional[Order]:
    """Query an order by order_id."""
    Session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with Session() as session:
        result = await session.execute(
            select(Order).where(Order.order_id == order_id)
        )
        return result.scalar_one_or_none()


async def get_order_status(order_id: str) -> str:
    """Get order status as a human-readable string."""
    order = await get_order_by_id(order_id)
    if not order:
        return f"未找到订单 {order_id}，请确认订单号是否正确。"

    STATUS_LABELS = {
        "pending": "待付款",
        "paid": "已付款",
        "shipped": "已发货",
        "delivered": "已签收",
        "cancelled": "已取消",
        "returning": "退货中",
        "refunded": "已退款",
    }
    label = STATUS_LABELS.get(order.status, order.status)

    lines = [f"订单 {order_id} 当前状态：{label}"]
    lines.append(f"商品：{order.product_name} × {order.quantity}")
    lines.append(f"金额：¥{order.total_amount:.2f}")
    lines.append(f"下单时间：{order.created_at.strftime('%Y-%m-%d %H:%M')}")

    if order.logistics_company and order.tracking_number:
        lines.append(f"物流：{order.logistics_company}（单号：{order.tracking_number}）")
    if order.shipping_address:
        lines.append(f"收货地址：{order.shipping_address}")

    return "\n".join(lines)


async def cancel_order(order_id: str) -> str:
    """Cancel an order (update status to cancelled)."""
    order = await get_order_by_id(order_id)
    if not order:
        return f"未找到订单 {order_id}，请确认订单号是否正确。"

    if order.status in ("cancelled", "refunded"):
        return f"订单 {order_id} 已{ '取消' if order.status == 'cancelled' else '退款' }，无法重复操作。"

    if order.status in ("shipped", "delivered"):
        return f"订单 {order_id} 已发货，无法直接取消。如需退货请使用退货功能。"

    Session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with Session() as session:
        await session.execute(
            update(Order)
            .where(Order.order_id == order_id)
            .values(status="cancelled", updated_at=datetime.now())
        )
        await session.commit()

    return f"订单 {order_id} 已成功取消。"


async def modify_order(order_id: str) -> str:
    """Modify an order - currently limited. Just returns status info."""
    order = await get_order_by_id(order_id)
    if not order:
        return f"未找到订单 {order_id}，请确认订单号是否正确。"
    if order.status != "pending":
        return f"订单 {order_id} 已付款/发货，无法修改。如需修改请联系人工客服。"
    return f"订单 {order_id} 当前为待付款状态，您可以取消后重新下单。"


async def confirm_receipt(order_id: str) -> str:
    """Confirm receipt of an order."""
    order = await get_order_by_id(order_id)
    if not order:
        return f"未找到订单 {order_id}，请确认订单号是否正确。"

    if order.status == "delivered":
        return f"订单 {order_id} 已签收，无需重复确认。"

    if order.status != "shipped":
        return f"订单 {order_id} 当前状态不支持确认收货。"

    Session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with Session() as session:
        await session.execute(
            update(Order)
            .where(Order.order_id == order_id)
            .values(status="delivered", updated_at=datetime.now())
        )
        await session.commit()

    return f"已确认订单 {order_id} 收货成功！感谢您的购买，如有售后问题随时联系我们。"


async def initiate_return(order_id: str, reason: str) -> str:
    """Initiate a return request."""
    order = await get_order_by_id(order_id)
    if not order:
        return f"未找到订单 {order_id}，请确认订单号是否正确。"

    if order.status in ("cancelled", "refunded"):
        return f"订单 {order_id} 已取消或已退款，无法发起退货。"

    if order.status == "returning":
        return f"订单 {order_id} 已在退货流程中，无需重复申请。"

    Session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with Session() as session:
        await session.execute(
            update(Order)
            .where(Order.order_id == order_id)
            .values(
                status="returning",
                return_reason=reason,
                updated_at=datetime.now(),
            )
        )
        await session.commit()

    return f"已为您提交订单 {order_id} 的退货申请（原因：{reason}）。客服将在24小时内审核，请保持手机畅通。"


async def initiate_exchange(order_id: str, reason: str) -> str:
    """Initiate an exchange request."""
    order = await get_order_by_id(order_id)
    if not order:
        return f"未找到订单 {order_id}，请确认订单号是否正确。"

    if order.status in ("cancelled", "refunded", "returning"):
        return f"订单 {order_id} 当前状态无法申请换货。"

    Session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with Session() as session:
        await session.execute(
            update(Order)
            .where(Order.order_id == order_id)
            .values(
                return_reason=reason,
                updated_at=datetime.now(),
            )
        )
        await session.commit()

    return f"已为您提交订单 {order_id} 的换货申请（原因：{reason}）。客服将在24小时内审核处理。"


async def check_refund(order_id: str) -> str:
    """Check refund status."""
    order = await get_order_by_id(order_id)
    if not order:
        return f"未找到订单 {order_id}，请确认订单号是否正确。"

    if order.status == "refunded":
        amount = order.refund_amount or order.total_amount
        return f"订单 {order_id} 已退款，金额 ¥{amount:.2f}，请查看您的支付账户。"
    elif order.status == "returning":
        return f"订单 {order_id} 正在退货流程中，退货审核通过后将安排退款。"
    else:
        return f"订单 {order_id} 当前状态为「{order.status}」，暂无退款信息。"


# ---------------------------------------------------------------------------
# CRUD operations for order import API
# ---------------------------------------------------------------------------


async def create_order(data: dict) -> Optional[Order]:
    """Create a new order."""
    async with async_sessionmaker(bind=async_engine, expire_on_commit=False)() as session:
        order = Order(**data)
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order


async def list_orders(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    source: Optional[str] = None,
    keyword: Optional[str] = None,
) -> tuple[list[Order], int]:
    """List orders with pagination and filters."""
    async with async_sessionmaker(bind=async_engine, expire_on_commit=False)() as session:
        query = select(Order)
        if status:
            query = query.where(Order.status == status)
        if source:
            query = query.where(Order.source == source)
        if keyword:
            query = query.where(
                Order.order_id.contains(keyword)
                | Order.product_name.contains(keyword)
            )
        count_q = select(func.count()).select_from(query.subquery())
        total = (await session.execute(count_q)).scalar() or 0
        query = query.order_by(Order.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await session.execute(query)
        return result.scalars().all(), total


async def update_order(order_id: str, data: dict) -> Optional[Order]:
    """Update order fields."""
    async with async_sessionmaker(bind=async_engine, expire_on_commit=False)() as session:
        data["updated_at"] = datetime.now()
        result = await session.execute(
            update(Order)
            .where(Order.order_id == order_id)
            .values(**data)
        )
        await session.commit()
        if result.rowcount == 0:
            return None
    return await get_order_by_id(order_id)
