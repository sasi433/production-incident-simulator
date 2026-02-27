import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

HEADER = "X-Request-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id  # <-- reliable storage

        response: Response = await call_next(request)
        response.headers[HEADER] = request_id
        return response