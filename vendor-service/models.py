from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from database import Base

# ---------- Vendor ----------
class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    vendor_type = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)

    menus = relationship("Menu", back_populates="vendor", cascade="all, delete")
    slots = relationship("Slot", back_populates="vendor", cascade="all, delete")


# ---------- Menu ----------
class Menu(Base):
    __tablename__ = "menus"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)

    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"))

    vendor = relationship("Vendor", back_populates="menus")
    items = relationship("Item", back_populates="menu", cascade="all, delete")


# ---------- Item ----------
class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String)
    is_available = Column(String, default="yes")

    menu_id = Column(UUID(as_uuid=True), ForeignKey("menus.id"))

    menu = relationship("Menu", back_populates="items")


# ---------- Slot ----------
class Slot(Base):
    __tablename__ = "slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"))

    start_time = Column(Time)
    end_time = Column(Time)

    max_capacity = Column(Integer, default=20)
    current_load = Column(Integer, default=0)

    vendor = relationship("Vendor", back_populates="slots")
