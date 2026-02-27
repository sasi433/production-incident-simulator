from fastapi import FastAPI
import structlog

from app.core.logging import configure_logging
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware
from app.db import check_db
from app.cache import check_redis

configure_logging()
log = structlog.get_logger("app")

app = FastAPI(title="Production Incident Simulator")

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    await check_db()
    await check_redis()
    return {"ready": True}


@app.on_event("startup")
async def startup():
    log.info("application_started")