"""Database models and async engine setup for SQLite."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from config.settings import settings

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "ecommerce.db"
DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"
# Sync URL for sync operations (schema creation, seeding)
SYNC_DB_URL = f"sqlite:///{DB_PATH}"


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, default="default")
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        comment="pending|paid|shipped|delivered|cancelled|returning|refunded",
    )
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )
    shipping_address: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    logistics_company: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    return_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    refund_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")


def init_sync_engine():
    """Create sync engine (for schema creation and seeding)."""
    engine = create_engine(SYNC_DB_URL, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_sync_session(engine=None):
    """Get a sync session (for seeding)."""
    if engine is None:
        engine = init_sync_engine()
    Session = sessionmaker(bind=engine)
    return Session()


from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

async_engine = create_async_engine(DB_URL, echo=False)


async def get_async_session() -> AsyncSession:
    """Get an async session (for runtime queries)."""
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session
