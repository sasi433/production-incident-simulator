import json

import structlog

from app.clients import redis_client

log = structlog.get_logger("product_cache")

PRODUCT_CACHE_TTL_SECONDS = 60


async def get_cached_product(product_id: str) -> dict | None:
    raw = await redis_client.get(f"product:{product_id}")
    if not raw:
        log.info("product_cache_miss", product_id=product_id)
        return None

    log.info("product_cache_hit", product_id=product_id)
    return json.loads(raw)


async def cache_product(product_id: str, product: dict) -> None:
    await redis_client.setex(
        f"product:{product_id}",
        PRODUCT_CACHE_TTL_SECONDS,
        json.dumps(product),
    )
    log.info("product_cached", product_id=product_id)