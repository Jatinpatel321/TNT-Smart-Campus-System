from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models import (
    Order,
    OrderItem,
    SlotReservation,
    OrderStatus
)
from app.utils.vendor_client import get_slot_by_id
from app.utils.redis_client import redis_client
from app.utils.ai_client import ai_client
import logging

logger = logging.getLogger(__name__)


# ======================================================
# HELPER FUNCTIONS
# ======================================================
def _get_time_of_day() -> str:
    """Get current time of day category"""
    import datetime
    hour = datetime.datetime.utcnow().hour
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    else:
        return "evening"

def _get_day_of_week() -> str:
    """Get current day of week"""
    import datetime
    return datetime.datetime.utcnow().strftime("%A").lower()


# ======================================================
# CREATE ORDER (STUDENT)
# ======================================================
async def create_order(
    db: Session,
    student_phone: str,
    slot_id,
    items
):
    # 1️⃣ Get slot info from Vendor Service
    slot = await get_slot_by_id(slot_id)
    vendor_id = slot["vendor_id"]

    # 2️⃣ Prevent double booking (same student, same slot)
    existing = db.query(Order).filter(
        Order.student_phone == student_phone,
        Order.slot_id == slot_id,
        Order.status != OrderStatus.cancelled
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="You have already booked this slot"
        )

    # 3️⃣ Acquire Redis distributed lock for slot (PREVENTS RACE CONDITIONS)
    lock_key = f"slot_lock:{slot_id}"
    if not redis_client.acquire_lock(lock_key, ttl_seconds=30):
        logger.warning(f"Failed to acquire lock for slot {slot_id}")
        raise HTTPException(
            status_code=409,
            detail="Slot is currently being booked by another user. Please try again."
        )

    try:
        # 4️⃣ Lock slot reservation row (DATABASE LEVEL)
        reservation = (
            db.query(SlotReservation)
            .filter(SlotReservation.slot_id == slot_id)
            .with_for_update()
            .first()
        )

        if not reservation or reservation.available_capacity <= 0:
            raise HTTPException(
                status_code=409,
                detail="Slot is full"
            )

        # 5️⃣ Decrease capacity
        reservation.available_capacity -= 1

        # 6️⃣ Create order
        order = Order(
            student_phone=student_phone,
            vendor_id=vendor_id,
            slot_id=slot_id,
            status=OrderStatus.confirmed
        )
        db.add(order)
        db.flush()  # generate order.id

        # 7️⃣ Create order items
        for item in items:
            db.add(
                OrderItem(
                    order_id=order.id,
                    item_id=item.item_id,
                    quantity=item.quantity
                )
            )

        # 8️⃣ Get AI-powered ETA prediction
        eta_prediction = None
        try:
            # Get current order count for this vendor
            current_orders = db.query(Order).filter(
                Order.vendor_id == vendor_id,
                Order.status == OrderStatus.confirmed
            ).count()

            # Prepare AI request
            from app.utils.ai_client import ETAPredictionRequest
            import datetime

            eta_request = ETAPredictionRequest(
                vendor_id=vendor_id,
                slot_id=slot_id,
                current_orders=current_orders,
                historical_avg_orders=15.0,  # TODO: Calculate from historical data
                time_of_day=self._get_time_of_day(),
                day_of_week=self._get_day_of_week()
            )

            eta_prediction = await ai_client.predict_eta(eta_request)
        except Exception as e:
            logger.warning(f"ETA prediction failed: {e}")

        # 9️⃣ Commit transaction
        db.commit()
        db.refresh(order)

        # 10️⃣ Add ETA to order response
        if eta_prediction:
            order.estimated_minutes = eta_prediction.get("estimated_minutes")
            order.eta_confidence = eta_prediction.get("confidence_score")

        return order

    finally:
        # 9️⃣ Always release Redis lock
        redis_client.release_lock(lock_key)


# ======================================================
# CANCEL ORDER (STUDENT)
# ======================================================
def cancel_order(
    db: Session,
    order_id,
    student_phone: str
):
    # 1️⃣ Fetch order (ownership enforced)
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.student_phone == student_phone
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # 2️⃣ Validate order state
    if order.status == OrderStatus.cancelled:
        raise HTTPException(
            status_code=400,
            detail="Order already cancelled"
        )

    if order.status == OrderStatus.completed:
        raise HTTPException(
            status_code=400,
            detail="Completed orders cannot be cancelled"
        )

    # 3️⃣ Lock slot reservation row
    reservation = (
        db.query(SlotReservation)
        .filter(SlotReservation.slot_id == order.slot_id)
        .with_for_update()
        .first()
    )

    if not reservation:
        raise HTTPException(
            status_code=500,
            detail="Slot reservation missing"
        )

    # 4️⃣ Restore slot capacity
    reservation.available_capacity += 1

    # 5️⃣ Update order status
    order.status = OrderStatus.cancelled

    # 6️⃣ Commit transaction
    db.commit()
    db.refresh(order)

    return order


# ======================================================
# SYNC SLOT RESERVATIONS (INITIALIZE FROM VENDOR SERVICE)
# ======================================================
async def sync_slot_reservations(db: Session):
    """
    Sync SlotReservation table with slots from Vendor Service.
    This should be called on startup or periodically.
    """
    import httpx

    VENDOR_SERVICE_URL = "http://localhost:8001"

    async with httpx.AsyncClient() as client:
        # Get all vendors first
        vendors_response = await client.get(f"{VENDOR_SERVICE_URL}/vendors/")
        if vendors_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch vendors")

        vendors = vendors_response.json()

        for vendor in vendors:
            # Get slots for each vendor
            slots_response = await client.get(f"{VENDOR_SERVICE_URL}/slots/", headers={"Authorization": f"Bearer {vendor['phone']}"})
            if slots_response.status_code == 200:
                slots = slots_response.json()
                for slot in slots:
                    # Upsert SlotReservation
                    reservation = db.query(SlotReservation).filter(SlotReservation.slot_id == slot["id"]).first()
                    if not reservation:
                        reservation = SlotReservation(
                            slot_id=slot["id"],
                            available_capacity=slot["max_capacity"]
                        )
                        db.add(reservation)
                    else:
                        # Update capacity if changed
                        reservation.available_capacity = slot["max_capacity"]

        db.commit()


from typing import Optional
from app.db.models import Order


def get_vendor_orders(
    db: Session,
    vendor_id,
    status: Optional[OrderStatus] = None
):
    query = db.query(Order).filter(
        Order.vendor_id == vendor_id
    )

    if status:
        query = query.filter(Order.status == status)

    return query.order_by(Order.created_at.desc()).all()


def get_student_orders(
    db: Session,
    student_phone: str,
    status: Optional[OrderStatus] = None
):
    query = db.query(Order).filter(
        Order.student_phone == student_phone
    )

    if status:
        query = query.filter(Order.status == status)

    return query.order_by(Order.created_at.desc()).all()


def complete_order(
    db,
    order_id,
    vendor_id
):
    # 1️⃣ Fetch order (vendor ownership enforced)
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.vendor_id == vendor_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # 2️⃣ Validate order status
    if order.status == OrderStatus.completed:
        raise HTTPException(
            status_code=400,
            detail="Order already completed"
        )

    if order.status != OrderStatus.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Only confirmed orders can be completed"
        )

    # 3️⃣ Update status
    order.status = OrderStatus.completed

    db.commit()
    db.refresh(order)

    return order
