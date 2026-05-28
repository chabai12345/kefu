from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    # 售前
    product_inquiry = "product_inquiry"
    price_inquiry = "price_inquiry"
    stock_inquiry = "stock_inquiry"
    recommendation = "recommendation"
    comparison = "comparison"
    promotion_inquiry = "promotion_inquiry"
    shipping_inquiry = "shipping_inquiry"
    # 订单
    order_status = "order_status"
    order_cancel = "order_cancel"
    order_modify = "order_modify"
    order_confirm = "order_confirm"
    delivery_inquiry = "delivery_inquiry"
    # 售后
    return_request = "return_request"
    exchange_request = "exchange_request"
    refund_inquiry = "refund_inquiry"
    after_sale_policy = "after_sale_policy"
    complaint = "complaint"
    warranty_inquiry = "warranty_inquiry"
    # 账户
    account_issue = "account_issue"
    payment_issue = "payment_issue"
    invoice_request = "invoice_request"
    point_inquiry = "point_inquiry"
    # 通用
    faq = "faq"
    chat = "chat"
    greeting = "greeting"
    farewell = "farewell"
    human_handoff = "human_handoff"
    feedback = "feedback"
    offensive = "offensive"
    # 系统
    need_web_search = "need_web_search"
    need_rag_search = "need_rag_search"
    ambiguous = "ambiguous"


class RelationType(str, Enum):
    parallel = "parallel"
    sequential = "sequential"
    conflict = "conflict"


class IntentResult(BaseModel):
    id: int
    intent: IntentType
    params: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0)


class MultiIntentResult(BaseModel):
    intents: List[IntentResult]
    relation: RelationType
    dependency: List[List[int]] = Field(default_factory=list)
    primary_intent_id: int
    summary: str


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class SessionContext(BaseModel):
    session_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    current_order_id: Optional[str] = None
    current_product: Optional[str] = None
    last_intent: Optional[IntentType] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0


class UserRequest(BaseModel):
    session_id: str
    message: str
    platform: str = "web"


class ToolCall(BaseModel):
    tool: str
    params: Dict[str, Any]


class HandlerResult(BaseModel):
    response: str
    tool_calls: List[ToolCall] = Field(default_factory=list)
    rich_data: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    session_id: str
    reply: str
    intents: List[IntentResult]
    rich_data: Optional[Dict[str, Any]] = None
    suggest_human: bool = False
