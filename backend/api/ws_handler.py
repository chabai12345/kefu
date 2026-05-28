import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from engine.router import IntentRouter
from models.schemas import UserRequest

logger = logging.getLogger(__name__)


async def handle_websocket(websocket: WebSocket, router: IntentRouter):
    await websocket.accept()
    session_id = f"ws_{id(websocket):x}"

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            message = data.get("message", "")
            if not message.strip():
                continue

            request = UserRequest(session_id=session_id, message=message, platform="web")
            response = await router.route(request)

            await websocket.send_json(response.dict())

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"error": "Internal server error"})
        except Exception:
            pass
