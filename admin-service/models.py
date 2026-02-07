from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AdminLog(Base):
    __tablename__ = "admin_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_phone = Column(String, nullable=False)
    action = Column(String, nullable=False)  # VIEW_VENDORS, VIEW_ORDERS, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
