import logging

from models.schemas import HandlerResult, IntentResult

logger = logging.getLogger(__name__)


async def handle_order_status(intent: IntentResult, context: dict) -> HandlerResult:
    order_id = intent.params.get("order_id", "")
    return HandlerResult(response=f"正在查询订单 {order_id} 的状态...")


async def handle_order_cancel(intent: IntentResult, context: dict) -> HandlerResult:
    order_id = intent.params.get("order_id", "")
    return HandlerResult(response=f"正在为您处理订单 {order_id} 的取消请求...")


async def handle_order_modify(intent: IntentResult, context: dict) -> HandlerResult:
    order_id = intent.params.get("order_id", "")
    return HandlerResult(response=f"正在为您修改订单 {order_id} 的信息...")


async def handle_order_confirm(intent: IntentResult, context: dict) -> HandlerResult:
    order_id = intent.params.get("order_id", "")
    return HandlerResult(response=f"正在确认订单 {order_id} 的收货...")


async def handle_delivery_inquiry(intent: IntentResult, context: dict) -> HandlerResult:
    order_id = intent.params.get("order_id", "")
    return HandlerResult(response=f"正在查询订单 {order_id} 的物流信息...")
