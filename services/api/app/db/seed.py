from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Product


async def seed_products(session: AsyncSession) -> None:
    result = await session.execute(select(Product.id).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    session.add_all(
        [
            Product(name="Hoodie", price_cents=4999),
            Product(name="Mug", price_cents=1499),
            Product(name="Cap", price_cents=1999),
        ]
    )
    await session.commit()