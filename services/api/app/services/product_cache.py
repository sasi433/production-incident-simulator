import json

import structlog

from app.clients.redis_client import get_client
from app.core.config import incident_pricing_cache_enabled

log = structlog.get_logger("product_cache")

PRODUCT_CACHE_TTL_SECONDS = 60


def _cache_key(product_id: str) -> str:
    if incident_pricing_cache_enabled():
        log.warning(
            "pricing_cache_bug_triggered",
            product_id=product_id,
            cache_key="product:shared",
        )
        return "product:shared"

    return f"product:{product_id}"


async def get_cached_product(product_id: str) -> dict | None:
    cache_key = _cache_key(product_id)
    client = get_client()
    raw = await client.get(cache_key)

    if not raw:
        log.info("product_cache_miss", product_id=product_id, cache_key=cache_key)
        return None

    log.info("product_cache_hit", product_id=product_id, cache_key=cache_key)
    return json.loads(raw)


async def cache_product(product_id: str, product: dict) -> None:
    cache_key = _cache_key(product_id)
    client = get_client()
    await client.setex(
        cache_key,
        PRODUCT_CACHE_TTL_SECONDS,
        json.dumps(product),
    )
    log.info("product_cached", product_id=product_id, cache_key=cache_key)