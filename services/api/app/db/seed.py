from sqlalchemy import select, func
from app.db.session import SessionLocal
from app.db.models import Product


async def seed_products() -> None:
    async with SessionLocal() as session:
        existing_count = await session.scalar(select(func.count()).select_from(Product))
        if existing_count and existing_count > 0:
            return

        session.add_all(
            [
                Product(name="Hoodie", price_cents=4999),
                Product(name="Mug", price_cents=1499),
                Product(name="Cap", price_cents=1999),
            ]
        )
        await session.commit() 