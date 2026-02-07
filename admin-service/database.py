from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# ---------- DATABASE URL ----------
DATABASE_URL = os.getenv("ADMIN_DB_URL", "postgresql://postgres:5461@localhost:5432/tnt_admin_db")

# ---------- ENGINE ----------
engine = create_engine(DATABASE_URL)

# ---------- SESSION ----------
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ---------- BASE MODEL ----------
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
