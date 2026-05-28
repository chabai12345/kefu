import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    # LLM
    llm_provider: str = os.getenv("LLM_PROVIDER", "deepseek")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "deepseek-chat")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")

    # Embedding (for RAG)
    embedding_api_key: str = os.getenv("EMBEDDING_API_KEY", "")
    embedding_base_url: str = os.getenv("EMBEDDING_BASE_URL", "https://api.siliconflow.cn/v1")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-zh-v1.5")

    # RAG MCP Server
    rag_mcp_url: str = os.getenv("RAG_MCP_URL", "http://localhost:8000")

    # Web search
    web_search_provider: str = os.getenv("WEB_SEARCH_PROVIDER", "duckduckgo")

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8001"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Session
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

    # Third-party API stubs
    order_api_base: str = os.getenv("ORDER_API_BASE", "")
    logistics_api_base: str = os.getenv("LOGISTICS_API_BASE", "")
    payment_api_base: str = os.getenv("PAYMENT_API_BASE", "")


settings = Settings()
