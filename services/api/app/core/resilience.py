import asyncio
import os
import random
import time
from dataclasses import dataclass
from typing import Awaitable, Callable, Optional, TypeVar

import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

T = TypeVar("T")
log = structlog.get_logger("resilience")


class DependencyUnavailable(Exception):
    """Raised when a downstream dependency is unavailable (redis/db)."""


def failure_mode() -> str:
    return os.getenv("FAILURE_MODE", "off").strip().lower()


def chaos_probability() -> float:
    try:
        return float(os.getenv("CHAOS_PROBABILITY", "0.30"))
    except ValueError:
        return 0.30


async def maybe_inject_failure(scope: str) -> None:
    """
    Controlled failure injection for the incident simulator.
    scope: e.g., "db", "redis", "handler"
    """
    mode = failure_mode()
    if mode == "off":
        return

    if mode == "db_slow" and scope == "db":
        delay_ms = int(os.getenv("DB_SLOW_MS", "1500"))
        await asyncio.sleep(delay_ms / 1000)
        return

    if mode == "redis_down" and scope == "redis":
        raise DependencyUnavailable("simulated_redis_outage")

    if mode == "random_500" and scope in ("handler", "db", "redis"):
        if random.random() < chaos_probability():
            raise RuntimeError("simulated_random_failure")


async def with_timeout(
    name: str,
    coro: Awaitable[T],
    timeout_s: float,
) -> T:
    try:
        return await asyncio.wait_for(coro, timeout=timeout_s)
    except asyncio.TimeoutError as exc:
        raise DependencyUnavailable(f"{name}_timeout") from exc


@dataclass
class CircuitBreaker:
    """
    Minimal circuit breaker:
      - opens after N consecutive failures
      - stays open for reset_timeout seconds
      - allows one trial request when half-open
    """
    name: str
    failure_threshold: int = 3
    reset_timeout_s: float = 10.0

    _state: str = "closed"  # closed | open | half_open
    _failures: int = 0
    _opened_at: float = 0.0
    _half_open_in_flight: bool = False

    def allow(self) -> bool:
        now = time.time()

        if self._state == "closed":
            return True

        if self._state == "open":
            if (now - self._opened_at) >= self.reset_timeout_s:
                self._state = "half_open"
                self._half_open_in_flight = False
                return True
            return False

        # half_open
        if self._half_open_in_flight:
            return False
        self._half_open_in_flight = True
        return True

    def on_success(self) -> None:
        self._failures = 0
        self._state = "closed"
        self._half_open_in_flight = False

    def on_failure(self) -> None:
        self._failures += 1
        self._half_open_in_flight = False

        if self._state == "half_open":
            self._state = "open"
            self._opened_at = time.time()
            return

        if self._failures >= self.failure_threshold:
            self._state = "open"
            self._opened_at = time.time()

    @property
    def state(self) -> str:
        return self._state


def retryable_dependency_call(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """
    Decorator: retries dependency failures with exponential backoff + jitter.
    """
    return retry(
        reraise=True,
        stop=stop_after_attempt(int(os.getenv("RETRY_ATTEMPTS", "3"))),
        wait=wait_exponential_jitter(
            initial=float(os.getenv("RETRY_INITIAL_S", "0.1")),
            max=float(os.getenv("RETRY_MAX_S", "1.5")),
        ),
        retry=retry_if_exception_type(DependencyUnavailable),
    )(fn)