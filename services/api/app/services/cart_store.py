import json
import random

import structlog

from app.clients.redis_client import get_client
from app.core.config import incident_session_reset_enabled

log = structlog.get_logger("cart_store")

CART_TTL_SECONDS = 60 * 60 * 24  # 24 hours


def _write_cart_key(session_id: str) -> str:
    """
    The correct Redis key used to persist cart state.
    """
    return f"cart:{session_id}"


def _read_cart_key(session_id: str) -> str:
    """
    Normal mode:
        cart:{session_id}

    Incident mode:
        randomly choose the wrong namespace for reads:
        cart:v2:{session_id}

    This simulates a rollout or namespace mismatch bug where cart
    writes go to one key but reads sometimes look somewhere else.
    """
    if incident_session_reset_enabled():
        use_wrong_key = random.random() < 0.5
        selected_key = (
            f"cart:v2:{session_id}" if use_wrong_key else f"cart:{session_id}"
        )
        log.warning(
            "session_cart_bug_triggered",
            session_id=session_id,
            selected_key=selected_key,
            wrong_namespace=use_wrong_key,
        )
        return selected_key

    return f"cart:{session_id}"


async def get_cart(session_id: str) -> dict:
    client = get_client()
    cart_key = _read_cart_key(session_id)
    raw = await client.get(cart_key)

    if not raw:
        log.warning(
            "cart_lookup_miss",
            session_id=session_id,
            cart_key=cart_key,
        )
        return {"items": []}

    log.info(
        "cart_lookup_hit",
        session_id=session_id,
        cart_key=cart_key,
    )
    return json.loads(raw)


async def save_cart(session_id: str, cart: dict) -> None:
    client = get_client()
    cart_key = _write_cart_key(session_id)
    await client.setex(
        cart_key,
        CART_TTL_SECONDS,
        json.dumps(cart),
    )
    log.info(
        "cart_saved",
        session_id=session_id,
        cart_key=cart_key,
        item_count=len(cart.get("items", [])),
    )