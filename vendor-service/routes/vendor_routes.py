from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Vendor
from schemas import VendorCreate, VendorResponse
from security import verify_vendor_token

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", response_model=VendorResponse)
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    # TODO: Add authentication requirement for vendor creation in production
    # For now, allowing public vendor registration as per current requirements
    existing = db.query(Vendor).filter(Vendor.phone == vendor.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vendor already exists")

    new_vendor = Vendor(
        name=vendor.name,
        vendor_type=vendor.vendor_type,
        phone=vendor.phone
    )

    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)

    return new_vendor


@router.get("/", response_model=list[VendorResponse])
def get_all_vendors(db: Session = Depends(get_db)):
    return db.query(Vendor).all()


@router.get("/phone/{phone}", response_model=VendorResponse)
def get_vendor_by_phone(phone: str, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.phone == phone).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor
