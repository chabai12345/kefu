import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="E-Commerce CS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    logger.info(f"Server starting on {settings.host}:{settings.port}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=settings.host, port=settings.port, reload=settings.debug)
