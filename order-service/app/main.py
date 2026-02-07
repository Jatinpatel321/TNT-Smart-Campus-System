from fastapi import FastAPI
from app.db.session import engine, get_db
from app.db.models import Base
from app.routers.orders import router as orders_router
from app.services.booking import sync_slot_reservations
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TNT Order Service")

app.include_router(orders_router)

@app.get("/")
def root():
    return {"service": "TNT Order Service", "status": "running"}

@app.on_event("startup")
async def startup_event():
    """Sync slot reservations on startup"""
    db: Session = next(get_db())
    try:
        await sync_slot_reservations(db)
    finally:
        db.close()
