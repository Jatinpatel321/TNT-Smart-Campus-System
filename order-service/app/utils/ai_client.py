import httpx
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel

# AI Service configuration
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8004")

class ETAPredictionRequest(BaseModel):
    vendor_id: int
    slot_id: int
    current_orders: int
    historical_avg_orders: float
    time_of_day: str
    day_of_week: str

class RushDetectionRequest(BaseModel):
    vendor_id: int
    current_capacity: int
    available_capacity: int
    booking_rate_per_minute: float
    time_of_day: str
    day_of_week: str

class AIClient:
    def __init__(self):
        self.base_url = AI_SERVICE_URL

    async def predict_eta(self, request: ETAPredictionRequest) -> Optional[Dict[str, Any]]:
        """Get ETA prediction from AI service"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.base_url}/predict-eta",
                    json=request.dict()
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"AI ETA prediction failed: {response.status_code}")
                    return None
        except Exception as e:
            print(f"AI service unavailable for ETA: {e}")
            return None

    async def detect_rush(self, request: RushDetectionRequest) -> Optional[Dict[str, Any]]:
        """Get rush detection from AI service"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{self.base_url}/detect-rush",
                    json=request.dict()
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"AI rush detection failed: {response.status_code}")
                    return None
        except Exception as e:
            print(f"AI service unavailable for rush detection: {e}")
            return None

    async def health_check(self) -> bool:
        """Check if AI service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except:
            return False

# Global AI client instance
ai_client = AIClient()
