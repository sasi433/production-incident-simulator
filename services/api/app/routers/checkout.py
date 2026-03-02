from fastapi import APIRouter
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.db.models import Order

router = APIRouter(tags=["checkout"])


class CheckoutRequest(BaseModel):
    user_id: str
    total_cents: int


@router.post("/checkout")
async def checkout(req: CheckoutRequest):
    async with SessionLocal() as session:
        order = Order(
            user_id=req.user_id,
            total_cents=req.total_cents,
        )
        session.add(order)
        await session.commit()
        return {"order_id": str(order.id)}