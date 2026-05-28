import logging
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

logger = logging.getLogger(__name__)

RAG_SERVER_DIR = Path(r"C:\Users\dengq.DESKTOP-FPEH2CV\Desktop\RAG-MCP-SERVER")
RAG_VENV_PY = RAG_SERVER_DIR / ".venv" / "Scripts" / "python.exe"


class RAGClient:
    """MCP stdio client for the RAG MCP Server.

    Spawns the RAG server as a subprocess and communicates via MCP stdio transport.
    Managed via FastAPI lifespan (start/close).
    """

    def __init__(self) -> None:
        self._exit_stack = AsyncExitStack()
        self._session: Optional[ClientSession] = None
        self._server_params = StdioServerParameters(
            command=str(RAG_VENV_PY),
            args=["-m", "src.mcp_server.server"],
            cwd=str(RAG_SERVER_DIR),
        )

    async def start(self) -> None:
        """Connect to the RAG MCP Server via stdio and initialize the session."""
        if self._session is not None:
            return
        logger.info("Connecting to RAG MCP Server...")
        streams = await self._exit_stack.enter_async_context(
            stdio_client(self._server_params)
        )
        read_stream, write_stream = streams
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()
        logger.info("RAG MCP Server connected and initialized")

    async def close(self) -> None:
        """Close the MCP session and subprocess."""
        if self._session is None:
            return
        await self._exit_stack.aclose()
        self._session = None
        logger.info("RAG MCP Server disconnected")

    async def query(
        self, query: str, collection: str = "knowledge_hub", top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Query the RAG knowledge base.

        Args:
            query: The search query string.
            collection: Target collection name.
            top_k: Maximum results to return.

        Returns:
            List of result dicts with keys: text, score, source, title.
        """
        if not self._session:
            raise RuntimeError("RAGClient not connected. Call start() first.")

        logger.info("RAG query: '%s' (collection=%s, top_k=%d)", query[:80], collection, top_k)
        result = await self._session.call_tool(
            "query_knowledge_hub",
            {"query": query, "top_k": top_k, "collection": collection},
        )

        if result.isError:
            error_text = ""
            for content in result.content:
                if hasattr(content, "text"):
                    error_text = content.text
                    break
            logger.error("RAG query returned error: %s", error_text)
            return []

        # Parse text content blocks
        results: List[Dict[str, Any]] = []
        for content in result.content:
            if hasattr(content, "text"):
                results.append({"text": content.text, "type": "text"})
            elif hasattr(content, "data") and hasattr(content, "mimeType"):
                results.append(
                    {"data": content.data, "mimeType": content.mimeType, "type": "image"}
                )

        return results

    async def list_collections(self) -> List[str]:
        """List available collections in the knowledge base."""
        if not self._session:
            raise RuntimeError("RAGClient not connected. Call start() first.")

        result = await self._session.call_tool("list_collections", {"include_stats": True})

        collections: List[str] = []
        for content in result.content:
            if hasattr(content, "text"):
                collections.append(content.text)
        return collections


# Module-level singleton
rag_client = RAGClient()
