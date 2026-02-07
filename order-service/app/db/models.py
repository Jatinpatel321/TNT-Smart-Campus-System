from sqlalchemy import Column, String, Integer, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
import enum
from datetime import datetime

Base = declarative_base()


# -----------------------------
# Order Status Enum
# -----------------------------
class OrderStatus(enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"


# -----------------------------
# Orders Table
# -----------------------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_phone = Column(String, nullable=False)
    vendor_id = Column(UUID(as_uuid=True), nullable=False)
    slot_id = Column(UUID(as_uuid=True), nullable=False)

    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.pending,
        nullable=False
    )

    # AI-powered ETA prediction
    estimated_minutes = Column(Integer, nullable=True)
    eta_confidence = Column(Integer, nullable=True)  # 0-100 percentage

    created_at = Column(DateTime, default=datetime.utcnow)


# -----------------------------
# Order Items Table
# -----------------------------
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    item_id = Column(UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer, nullable=False)


# -----------------------------
# Slot Reservation Table
# -----------------------------
class SlotReservation(Base):
    __tablename__ = "slot_reservations"

    slot_id = Column(UUID(as_uuid=True), primary_key=True)
    available_capacity = Column(Integer, nullable=False)
