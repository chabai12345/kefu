"""RAG answer generator: takes retrieved chunks and generates a natural language answer via LLM."""

import json
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI

from config.settings import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个电商客服助手，请根据提供的参考信息回答用户的问题。

要求：
1. 只基于提供的参考信息回答，不要编造信息
2. 用自然、友好的语气回答
3. 如果参考信息不足以回答用户问题，直接说"根据现有知识库无法回答这个问题"
4. 回答简洁明了，有条理
5. 使用中文回答"""


class RAGGenerator:
    """Generates natural language answers from RAG-retrieved chunks using LLM."""

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self.model = settings.llm_model

    def generate(
        self,
        question: str,
        chunks: List[Dict[str, Any]],
        max_retries: int = 2,
    ) -> Optional[str]:
        """Generate a natural answer from RAG chunks.

        Args:
            question: The user's original question.
            chunks: List of RAG result dicts, each with at least a "text" key.
            max_retries: LLM call retry count on failure.

        Returns:
            Generated answer string, or None on failure.
        """
        # Filter to text chunks only
        text_chunks = [
            c.get("text", "") for c in chunks if c.get("type") == "text" and c.get("text")
        ]
        if not text_chunks:
            return None

        context = "\n\n---\n\n".join(text_chunks[:5])

        user_prompt = f"""## 用户问题
{question}

## 参考信息
{context}

请根据以上参考信息回答用户问题。"""

        for attempt in range(max_retries + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                    max_tokens=1024,
                )
                content = resp.choices[0].message.content
                if content and content.strip():
                    return content.strip()
            except Exception as e:
                logger.warning("RAG generation attempt %d failed: %s", attempt + 1, e)
                if attempt < max_retries:
                    import time
                    time.sleep(2 ** attempt)

        return None


# Module-level singleton
rag_generator = RAGGenerator()
