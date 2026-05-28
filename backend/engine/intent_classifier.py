import json
import logging
from typing import List

from openai import OpenAI

from config.settings import settings
from models.schemas import ChatMessage, IntentResult, MultiIntentResult

logger = logging.getLogger(__name__)

INTENT_SYSTEM_PROMPT = """You are an intent classifier for an e-commerce customer service system.
Analyze the user's message and classify it into one or more intents.

## Intent List
- product_inquiry: 询问商品详情、规格、材质、功能等
- price_inquiry: 询问价格、优惠、折扣
- stock_inquiry: 询问库存、补货时间
- recommendation: 根据需求推荐商品
- comparison: 商品对比、选哪个好
- promotion_inquiry: 促销活动、满减、优惠券
- shipping_inquiry: 运费、配送范围、时效
- order_status: 查询订单状态、物流跟踪
- order_cancel: 取消订单
- order_modify: 修改地址/规格等
- order_confirm: 确认收货
- delivery_inquiry: 物流问题、配送异常
- return_request: 申请退货
- exchange_request: 申请换货
- refund_inquiry: 退款进度、金额
- after_sale_policy: 退换货政策咨询
- complaint: 投诉、差评处理
- warranty_inquiry: 保修期、维修服务
- account_issue: 账号登录、注册问题
- payment_issue: 支付失败、支付方式
- invoice_request: 发票申请
- point_inquiry: 积分、会员等级查询
- faq: 常见问题
- chat: 闲聊，无业务意图
- greeting: 打招呼
- farewell: 结束对话
- human_handoff: 要求转人工
- feedback: 建议反馈
- offensive: 辱骂、恶意内容

## Rules
1. Return raw JSON only, no markdown fences, no other text.
2. List ALL intents present. If multiple, determine relation.
3. relation: "parallel" (independent), "sequential" (dependent), "conflict" (contradictory).
4. confidence < 0.6 → set intent to "ambiguous".
5. If abusive → "offensive".
"""


class IntentClassifier:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self.model = settings.llm_model

    def classify(
        self,
        message: str,
        history: List[ChatMessage],
    ) -> MultiIntentResult:
        history_text = "\n".join(
            f"{m.role}: {m.content}" for m in history[-5:]
        ) or "无历史记录"

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": f"历史对话:\n{history_text}\n\n用户消息: {message}"},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            content = resp.choices[0].message.content.strip()
            data = json.loads(content)
            return MultiIntentResult(**data)

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return MultiIntentResult(
                intents=[IntentResult(id=1, intent="ambiguous", params={}, confidence=0.0)],
                relation="parallel",
                dependency=[],
                primary_intent_id=1,
                summary="意图识别失败",
            )
