import logging

from models.schemas import HandlerResult, IntentResult

logger = logging.getLogger(__name__)


async def handle_return_request(intent: IntentResult, context: dict) -> HandlerResult:
    order_id = intent.params.get("order_id", "")
    return HandlerResult(response=f"正在为您处理订单 {order_id} 的退货申请...")


async def handle_exchange_request(intent: IntentResult, context: dict) -> HandlerResult:
    order_id = intent.params.get("order_id", "")
    return HandlerResult(response=f"正在为您处理订单 {order_id} 的换货申请...")


async def handle_refund_inquiry(intent: IntentResult, context: dict) -> HandlerResult:
    order_id = intent.params.get("order_id", "")
    return HandlerResult(response=f"正在查询订单 {order_id} 的退款进度...")


async def handle_after_sale_policy(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="正在查询售后政策...")


async def handle_complaint(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="非常抱歉给您带来了不好的体验，请详细描述您遇到的问题，我会为您记录并反馈。")


async def handle_warranty_inquiry(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="正在查询保修信息...")
