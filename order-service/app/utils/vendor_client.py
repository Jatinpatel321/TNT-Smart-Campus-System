import httpx
from fastapi import HTTPException

VENDOR_SERVICE_URL = "http://localhost:8001"  # adjust if needed


async def get_slot_by_id(slot_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{VENDOR_SERVICE_URL}/slots/{slot_id}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail="Slot not found in vendor service"
        )

    return response.json()


async def get_vendor_id_by_phone(phone: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{VENDOR_SERVICE_URL}/vendors/phone/{phone}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=403,
            detail="Vendor not found"
        )

    vendor_data = response.json()
    return vendor_data["id"]
