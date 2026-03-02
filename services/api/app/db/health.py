from sqlalchemy import text
from app.db.session import engine


async def check_db() -> None:
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))