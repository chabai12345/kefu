import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.ws_handler import handle_websocket
from config.settings import settings
from engine.context_manager import ContextManager
from engine.intent_classifier import IntentClassifier
from engine.multi_intent import MultiIntentHandler
from engine.router import IntentRouter
from handlers import register_all_handlers
from models.schemas import UserRequest

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize engine
classifier = IntentClassifier()
context_mgr = ContextManager(timeout_minutes=settings.session_timeout_minutes)
multi_handler = MultiIntentHandler()
register_all_handlers(multi_handler)
intent_router = IntentRouter(classifier, context_mgr, multi_handler)


@router.get("/health")
async def health():
    return {"status": "ok", "service": "ecommerce-cs"}


@router.post("/chat")
async def chat(request: UserRequest):
    response = await intent_router.route(request)
    return response


@router.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await handle_websocket(websocket, intent_router)


@router.get("/sessions/{session_id}/history")
async def get_history(session_id: str, limit: Optional[int] = 10):
    history = context_mgr.get_history(session_id, limit)
    return {"session_id": session_id, "messages": [m.dict() for m in history]}
