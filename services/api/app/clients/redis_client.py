import os
from typing import Optional

import redis.asyncio as redis
import structlog

from app.core.resilience import CircuitBreaker, DependencyUnavailable, maybe_inject_failure, retryable_dependency_call, with_timeout

log = structlog.get_logger("redis")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
REDIS_TIMEOUT_S = float(os.getenv("REDIS_TIMEOUT_S", "0.4"))

breaker = CircuitBreaker(
    name="redis",
    failure_threshold=int(os.getenv("REDIS_CB_FAILS", "3")),
    reset_timeout_s=float(os.getenv("REDIS_CB_RESET_S", "10")),
)

_client: Optional[redis.Redis] = None


def get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_timeout=REDIS_TIMEOUT_S,
            socket_connect_timeout=REDIS_TIMEOUT_S,
        )
    return _client


@retryable_dependency_call
async def ping() -> bool:
    if not breaker.allow():
        raise DependencyUnavailable("redis_circuit_open")

    #await maybe_inject_failure("redis")

    try:
        ok = await with_timeout("redis", get_client().ping(), REDIS_TIMEOUT_S)
        breaker.on_success()
        return bool(ok)
    except Exception as exc:
        breaker.on_failure()
        log.warn("redis_ping_failed", error=str(exc), breaker_state=breaker.state)
        raise DependencyUnavailable("redis_unavailable") from exc


@retryable_dependency_call
async def get(key: str) -> Optional[str]:
    if not breaker.allow():
        raise DependencyUnavailable("redis_circuit_open")

    #await maybe_inject_failure("redis")

    try:
        val = await with_timeout("redis", get_client().get(key), REDIS_TIMEOUT_S)
        breaker.on_success()
        return val
    except Exception as exc:
        breaker.on_failure()
        log.warn("redis_get_failed", key=key, error=str(exc), breaker_state=breaker.state)
        raise DependencyUnavailable("redis_unavailable") from exc


@retryable_dependency_call
async def setex(key: str, ttl_s: int, value: str) -> None:
    if not breaker.allow():
        raise DependencyUnavailable("redis_circuit_open")

    #await maybe_inject_failure("redis")

    try:
        await with_timeout("redis", get_client().setex(key, ttl_s, value), REDIS_TIMEOUT_S)
        breaker.on_success()
    except Exception as exc:
        breaker.on_failure()
        log.warn("redis_setex_failed", key=key, error=str(exc), breaker_state=breaker.state)
        raise DependencyUnavailable("redis_unavailable") from exc