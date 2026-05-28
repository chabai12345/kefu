import logging

from models.schemas import HandlerResult, IntentResult

logger = logging.getLogger(__name__)


async def handle_product_inquiry(intent: IntentResult, context: dict) -> HandlerResult:
    product = intent.params.get("product", "")
    # TODO: call RAG MCP Server for product info
    return HandlerResult(
        response=f"您想了解 {product} 的详细信息，正在为您查询...",
        tool_calls=[],
    )


async def handle_price_inquiry(intent: IntentResult, context: dict) -> HandlerResult:
    product = intent.params.get("product", "")
    return HandlerResult(response=f"正在查询 {product} 的价格信息...")


async def handle_stock_inquiry(intent: IntentResult, context: dict) -> HandlerResult:
    product = intent.params.get("product", "")
    return HandlerResult(response=f"正在查询 {product} 的库存情况...")


async def handle_recommendation(intent: IntentResult, context: dict) -> HandlerResult:
    需求 = intent.params.get("需求", "")
    return HandlerResult(response=f"根据您的需求「{需求}」，正在为您推荐合适的商品...")


async def handle_comparison(intent: IntentResult, context: dict) -> HandlerResult:
    products = intent.params.get("products", [])
    return HandlerResult(response=f"正在为您对比 {' vs '.join(products)}...")


async def handle_promotion_inquiry(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="正在查询当前促销活动和优惠信息...")


async def handle_shipping_inquiry(intent: IntentResult, context: dict) -> HandlerResult:
    return HandlerResult(response="正在查询配送信息...")
