import json
import logging
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
