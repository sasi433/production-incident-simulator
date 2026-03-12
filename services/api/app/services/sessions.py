import json
from datetime import datetime, timezone

import structlog

from app.clients import redis_client

log = structlog.get_logger("sessions")

SESSION_TTL_SECONDS = 60 * 60 * 24  # 24 hours


async def create_session(session_id: str, user_id: str, username: str) -> None:
    payload = {
        "user_id": user_id,
        "username": username,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await redis_client.setex(
        f"session:{session_id}",
        SESSION_TTL_SECONDS,
        json.dumps(payload),
    )
    log.info("session_created", session_id=session_id, user_id=user_id)


async def get_session(session_id: str) -> dict | None:
    raw = await redis_client.get(f"session:{session_id}")
    if not raw:
        log.warning("session_lookup_miss", session_id=session_id)
        return None

    log.info("session_lookup_hit", session_id=session_id)
    return json.loads(raw)