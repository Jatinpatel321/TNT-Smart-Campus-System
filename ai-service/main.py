from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import datetime
import random

app = FastAPI(title="TNT AI Service", version="1.0.0")

# ======================================================
# REQUEST/RESPONSE MODELS
# ======================================================

class ETAPredictionRequest(BaseModel):
    vendor_id: int
    slot_id: int
    current_orders: int
    historical_avg_orders: float
    time_of_day: str  # "morning", "afternoon", "evening"
    day_of_week: str  # "monday", "tuesday", etc.

class ETAPredictionResponse(BaseModel):
    estimated_minutes: int
    confidence_score: float  # 0-1
    factors: List[str]

class RushDetectionRequest(BaseModel):
    vendor_id: int
    current_capacity: int
    available_capacity: int
    booking_rate_per_minute: float
    time_of_day: str
    day_of_week: str

class RushDetectionResponse(BaseModel):
    is_rush_hour: bool
    rush_level: str  # "low", "medium", "high"
    confidence_score: float
    recommendations: List[str]

# ======================================================
# AI PREDICTION LOGIC
# ======================================================

def predict_eta(request: ETAPredictionRequest) -> ETAPredictionResponse:
    """
    Predict ETA based on current load and historical data.
    Using simple heuristic model (in production, this would be ML).
    """

    base_time = 15  # base preparation time in minutes

    # Factor 1: Current load multiplier
    load_multiplier = 1 + (request.current_orders / 10)  # +10% per 10 orders

    # Factor 2: Time of day multiplier
    time_multipliers = {
        "morning": 0.8,   # faster in morning
        "afternoon": 1.2, # slower during lunch rush
        "evening": 1.1    # moderate evening
    }
    time_multiplier = time_multipliers.get(request.time_of_day, 1.0)

    # Factor 3: Day of week multiplier
    weekend_days = ["saturday", "sunday"]
    day_multiplier = 1.3 if request.day_of_week.lower() in weekend_days else 1.0

    # Calculate ETA
    estimated_minutes = int(base_time * load_multiplier * time_multiplier * day_multiplier)

    # Confidence based on historical data availability
    confidence = min(0.95, request.historical_avg_orders / 50)  # higher confidence with more data

    # Factors contributing to ETA
    factors = []
    if load_multiplier > 1.5:
        factors.append("High current order volume")
    if time_multiplier > 1.1:
        factors.append(f"Peak time: {request.time_of_day}")
    if day_multiplier > 1.0:
        factors.append("Weekend demand")
    if not factors:
        factors.append("Normal operating conditions")

    return ETAPredictionResponse(
        estimated_minutes=estimated_minutes,
        confidence_score=round(confidence, 2),
        factors=factors
    )

def detect_rush(request: RushDetectionRequest) -> RushDetectionResponse:
    """
    Detect if current time is rush hour based on booking patterns.
    """

    # Calculate capacity utilization
    utilization = (request.current_capacity - request.available_capacity) / request.current_capacity

    # Rush detection logic
    is_rush = False
    rush_level = "low"
    confidence = 0.7

    # High utilization + high booking rate = rush
    if utilization > 0.8 and request.booking_rate_per_minute > 2:
        is_rush = True
        rush_level = "high"
        confidence = 0.9
    elif utilization > 0.6 and request.booking_rate_per_minute > 1:
        is_rush = True
        rush_level = "medium"
        confidence = 0.8
    elif utilization > 0.4 or request.booking_rate_per_minute > 0.5:
        rush_level = "low"
        confidence = 0.6

    # Time-based rush detection
    peak_times = ["afternoon"]  # lunch rush
    if request.time_of_day in peak_times and utilization > 0.5:
        is_rush = True
        rush_level = max(rush_level, "medium", key=lambda x: ["low", "medium", "high"].index(x))
        confidence = min(confidence + 0.1, 0.95)

    # Recommendations
    recommendations = []
    if is_rush:
        recommendations.append("Consider increasing staff or extending operating hours")
        if rush_level == "high":
            recommendations.append("Implement queue management system")
    else:
        recommendations.append("Normal operations - monitor booking rate")

    return RushDetectionResponse(
        is_rush_hour=is_rush,
        rush_level=rush_level,
        confidence_score=round(confidence, 2),
        recommendations=recommendations
    )

# ======================================================
# API ENDPOINTS
# ======================================================

@app.get("/")
def root():
    return {
        "service": "TNT AI Service",
        "status": "running",
        "endpoints": ["/predict-eta", "/detect-rush"]
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow()}

@app.post("/predict-eta", response_model=ETAPredictionResponse)
def predict_eta_endpoint(request: ETAPredictionRequest):
    """Predict estimated time of arrival for an order"""
    try:
        return predict_eta(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/detect-rush", response_model=RushDetectionResponse)
def detect_rush_endpoint(request: RushDetectionRequest):
    """Detect if current time is rush hour for a vendor"""
    try:
        return detect_rush(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

# ======================================================
# UTILITY ENDPOINTS
# ======================================================

@app.get("/test-eta")
def test_eta():
    """Test endpoint with sample data"""
    sample_request = ETAPredictionRequest(
        vendor_id=1,
        slot_id=1,
        current_orders=5,
        historical_avg_orders=20.0,
        time_of_day="afternoon",
        day_of_week="monday"
    )
    return predict_eta(sample_request)

@app.get("/test-rush")
def test_rush():
    """Test endpoint with sample data"""
    sample_request = RushDetectionRequest(
        vendor_id=1,
        current_capacity=20,
        available_capacity=5,
        booking_rate_per_minute=1.5,
        time_of_day="afternoon",
        day_of_week="monday"
    )
    return detect_rush(sample_request)
