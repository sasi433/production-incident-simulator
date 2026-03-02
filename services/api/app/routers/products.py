from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models import Product
import uuid

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def list_products():
    async with SessionLocal() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        return [
            {
                "id": str(p.id),
                "name": p.name,
                "price_cents": p.price_cents,
            }
            for p in products
        ]


@router.get("/{product_id}")
async def get_product(product_id: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Product).where(Product.id == uuid.UUID(product_id))
        )
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return {
            "id": str(product.id),
            "name": product.name,
            "price_cents": product.price_cents,
        }