import asyncio
from collections.abc import Awaitable, Callable


async def retry(
    fn: Callable[[], Awaitable[None]],
    *,
    attempts: int = 20,
    delay_s: float = 0.5,
    backoff: float = 1.2,
) -> None:
    last_exc: Exception | None = None
    d = delay_s
    for _ in range(attempts):
        try:
            await fn()
            return
        except Exception as e:
            last_exc = e
            await asyncio.sleep(d)
            d *= backoff
    raise last_exc if last_exc else RuntimeError("retry failed")