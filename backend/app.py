import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Server starting on {settings.host}:{settings.port}")
    # Start RAG MCP client
    from tools.rag_client import rag_client
    try:
        await rag_client.start()
    except Exception as e:
        logger.warning(f"RAG MCP client failed to start: %s", e)
    cleanup_task = asyncio.create_task(_periodic_cleanup())
    yield
    cleanup_task.cancel()
    # Close RAG MCP client
    try:
        await rag_client.close()
    except Exception as e:
        logger.warning(f"RAG MCP client close error: %s", e)
    logger.info("Server shutting down")


async def _periodic_cleanup():
    while True:
        await asyncio.sleep(300)  # every 5 minutes
        from api.routes import context_mgr
        context_mgr.cleanup_expired()
        logger.debug("Session cleanup done")


app = FastAPI(title="E-Commerce CS", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=settings.host, port=settings.port, reload=settings.debug)
