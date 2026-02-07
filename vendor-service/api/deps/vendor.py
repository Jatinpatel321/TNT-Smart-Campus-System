from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Vendor
from security import verify_vendor_token


def get_current_vendor(
    token_data=Depends(verify_vendor_token),
    db: Session = Depends(get_db),
):
    vendor = (
        db.query(Vendor)
        .filter(Vendor.phone == token_data.phone)
        .first()
    )

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor account not found"
        )

    return vendor
