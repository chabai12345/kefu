import asyncio
import logging
from typing import Awaitable, Callable, Dict, List, Tuple

from models.schemas import (
    HandlerResult,
    IntentResult,
    IntentType,
    MultiIntentResult,
    RelationType,
)

logger = logging.getLogger(__name__)

HandlerFunc = Callable[[IntentResult, Dict], Awaitable[HandlerResult]]


class MultiIntentHandler:
    def __init__(self):
        self._handlers: Dict[IntentType, HandlerFunc] = {}

    def register(self, intent: IntentType, handler: HandlerFunc):
        self._handlers[intent] = handler

    async def resolve(
        self,
        multi_intent: MultiIntentResult,
        context: Dict,
    ) -> Tuple[List[HandlerResult], str]:
        relation = multi_intent.relation
        intent_map = {i.id: i for i in multi_intent.intents}

        if relation == RelationType.parallel:
            return await self._handle_parallel(multi_intent.intents, context)

        elif relation == RelationType.sequential:
            return await self._handle_sequential(
                multi_intent.intents, multi_intent.dependency, intent_map, context
            )

        elif relation == RelationType.conflict:
            return await self._handle_conflict(multi_intent.intents, context)

        return [], "无法处理该意图组合"

    async def _handle_parallel(
        self,
        intents: List[IntentResult],
        context: Dict,
    ) -> Tuple[List[HandlerResult], str]:
        tasks = []
        for intent in intents:
            handler = self._handlers.get(intent.intent)
            if handler:
                tasks.append(handler(intent, context))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results: List[HandlerResult] = []
        for r in results:
            if isinstance(r, HandlerResult):
                valid_results.append(r)
            elif isinstance(r, Exception):
                logger.error(f"Parallel handler error: {r}")

        merged = "\n\n".join(r.response for r in valid_results)
        return valid_results, merged

    async def _handle_sequential(
        self,
        intents: List[IntentResult],
        dependency: List[List[int]],
        intent_map: Dict[int, IntentResult],
        context: Dict,
    ) -> Tuple[List[HandlerResult], str]:
        results: List[HandlerResult] = []
        executed = set()

        for group_ids in dependency:
            for id_ in group_ids:
                intent = intent_map.get(id_)
                if not intent:
                    continue
                handler = self._handlers.get(intent.intent)
                if not handler:
                    continue

                context["_previous_results"] = results
                result = await handler(intent, context)
                results.append(result)
                executed.add(id_)

        # Handle remaining intents not in dependency
        for intent in intents:
            if intent.id not in executed:
                handler = self._handlers.get(intent.intent)
                if handler:
                    result = await handler(intent, context)
                    results.append(result)

        responses = "\n\n".join(r.response for r in results)
        return results, responses

    async def _handle_conflict(
        self,
        intents: List[IntentResult],
        context: Dict,
    ) -> Tuple[List[HandlerResult], str]:
        if not intents:
            return [], "请确认您的具体需求"
        best = max(intents, key=lambda i: i.confidence)
        if best.confidence < 0.7:
            return [], "您刚才提到了几种不同的操作，请问您最终想怎么做呢？"

        handler = self._handlers.get(best.intent)
        if handler:
            result = await handler(best, context)
            return [result], result.response

        return [], "请确认您的具体需求"
