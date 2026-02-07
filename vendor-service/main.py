from fastapi import FastAPI
from database import engine, Base
import models  # IMPORTANT

Base.metadata.create_all(bind=engine)

from routes.vendor_routes import router as vendor_router
from routes.menu_routes import router as menu_router
from routes.item_routes import router as item_router
from routes.slot_routes import router as slot_router

app = FastAPI(title="TNT Vendor Service")

@app.get("/")
def root():
    return {
        "service": "TNT Vendor Service",
        "status": "running",
        "docs": "/docs"
    }

app.include_router(vendor_router)
app.include_router(menu_router)
app.include_router(item_router)
app.include_router(slot_router)
