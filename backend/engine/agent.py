"""Agent executor: LLM-driven tool calling with OpenAI-compatible function calling.

Flow:
1. Receive user message + conversation history
2. Call LLM with tool definitions
3. If LLM returns tool_calls → execute tools in parallel → feed results back
4. LLM generates final response from tool results
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI

from config.settings import settings
from models.schemas import ChatMessage
from tools.tool_definitions import (
    TOOL_DEFINITIONS,
    TOOL_EXECUTORS,
    TOOL_NAMES,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)

# Maximum rounds of tool calling to prevent infinite loops
MAX_TOOL_ROUNDS = 2

# Truncate tool results to avoid blowing the context window
MAX_TOOL_RESULT_CHARS = 1500


class AgentExecutor:
    """LLM-driven tool calling agent that decides which tools to use."""

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self.model = settings.llm_model

    async def execute(
        self,
        message: str,
        history: List[ChatMessage],
    ) -> str:
        """Execute the agent loop: LLM → tool calls → LLM → response.

        Args:
            message: The user's current message.
            history: Recent conversation history (ChatMessage list).

        Returns:
            Final response string.
        """
        # Build messages list
        messages = self._build_messages(message, history)

        for _round in range(MAX_TOOL_ROUNDS):
            # Call LLM with tools
            response = await self._call_llm(messages)

            if response is None:
                break

            # Check for tool calls
            tool_calls = response.tool_calls
            if not tool_calls:
                # LLM responded directly - return the text
                content = response.content
                if content and content.strip():
                    return content.strip()
                break

            # LLM wants to call tools - append the assistant message with tool_calls
            assistant_msg = {"role": "assistant", "content": response.content or ""}
            if tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ]
            messages.append(assistant_msg)

            # Execute all tool calls in parallel
            tool_results = await self._execute_tool_calls(tool_calls)

            # Append tool results
            for tr in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tr["tool_call_id"],
                    "content": tr["content"],
                })

        # Final fallback if nothing worked
        return await self._fallback_generate(message, history)

    def _build_messages(
        self, message: str, history: List[ChatMessage]
    ) -> List[Dict[str, Any]]:
        """Build the message list for the LLM call."""
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        # Add recent history (last 6 messages)
        for m in history[-6:]:
            messages.append({"role": m.role, "content": m.content})
        # Add current user message
        messages.append({"role": "user", "content": message})
        return messages

    async def _call_llm(self, messages: List[Dict[str, Any]]) -> Optional[Any]:
        """Call the LLM with tools, returns the response object."""
        try:
            return await asyncio.to_thread(
                self._sync_llm_call,
                messages,
            )
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            return None

    def _sync_llm_call(self, messages: List[Dict[str, Any]]) -> Any:
        """Synchronous LLM call (runs in thread to not block event loop)."""
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0.3,
            max_tokens=2048,
        ).choices[0].message

    async def _execute_tool_calls(
        self, tool_calls: List[Any]
    ) -> List[Dict[str, str]]:
        """Execute all tool calls in parallel and return results."""
        async def execute_one(tc: Any) -> Dict[str, str]:
            name = tc.function.name
            tool_call_id = tc.id

            if name not in TOOL_EXECUTORS:
                logger.warning("Unknown tool: %s", name)
                return {
                    "tool_call_id": tool_call_id,
                    "content": f"错误：未知工具 '{name}'",
                }

            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError as e:
                logger.warning("Invalid tool args for %s: %s", name, e)
                return {
                    "tool_call_id": tool_call_id,
                    "content": f"错误：工具参数格式不正确",
                }

            logger.info("Executing tool: %s args=%s", name, args)
            try:
                executor = TOOL_EXECUTORS[name]
                result = await executor(**args)
                # Truncate to prevent bloat
                if len(result) > MAX_TOOL_RESULT_CHARS:
                    result = result[:MAX_TOOL_RESULT_CHARS] + "...（结果已截断）"
                return {"tool_call_id": tool_call_id, "content": result}
            except Exception as e:
                logger.error("Tool %s execution failed: %s", name, e)
                return {
                    "tool_call_id": tool_call_id,
                    "content": f"工具执行失败：{e}",
                }

        return await asyncio.gather(*[execute_one(tc) for tc in tool_calls])

    async def _fallback_generate(self, message: str, history: list) -> str:
        """Fallback: generate response without tools."""
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
        try:
            resp = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个友好的电商客服助手。请用中文简洁地回答用户问题。"},
                    *[{"role": m.role, "content": m.content} for m in history[-3:]],
                ],
                temperature=0.7,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            logger.error("Fallback generation failed: %s", e)
            return "抱歉，我现在暂时无法回答，请稍后再试。"
