import logging
from typing import Any, Dict, List, Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class RAGClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.rag_mcp_url

    async def query(self, query: str, collection: str = "default", top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/api/v1/query",
                    json={"query": query, "collection": collection, "top_k": top_k},
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("results", [])
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return []

    async def list_collections(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/v1/collections")
                resp.raise_for_status()
                return resp.json().get("collections", [])
        except Exception as e:
            logger.error(f"List collections failed: {e}")
            return []

    async def get_document_summary(self, doc_id: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/v1/documents/{doc_id}")
                resp.raise_for_status()
                return resp.json().get("summary", "")
        except Exception as e:
            logger.error(f"Get document summary failed: {e}")
            return None
