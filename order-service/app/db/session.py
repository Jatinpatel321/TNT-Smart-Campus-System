from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
DATABASE_URL = os.getenv("ORDER_DB_URL", "postgresql://postgres:5461@localhost:5432/tnt_orders")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ✅ THIS WAS MISSING
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
