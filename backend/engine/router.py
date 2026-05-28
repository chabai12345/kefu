import logging

from engine.context_manager import ContextManager
from engine.intent_classifier import IntentClassifier
from engine.multi_intent import MultiIntentHandler
from models.schemas import AgentResponse, HandlerResult, IntentType, MultiIntentResult, UserRequest

logger = logging.getLogger(__name__)


class IntentRouter:
    def __init__(
        self,
        classifier: IntentClassifier,
        context_mgr: ContextManager,
        multi_handler: MultiIntentHandler,
    ):
        self.classifier = classifier
        self.context_mgr = context_mgr
        self.multi_handler = multi_handler

    async def route(self, request: UserRequest) -> AgentResponse:
        # 1. Get or create session
        session = self.context_mgr.get_or_create(request.session_id)

        # 2. Add user message to history
        self.context_mgr.add_message(session.session_id, "user", request.message)

        # 3. Get history
        history = self.context_mgr.get_history(session.session_id)

        # 4. Intent classification
        multi_intent = self.classifier.classify(request.message, history)

        # 5. Check offensive
        if any(i.intent == IntentType.offensive for i in multi_intent.intents):
            reply = "很抱歉让您有不愉快的体验，我会尽力帮您解决问题。请问有什么我可以帮您的吗？"
            self.context_mgr.add_message(session.session_id, "assistant", reply)
            return AgentResponse(
                session_id=session.session_id,
                reply=reply,
                intents=multi_intent.intents,
            )

        # 6. Check human_handoff
        if any(i.intent == IntentType.human_handoff for i in multi_intent.intents):
            reply = "好的，正在为您转接人工客服，请稍候。"
            self.context_mgr.add_message(session.session_id, "assistant", reply)
            return AgentResponse(
                session_id=session.session_id,
                reply=reply,
                intents=multi_intent.intents,
                suggest_human=True,
            )

        # 7. Check ambiguous
        if all(i.intent == IntentType.ambiguous for i in multi_intent.intents):
            reply = "抱歉，我没有完全理解您的意思。您可以详细描述一下您遇到的问题吗？比如是想咨询商品、查询订单，还是需要售后帮助？"
            self.context_mgr.add_message(session.session_id, "assistant", reply)
            return AgentResponse(
                session_id=session.session_id,
                reply=reply,
                intents=multi_intent.intents,
            )

        # 8. Update session meta
        primary = next(
            (i for i in multi_intent.intents if i.id == multi_intent.primary_intent_id),
            multi_intent.intents[0],
        )
        self.context_mgr.update_meta(
            session.session_id,
            last_intent=primary.intent,
        )

        # 9. Multi-intent handling
        context = {
            "session_id": session.session_id,
            "history": history,
            "multi_intent": multi_intent,
        }
        results, reply = await self.multi_handler.resolve(multi_intent, context)

        # 10. If no handler returned content, fallback LLM reply
        if not reply:
            reply = await self._fallback_generate(request.message, history)

        self.context_mgr.add_message(session.session_id, "assistant", reply)

        return AgentResponse(
            session_id=session.session_id,
            reply=reply,
            intents=multi_intent.intents,
        )

    async def _fallback_generate(self, message: str, history: list) -> str:
        from openai import OpenAI
        from config.settings import settings

        client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
        try:
            resp = client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": "你是一个友好的电商客服助手。请用中文简洁地回答用户问题。"},
                    *[{"role": m.role, "content": m.content} for m in history[-3:]],
                ],
                temperature=0.7,
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.error(f"Fallback generation failed: {e}")
            return "抱歉，我现在暂时无法回答，请稍后再试。"
