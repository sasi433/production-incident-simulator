import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

log = structlog.get_logger("http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        try:
            response = await call_next(request)

            duration_ms = (time.perf_counter() - start) * 1000

            log.info(
                "request_completed",
                request_id=getattr(request.state, "request_id", None),
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            return response

        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000

            log.error(
                "request_failed",
                request_id=getattr(request.state, "request_id", None),
                method=request.method,
                path=request.url.path,
                status=500,
                duration_ms=round(duration_ms, 2),
            )
            raise