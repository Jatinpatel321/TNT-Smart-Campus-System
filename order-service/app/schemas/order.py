from pydantic import BaseModel
from typing import List
from uuid import UUID
from datetime import datetime


class OrderItemCreate(BaseModel):
    item_id: UUID
    quantity: int


class OrderCreate(BaseModel):
    slot_id: UUID
    items: List[OrderItemCreate]


class OrderItemResponse(BaseModel):
    item_id: UUID
    quantity: int


class OrderResponse(BaseModel):
    id: UUID
    vendor_id: UUID
    slot_id: UUID
    status: str
    created_at: datetime
    items: List[OrderItemResponse]
