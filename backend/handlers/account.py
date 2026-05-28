import logging

from models.schemas import HandlerResult, IntentResult

logger = logging.getLogger(__name__)


async def handle_account_issue(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="正在查询您的账号信息，请稍候...")


async def handle_payment_issue(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="正在查询支付问题...")


async def handle_invoice_request(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="正在为您处理发票申请...")


async def handle_point_inquiry(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="正在查询您的积分和会员等级...")
