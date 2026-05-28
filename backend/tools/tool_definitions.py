"""Tool definitions and execution functions for LLM dynamic tool calling.

Each tool has:
- OpenAI-compatible JSON schema for function calling
- Async execution function that returns a string result
"""

import json
import logging
from typing import Any, Dict, List

from tools.rag_client import rag_client
from tools.rag_generator import rag_generator
from tools import order_service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool Schemas (OpenAI Function Calling format)
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "query_knowledge_base",
            "description": "搜索知识库获取售后政策、退换货规则、商品信息、常见问题、配送政策等",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，如'退货流程'、'保修政策'、'商品信息'",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "查询订单状态，需要用户提供订单号",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "用户的订单号",
                    }
                },
                "required": ["order_id"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "取消指定订单，需要用户提供订单号",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "要取消的订单号",
                    }
                },
                "required": ["order_id"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modify_order",
            "description": "修改订单信息（如地址、商品等），需要用户提供订单号和修改内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "要修改的订单号",
                    }
                },
                "required": ["order_id"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "confirm_receipt",
            "description": "确认收货，需要用户提供订单号",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "要确认收货的订单号",
                    }
                },
                "required": ["order_id"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "initiate_return",
            "description": "发起退货申请，需要用户提供订单号和退货原因",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "要退货的订单号",
                    },
                    "reason": {
                        "type": "string",
                        "description": "退货原因",
                    },
                },
                "required": ["order_id", "reason"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "initiate_exchange",
            "description": "发起换货申请，需要用户提供订单号和换货原因",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "要换货的订单号",
                    },
                    "reason": {
                        "type": "string",
                        "description": "换货原因",
                    },
                },
                "required": ["order_id", "reason"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_refund",
            "description": "查询退款进度，需要用户提供订单号",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "要查询退款的订单号",
                    }
                },
                "required": ["order_id"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_user_orders",
            "description": "列出当前用户的所有订单，展示订单号、状态、商品名称和金额，无需用户提供订单号",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "按状态筛选（可选），如 pending/paid/shipped/delivered/cancelled/returning/refunded",
                    }
                },
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "联网搜索获取最新信息，如物流追踪、外部商品信息等",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词",
                    }
                },
                "required": ["query"],
            },
        }
    },
]

# Build lookup maps
TOOL_NAMES = {t["function"]["name"] for t in TOOL_DEFINITIONS}
SYSTEM_PROMPT = """你是一个专业的电商客服助手，为用户提供购物相关的帮助。

## 能力
你可以使用多种工具来帮助用户，包括查询知识库、查询订单信息、处理售后服务等。

## 规则
1. 如果用户的问题需要查询内部知识（政策、商品信息等），使用 query_knowledge_base
2. 如果用户需要查询或操作订单，使用对应的订单工具
3. 如果用户说"查我的订单""我的订单"等，使用 list_user_orders 列出所有订单
4. list_user_orders 返回的订单列表已按状态分组，直接呈现给用户即可，不要重复转换格式
5. 用户没有提供订单号时，主动问用户要订单号，不要假设
6. 先确认用户的需求，再执行操作
7. 用友好、专业的语气回复，使用中文
8. 如果用户只是打招呼或闲聊，直接回复，不需要调用工具"""


# ---------------------------------------------------------------------------
# Tool Execution Functions
# ---------------------------------------------------------------------------


async def execute_query_knowledge_base(query: str, top_k: int = 5) -> str:
    """Search RAG knowledge base and generate a natural answer."""
    try:
        chunks = await rag_client.query(query=query, collection="knowledge_hub", top_k=top_k)
        answer = rag_generator.generate(question=query, chunks=chunks)
        return answer if answer else "知识库中未找到相关信息。"
    except Exception as e:
        logger.warning("query_knowledge_base failed: %s", e)
        return "知识库查询暂时不可用。"


async def execute_get_order_status(order_id: str) -> str:
    """Check order status via database."""
    if not order_id:
        return "请提供订单号以便查询。"
    return await order_service.get_order_status(order_id)


async def execute_cancel_order(order_id: str) -> str:
    """Cancel an order via database."""
    if not order_id:
        return "请提供要取消的订单号。"
    return await order_service.cancel_order(order_id)


async def execute_modify_order(order_id: str) -> str:
    """Modify an order via database."""
    if not order_id:
        return "请提供要修改的订单号。"
    return await order_service.modify_order(order_id)


async def execute_confirm_receipt(order_id: str) -> str:
    """Confirm receipt via database."""
    if not order_id:
        return "请提供要确认收货的订单号。"
    return await order_service.confirm_receipt(order_id)


async def execute_initiate_return(order_id: str, reason: str = "") -> str:
    """Initiate a return via database."""
    if not order_id:
        return "请提供要退货的订单号。"
    if not reason:
        return "请提供退货原因。"
    return await order_service.initiate_return(order_id, reason)


async def execute_initiate_exchange(order_id: str, reason: str = "") -> str:
    """Initiate an exchange via database."""
    if not order_id:
        return "请提供要换货的订单号。"
    if not reason:
        return "请提供换货原因。"
    return await order_service.initiate_exchange(order_id, reason)


async def execute_check_refund(order_id: str) -> str:
    """Check refund progress via database."""
    if not order_id:
        return "请提供要查询退款的订单号。"
    return await order_service.check_refund(order_id)


STATUS_LABELS = {
    "pending": "待处理",
    "paid": "已付款",
    "shipped": "已发货",
    "delivered": "已签收",
    "cancelled": "已取消",
    "returning": "退货中",
    "refunded": "已退款",
}


async def execute_list_user_orders(status: str = "") -> str:
    """List orders for the current user."""
    try:
        kw = {}
        if status:
            kw["status"] = status
        orders, total = await order_service.list_orders(page=1, page_size=50, **kw)
        if total == 0:
            return "您目前还没有订单。"

        # Group by status
        groups: dict[str, list] = {}
        for o in orders:
            label = STATUS_LABELS.get(o.status, o.status)
            groups.setdefault(label, []).append(o)

        lines = [f"共 {total} 笔订单"]
        for label, items in groups.items():
            ids = ", ".join(o.order_id for o in items)
            lines.append(f"  [{label} {len(items)}]  {ids}")
        lines.append("")
        lines.append("告诉我订单号，我来帮您查看详情。")
        return "\n".join(lines)
    except Exception as e:
        logger.warning("list_user_orders failed: %s", e)
        return "查询订单列表失败，请稍后重试。"


async def execute_search_web(query: str) -> str:
    """Web search - currently a stub."""
    # TODO: integrate with web search provider
    return f"正在联网搜索：{query}...（联网搜索功能待接入）"


# Map tool name -> execution function
TOOL_EXECUTORS = {
    "query_knowledge_base": execute_query_knowledge_base,
    "get_order_status": execute_get_order_status,
    "cancel_order": execute_cancel_order,
    "modify_order": execute_modify_order,
    "confirm_receipt": execute_confirm_receipt,
    "initiate_return": execute_initiate_return,
    "initiate_exchange": execute_initiate_exchange,
    "check_refund": execute_check_refund,
    "list_user_orders": execute_list_user_orders,
    "search_web": execute_search_web,
}
