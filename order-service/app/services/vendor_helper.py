from app.utils.vendor_client import get_vendor_id_by_phone as get_vendor_id_from_service


async def get_vendor_id_by_phone(phone: str):
    return await get_vendor_id_from_service(phone)
