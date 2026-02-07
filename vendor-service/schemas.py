from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


# ======================
# VENDOR
# ======================
class VendorCreate(BaseModel):
    name: str
    vendor_type: str
    phone: str


class VendorResponse(BaseModel):
    id: UUID
    name: str
    vendor_type: str
    phone: str

    class Config:
        from_attributes = True


# ======================
# MENU
# ======================
class MenuCreate(BaseModel):
    name: str
    vendor_id: UUID


class MenuResponse(BaseModel):
    id: UUID
    name: str
    vendor_id: UUID

    class Config:
        from_attributes = True


# ======================
# ITEM
# ======================
class ItemCreate(BaseModel):
    name: str
    price: int
    description: Optional[str] = None
    menu_id: UUID


class ItemResponse(BaseModel):
    id: UUID
    name: str
    price: int
    description: Optional[str]
    is_available: str
    menu_id: UUID

    class Config:
        from_attributes = True


# ======================
# SLOT (THIS WAS THE BREAKER)
# ======================
class SlotCreate(BaseModel):
    vendor_id: UUID
    start_time: datetime
    end_time: datetime
    max_capacity: int = 20


class SlotResponse(BaseModel):
    id: UUID
    vendor_id: UUID
    start_time: datetime
    end_time: datetime
    max_capacity: int
    current_load: int

    class Config:
        from_attributes = True
