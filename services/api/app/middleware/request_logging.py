import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_TOTAL

log = structlog.get_logger("http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration = time.perf_counter() - start
            status_code = response.status_code

            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                path=path,
                status=str(status_code),
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                path=path,
            ).observe(duration)

            log.info(
                "request_completed",
                method=method,
                path=path,
                status=status_code,
                duration_ms=round(duration * 1000, 2),
            )
            return response

        except Exception:
            duration = time.perf_counter() - start

            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                path=path,
                status="500",
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                path=path,
            ).observe(duration)

            log.error(
                "request_failed",
                method=method,
                path=path,
                status=500,
                duration_ms=round(duration * 1000, 2),
            )
            raise