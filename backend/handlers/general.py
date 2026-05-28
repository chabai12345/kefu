import logging

from models.schemas import HandlerResult, IntentResult

logger = logging.getLogger(__name__)


async def handle_faq(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="正在查询常见问题...")


async def handle_chat(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="")


async def handle_greeting(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="您好！欢迎来到我们的电商平台。请问有什么可以帮您的吗？您可以咨询商品信息、查询订单状态，或者了解售后政策。")


async def handle_farewell(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="感谢您的咨询，祝您生活愉快！如果还有其他问题，随时可以找我。")


async def handle_feedback(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="感谢您的反馈，我们会不断改进！")
