from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from api.deps.vendor import get_current_vendor
from database import get_db
from models import Slot
from schemas import SlotCreate, SlotResponse
from security import verify_vendor_token

# 🔐 ROUTER-LEVEL SECURITY (APPLIED ONCE)
router = APIRouter(
    prefix="/slots",
    tags=["Slots"],
    dependencies=[Depends(verify_vendor_token)]
)

# --------------------------------------------------
# CREATE SLOT (vendor ownership + overlap prevention)
# --------------------------------------------------
@router.post("/", response_model=SlotResponse)
def create_slot(
    slot: SlotCreate,
    db: Session = Depends(get_db),
    current_vendor = Depends(get_current_vendor),
):
    # 1️⃣ Prevent overlapping slots for same vendor
    overlapping_slot = (
        db.query(Slot)
        .filter(
            Slot.vendor_id == current_vendor.id,
            and_(
                Slot.start_time < slot.end_time,
                Slot.end_time > slot.start_time,
            )
        )
        .first()
    )

    if overlapping_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot time overlaps with an existing slot"
        )

    new_slot = Slot(
        vendor_id=current_vendor.id,
        start_time=slot.start_time,
        end_time=slot.end_time,
        max_capacity=slot.max_capacity
    )

    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    return new_slot


# --------------------------------------------------
# GET ALL SLOTS (vendor scoped)
# --------------------------------------------------
@router.get("/", response_model=list[SlotResponse])
def get_slots(
    db: Session = Depends(get_db),
    current_vendor = Depends(get_current_vendor),
):
    return (
        db.query(Slot)
        .filter(Slot.vendor_id == current_vendor.id)
        .all()
    )


# --------------------------------------------------
# GET SLOT BY ID (vendor scoped)
# --------------------------------------------------
@router.get("/{slot_id}", response_model=SlotResponse)
def get_slot(
    slot_id: str,
    db: Session = Depends(get_db),
    current_vendor = Depends(get_current_vendor),
):
    slot = (
        db.query(Slot)
        .filter(
            Slot.id == slot_id,
            Slot.vendor_id == current_vendor.id
        )
        .first()
    )

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )

    return slot


# --------------------------------------------------
# UPDATE SLOT (vendor ownership enforced)
# --------------------------------------------------
@router.put("/{slot_id}", response_model=SlotResponse)
def update_slot(
    slot_id: str,
    slot: SlotCreate,
    db: Session = Depends(get_db),
    current_vendor = Depends(get_current_vendor),
):
    existing_slot = (
        db.query(Slot)
        .filter(
            Slot.id == slot_id,
            Slot.vendor_id == current_vendor.id
        )
        .first()
    )

    if not existing_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )

    # Prevent overlap on update
    overlapping_slot = (
        db.query(Slot)
        .filter(
            Slot.vendor_id == current_vendor.id,
            Slot.id != slot_id,
            and_(
                Slot.start_time < slot.end_time,
                Slot.end_time > slot.start_time,
            )
        )
        .first()
    )

    if overlapping_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Updated slot overlaps with another slot"
        )

    existing_slot.start_time = slot.start_time
    existing_slot.end_time = slot.end_time
    existing_slot.max_capacity = slot.max_capacity

    db.commit()
    db.refresh(existing_slot)

    return existing_slot


# --------------------------------------------------
# DELETE SLOT
# --------------------------------------------------
@router.delete("/{slot_id}")
def delete_slot(
    slot_id: str,
    db: Session = Depends(get_db),
    current_vendor = Depends(get_current_vendor),
):
    slot = (
        db.query(Slot)
        .filter(
            Slot.id == slot_id,
            Slot.vendor_id == current_vendor.id
        )
        .first()
    )

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )

    db.delete(slot)
    db.commit()

    return {"message": "Slot deleted"}
