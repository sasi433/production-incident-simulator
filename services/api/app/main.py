from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import structlog

from app.core.logging import configure_logging
from app.core.retry import retry
from app.core.resilience import DependencyUnavailable

from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware

from app.db.session import engine, Base, async_session_maker
from app.db.seed import seed_products
from app.db.health import check_db
from app.db.resilient import db_ping

from app.cache import check_redis

from app.clients import redis_client

from app.metrics import metrics_response

from app.routers.products import router as products_router
from app.routers.checkout import router as checkout_router
from app.routers.auth import router as auth_router
from app.routers.cart import router as cart_router

errlog = structlog.get_logger("errors")

configure_logging()
log = structlog.get_logger("app")

app = FastAPI(title="Production Incident Simulator")

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(products_router)
app.include_router(checkout_router)
app.include_router(auth_router)
app.include_router(cart_router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/readyz")
async def readyz():
    try:
        async with async_session_maker() as session:
            await db_ping(session)
        await redis_client.ping()
        return {"ready": True}
    except DependencyUnavailable as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"ready": False, "reason": str(exc)},
        )


@app.on_event("startup")
async def startup():
    # Wait for dependencies
    await retry(check_db, attempts=30, delay_s=0.5)
    await retry(check_redis, attempts=30, delay_s=0.5)

    # Create tables + seed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed products using an async session
    async with async_session_maker() as session:
        await seed_products(session)
    log.info("application_started")


@app.exception_handler(DependencyUnavailable)
async def dependency_unavailable_handler(request: Request, exc: DependencyUnavailable):
    errlog.warn(
        "dependency_unavailable",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(status_code=503, content={"error": "dependency_unavailable", "detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    errlog.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(status_code=500, content={"error": "internal_server_error"})

@app.get("/metrics")
async def metrics():
    return metrics_response()