from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ---------- DATABASE URL ----------
import os
DATABASE_URL = os.getenv("AUTH_DB_URL", "postgresql://postgres:5461@localhost:5432/tnt_auth_db")

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
