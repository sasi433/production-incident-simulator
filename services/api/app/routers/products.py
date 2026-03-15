import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
import structlog

from app.db.models import Product
from app.db.session import SessionLocal
from app.services.product_cache import cache_product, get_cached_product

router = APIRouter(prefix="/products", tags=["products"])
log = structlog.get_logger("products")


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
    try:
        product_uuid = uuid.UUID(product_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_product_id")

    cached = await get_cached_product(product_id)
    if cached:
        log.info("product_returned_from_cache", requested_product_id=product_id)
        return cached

    async with SessionLocal() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_uuid)
        )
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        payload = {
            "id": str(product.id),
            "name": product.name,
            "price_cents": product.price_cents,
        }

        await cache_product(product_id, payload)
        log.info("product_loaded_from_db", product_id=product_id)
        return payload