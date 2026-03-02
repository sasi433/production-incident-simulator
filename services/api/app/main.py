from fastapi import FastAPI
import structlog

from app.core.logging import configure_logging
from app.core.retry import retry

from app.middleware.correlation_id import CorrelationIdMiddleware
from app.middleware.request_logging import RequestLoggingMiddleware

from app.db.session import engine, Base
from app.db.seed import seed_products
from app.db.health import check_db

from app.cache import check_redis

from app.routers.products import router as products_router
from app.routers.checkout import router as checkout_router
from app.routers.auth import router as auth_router
from app.routers.cart import router as cart_router

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
    await check_db()
    await check_redis()
    return {"ready": True}


@app.on_event("startup")
async def startup():
    # Wait for dependencies
    await retry(check_db, attempts=30, delay_s=0.5)
    await retry(check_redis, attempts=30, delay_s=0.5)

    # Create tables + seed
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_products()
    log.info("application_started")