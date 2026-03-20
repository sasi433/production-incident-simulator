import asyncio
import random

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import incident_checkout_enabled
from app.db.models import Order
from app.db.session import async_session_maker
from app.metrics import CHECKOUT_FAILURES_TOTAL, CHECKOUT_REQUESTS_TOTAL

router = APIRouter(tags=["checkout"])
log = structlog.get_logger("checkout")


class CheckoutRequest(BaseModel):
    user_id: str
    total_cents: int


@router.post("/checkout")
async def checkout(req: CheckoutRequest):
    # metric: every checkout attempt
    CHECKOUT_REQUESTS_TOTAL.inc()

    if incident_checkout_enabled():
        roll = random.random()

        # Incident mode: intermittent failure injection to test alerting/rollback.
        # 25% hard failure
        if roll < 0.25:
            CHECKOUT_FAILURES_TOTAL.inc()

            log.warning(
                "incident_checkout_failure_triggered",
                incident="checkout_intermittent_failure",
                user_id=req.user_id,
                total_cents=req.total_cents,
            )
            raise HTTPException(status_code=500, detail="Simulated checkout intermittent failure")

        # optional extra realism: another 25% gets slow
        if roll < 0.50:
            log.warning(
                "incident_checkout_delay_triggered",
                incident="checkout_intermittent_failure",
                delay_seconds=2,
                user_id=req.user_id,
                total_cents=req.total_cents,
            )
            await asyncio.sleep(2)

    async with async_session_maker() as session:
        order = Order(
            user_id=req.user_id,
            total_cents=req.total_cents,
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)

        log.info(
            "checkout_completed",
            order_id=str(order.id),
            user_id=req.user_id,
            total_cents=req.total_cents,
        )

        return {"order_id": str(order.id)}