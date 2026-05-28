import time
import uuid
from typing import Dict, Optional

from models.schemas import ChatMessage, IntentType, SessionContext


class ContextManager:
    def __init__(self, timeout_minutes: int = 30):
        self._sessions: Dict[str, SessionContext] = {}
        self._timeout = timeout_minutes * 60

    def get_or_create(self, session_id: Optional[str] = None) -> SessionContext:
        if session_id and session_id in self._sessions:
            session = self._sessions[session_id]
            if time.time() - session.updated_at < self._timeout:
                session.updated_at = time.time()
                return session

        new_id = session_id or uuid.uuid4().hex[:12]
        now = time.time()
        session = SessionContext(
            session_id=new_id,
            created_at=now,
            updated_at=now,
        )
        self._sessions[new_id] = session
        return session

    def add_message(self, session_id: str, role: str, content: str):
        session = self.get_or_create(session_id)
        session.messages.append(ChatMessage(role=role, content=content))
        session.updated_at = time.time()

    def get_history(self, session_id: str, limit: int = 10) -> list:
        session = self.get_or_create(session_id)
        return session.messages[-limit:]

    def update_meta(self, session_id: str, **kwargs):
        session = self.get_or_create(session_id)
        for k, v in kwargs.items():
            setattr(session, k, v)

    def cleanup_expired(self):
        now = time.time()
        expired = [
            sid for sid, s in self._sessions.items()
            if now - s.updated_at > self._timeout
        ]
        for sid in expired:
            del self._sessions[sid]
