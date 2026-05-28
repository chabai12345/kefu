import json
import logging
import re
import time
from pathlib import Path
from typing import List

from openai import OpenAI

from config.settings import settings
from models.schemas import ChatMessage, IntentResult, MultiIntentResult

logger = logging.getLogger(__name__)


PROMPT_DIR = Path(__file__).parent.parent / "prompts"


class IntentClassifier:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self.model = settings.llm_model

    # Quick keyword-based classification for common patterns (no LLM call)
    _QUICK_RULES: list[tuple[re.Pattern, str, float]] = [
        (re.compile(r"查.*订单|我.*订单|订单.*列表|列出.*订单|所有订单"), "order_status", 0.95),
        (re.compile(r"你好|您好|嗨|hi\b|hello|在吗"), "greeting", 0.98),
        (re.compile(r"再见|bye|拜拜|88|谢谢|感谢"), "farewell", 0.95),
        (re.compile(r"转人工|人工客服|找人工|人工服务"), "human_handoff", 0.98),
        (re.compile(r"售后政策|售后|保修|质保|三包"), "after_sale_policy", 0.90),
        (re.compile(r"退货|退换货|我要退"), "return_request", 0.90),
        (re.compile(r"退款|退钱"), "refund_inquiry", 0.90),
        (re.compile(r"换货|我要换"), "exchange_request", 0.85),
        (re.compile(r"(取消|删除).*订单|订单.*(取消|删除)"), "order_cancel", 0.90),
        (re.compile(r"(修改|改).*订单|订单.*(修改|改)"), "order_modify", 0.85),
        (re.compile(r"确认收货|签收"), "order_confirm", 0.90),
        (re.compile(r"物流|快递|运送|发货|到哪"), "delivery_inquiry", 0.90),
        (re.compile(r"推荐|有什么.*推荐|推荐.*商品|买什么"), "recommendation", 0.85),
        (re.compile(r"价格|多少钱|报价|价位"), "price_inquiry", 0.85),
    ]

    def _quick_classify(self, message: str) -> MultiIntentResult | None:
        """Try keyword matching first. Returns None if no rule matches."""
        msg = message.strip().lower()
        for pattern, intent, conf in self._QUICK_RULES:
            if pattern.search(msg):
                # Extract order_id if present
                params = {}
                if intent in ("order_status", "order_cancel", "order_modify",
                             "order_confirm", "return_request", "exchange_request",
                             "refund_inquiry", "delivery_inquiry"):
                    m = re.search(r"[A-Z]{3,}\d+", message)
                    if m:
                        params["order_id"] = m.group()
                return MultiIntentResult(
                    intents=[IntentResult(id=1, intent=intent, params=params, confidence=conf)],
                    relation="parallel",
                    dependency=[],
                    primary_intent_id=1,
                    summary=intent,
                )
        return None

    def classify(
        self,
        message: str,
        history: List[ChatMessage],
    ) -> MultiIntentResult:
        history_text = "\n".join(
            f"{m.role}: {m.content}" for m in history[-5:]
        ) or "无历史记录"

        if not message or not message.strip():
            return MultiIntentResult(
                intents=[IntentResult(id=1, intent="ambiguous", params={}, confidence=0.0)],
                relation="parallel",
                dependency=[],
                primary_intent_id=1,
                summary="空消息",
            )

        # Try quick keyword matching first
        quick = self._quick_classify(message)
        if quick is not None:
            return quick

        prompt_template = (PROMPT_DIR / "intent_classification.txt").read_text(encoding="utf-8")
        user_content = prompt_template.replace("{history}", history_text).replace("{message}", message)

        try:
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    resp = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "user", "content": user_content},
                        ],
                        temperature=0.1,
                        response_format={"type": "json_object"},
                    )
                    break
                except Exception as e:
                    if attempt < max_retries:
                        time.sleep(2 ** attempt)
                        continue
                    raise

            content = resp.choices[0].message.content.strip()
            data = json.loads(content)
            result = MultiIntentResult(**data)
            # Enforce confidence threshold
            for intent in result.intents:
                if intent.confidence < 0.6:
                    intent.intent = "ambiguous"
            return result

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return MultiIntentResult(
                intents=[IntentResult(id=1, intent="ambiguous", params={}, confidence=0.0)],
                relation="parallel",
                dependency=[],
                primary_intent_id=1,
                summary="意图识别失败",
            )
