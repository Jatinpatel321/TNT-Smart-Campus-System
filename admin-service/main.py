from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import httpx

from database import get_db, engine, Base
from models import AdminLog
from security import require_admin

# Base.metadata.create_all(bind=engine)  # Commented out to avoid startup issues

app = FastAPI(title="TNT Admin Service")

@app.get("/")
def root():
    return {"service": "TNT Admin Service", "status": "running"}

# ======================================================
# VIEW ALL VENDORS
# ======================================================
@app.get("/vendors")
async def get_all_vendors(payload=Depends(require_admin)):
    """Admin-only: View all vendors across the system"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/vendors/")
            if response.status_code == 200:
                vendors = response.json()
                # Log admin action
                log_admin_action("VIEW_VENDORS", payload["sub"])
                return {"vendors": vendors, "count": len(vendors)}
            else:
                raise HTTPException(status_code=500, detail="Failed to fetch vendors")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service unavailable: {str(e)}")

# ======================================================
# VIEW ALL ORDERS
# ======================================================
@app.get("/orders")
async def get_all_orders(
    status: str = None,
    limit: int = 50,
    payload=Depends(require_admin)
):
    """Admin-only: View all orders across the system"""
    try:
        async with httpx.AsyncClient() as client:
            # Get orders from order service
            url = f"http://localhost:8002/orders?limit={limit}"
            if status:
                url += f"&status={status}"

            response = await client.get(url)
            if response.status_code == 200:
                orders = response.json()
                # Log admin action
                log_admin_action("VIEW_ORDERS", payload["sub"])
                return {"orders": orders, "count": len(orders)}
            else:
                raise HTTPException(status_code=500, detail="Failed to fetch orders")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service unavailable: {str(e)}")

# ======================================================
# SLOT UTILIZATION REPORT
# ======================================================
@app.get("/reports/slot-utilization")
async def get_slot_utilization(payload=Depends(require_admin)):
    """Admin-only: View slot utilization across all vendors"""
    try:
        async with httpx.AsyncClient() as client:
            # Get all slots from vendor service
            response = await client.get("http://localhost:8001/slots/")
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch slots")

            slots = response.json()

            # Get reservations from order service
            res_response = await client.get("http://localhost:8002/reservations/")
            reservations = res_response.json() if res_response.status_code == 200 else []

            # Calculate utilization
            utilization_report = []
            for slot in slots:
                slot_id = slot["id"]
                max_capacity = slot["max_capacity"]
                current_load = slot.get("current_load", 0)

                # Find reservation data
                reservation = next((r for r in reservations if r["slot_id"] == slot_id), None)
                available = reservation["available_capacity"] if reservation else max_capacity

                utilization = {
                    "slot_id": slot_id,
                    "vendor_id": slot["vendor_id"],
                    "max_capacity": max_capacity,
                    "current_load": current_load,
                    "available_capacity": available,
                    "utilization_percentage": ((max_capacity - available) / max_capacity * 100) if max_capacity > 0 else 0
                }
                utilization_report.append(utilization)

            # Log admin action
            log_admin_action("VIEW_UTILIZATION", payload["sub"])

            return {
                "utilization_report": utilization_report,
                "total_slots": len(utilization_report),
                "average_utilization": sum(u["utilization_percentage"] for u in utilization_report) / len(utilization_report) if utilization_report else 0
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service unavailable: {str(e)}")

# ======================================================
# SYSTEM HEALTH CHECK
# ======================================================
@app.get("/health")
async def system_health(payload=Depends(require_admin)):
    """Admin-only: Check health of all services"""
    health_status = {}

    services = {
        "auth": "http://localhost:8000/health",
        "vendor": "http://localhost:8001/",
        "order": "http://localhost:8002/"
    }

    async with httpx.AsyncClient() as client:
        for service_name, url in services.items():
            try:
                response = await client.get(url, timeout=5.0)
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }

    # Log admin action
    log_admin_action("HEALTH_CHECK", payload["sub"])

    return {
        "system_health": health_status,
        "overall_status": "healthy" if all(h["status"] == "healthy" for h in health_status.values()) else "degraded"
    }

# ======================================================
# ADMIN ACTION LOGGING
# ======================================================
def log_admin_action(action: str, admin_phone: str):
    """Log admin actions for audit trail"""
    try:
        db = next(get_db())
        log_entry = AdminLog(
            admin_phone=admin_phone,
            action=action
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        # Log to console if DB logging fails
        print(f"Failed to log admin action: {e}")
