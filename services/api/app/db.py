from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://incidentsim:incidentsim@postgres:5432/incidentsim"

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)


async def check_db():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))