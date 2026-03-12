from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
import structlog

from app.dependencies.session import require_session
from app.services.cart_store import get_cart, save_cart

router = APIRouter(prefix="/cart", tags=["cart"])
log = structlog.get_logger("cart")


class AddCartItemRequest(BaseModel):
    product_id: str
    qty: int = Field(default=1, ge=1)


@router.get("")
async def read_cart(session=Depends(require_session)):
    session_id = session["session_id"]
    cart = await get_cart(session_id)

    log.info(
        "cart_loaded",
        session_id=session_id,
        item_count=len(cart.get("items", [])),
    )
    return cart


@router.post("/items")
async def add_to_cart(payload: AddCartItemRequest, session=Depends(require_session)):
    session_id = session["session_id"]
    cart = await get_cart(session_id)

    for item in cart["items"]:
        if item["product_id"] == payload.product_id:
            item["qty"] += payload.qty
            break
    else:
        cart["items"].append(
            {
                "product_id": payload.product_id,
                "qty": payload.qty,
            }
        )

    await save_cart(session_id, cart)

    log.info(
        "cart_updated",
        session_id=session_id,
        product_id=payload.product_id,
        qty=payload.qty,
        item_count=len(cart["items"]),
    )
    return cart