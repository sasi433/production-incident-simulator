import json

import structlog

from app.clients import redis_client

log = structlog.get_logger("cart_store")

CART_TTL_SECONDS = 60 * 60 * 24  # 24 hours


async def get_cart(session_id: str) -> dict:
    raw = await redis_client.get(f"cart:{session_id}")
    if not raw:
        log.info("cart_cache_miss", session_id=session_id)
        return {"items": []}

    log.info("cart_cache_hit", session_id=session_id)
    return json.loads(raw)


async def save_cart(session_id: str, cart: dict) -> None:
    await redis_client.setex(
        f"cart:{session_id}",
        CART_TTL_SECONDS,
        json.dumps(cart),
    )
    log.info(
        "cart_saved",
        session_id=session_id,
        item_count=len(cart.get("items", [])),
    )