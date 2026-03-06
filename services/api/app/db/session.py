import os

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://incidentsim:incidentsim@postgres:5432/incidentsim",
)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)


class Base(DeclarativeBase):
    pass


async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Backwards compatible name used across the codebase
SessionLocal = async_session_maker