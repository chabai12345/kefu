import json
import logging
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

        prompt_template = (PROMPT_DIR / "intent_classification.txt").read_text(encoding="utf-8")
        user_content = prompt_template.replace("{history}", history_text).replace("{message}", message)

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": user_content},
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
