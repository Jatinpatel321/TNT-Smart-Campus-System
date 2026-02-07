from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse
from app.core.security import require_student, require_vendor
from app.db.session import get_db
from app.services.booking import create_order, complete_order, get_vendor_orders, cancel_order, get_student_orders
from app.db.models import OrderStatus
from uuid import UUID
from typing import Optional, List
from app.services.vendor_helper import get_vendor_id_by_phone

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post("/")
async def place_order(
    data: OrderCreate,
    payload=Depends(require_student),
    db: Session = Depends(get_db)
):
    order = await create_order(
        db=db,
        student_phone=payload["sub"],
        slot_id=data.slot_id,
        items=data.items
    )

    return {
        "order_id": order.id,
        "status": order.status,
        "slot_id": order.slot_id
    }


@router.get("/vendor")
async def get_orders_for_vendor(
    status: Optional[OrderStatus] = None,
    payload=Depends(require_vendor),
    db: Session = Depends(get_db)
):
    vendor_phone = payload["sub"]  # phone from JWT

    # Get vendor_id from Vendor Service
    vendor_id = await get_vendor_id_by_phone(vendor_phone)

    orders = get_vendor_orders(
        db=db,
        vendor_id=vendor_id,
        status=status
    )

    return orders


@router.post("/{order_id}/complete")
async def complete_order_api(
    order_id: UUID,
    payload=Depends(require_vendor),
    db: Session = Depends(get_db)
):
    vendor_phone = payload["sub"]

    # Get vendor_id from Vendor Service
    vendor_id = await get_vendor_id_by_phone(vendor_phone)

    order = complete_order(
        db=db,
        order_id=order_id,
        vendor_id=vendor_id
    )

    return {
        "order_id": order.id,
        "status": order.status
    }


@router.post("/{order_id}/cancel")
async def cancel_order_api(
    order_id: UUID,
    payload=Depends(require_student),
    db: Session = Depends(get_db)
):
    student_phone = payload["sub"]

    order = cancel_order(
        db=db,
        order_id=order_id,
        student_phone=student_phone
    )

    return {
        "order_id": order.id,
        "status": order.status
    }


@router.get("/student")
async def get_student_order_history(
    status: Optional[OrderStatus] = None,
    payload=Depends(require_student),
    db: Session = Depends(get_db)
) -> List[OrderResponse]:
    student_phone = payload["sub"]

    orders = get_student_orders(
        db=db,
        student_phone=student_phone,
        status=status
    )

    # Convert to response format
    response_orders = []
    for order in orders:
        items = [
            OrderItemResponse(
                item_id=item.item_id,
                quantity=item.quantity
            )
            for item in order.items
        ]

        response_orders.append(
            OrderResponse(
                id=order.id,
                vendor_id=order.vendor_id,
                slot_id=order.slot_id,
                status=order.status.value,
                created_at=order.created_at,
                items=items
            )
        )

    return response_orders
