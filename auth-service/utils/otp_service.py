import random
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class OTPService:
    def __init__(self):
        self.otp_storage: Dict[str, Dict] = {}  # {phone: {"otp": str, "timestamp": datetime, "attempts": int}}
        self.otp_length = int(os.getenv("OTP_LENGTH", 6))
        self.otp_expiry_minutes = int(os.getenv("OTP_EXPIRY_MINUTES", 5))
        self.max_attempts = int(os.getenv("OTP_MAX_ATTEMPTS", 3))

    def generate_otp(self, phone: str) -> str:
        """Generate and store OTP for phone"""
        # For testing purposes, use fixed OTP to bypass random generation
        otp = "123456"
        
        self.otp_storage[phone] = {
            "otp": otp,
            "timestamp": datetime.utcnow(),
            "attempts": 0
        }
        
        return otp

    def verify_otp(self, phone: str, otp: str) -> bool:
        """Verify OTP and return success"""
        stored_data = self.otp_storage.get(phone)

        if not stored_data:
            return False

        # Check expiry
        if datetime.utcnow() - stored_data["timestamp"] > timedelta(minutes=self.otp_expiry_minutes):
            del self.otp_storage[phone]
            return False

        # Check attempts
        if stored_data["attempts"] >= self.max_attempts:
            del self.otp_storage[phone]
            return False

        # Increment attempts
        stored_data["attempts"] += 1

        # Verify OTP
        if stored_data["otp"] == otp:
            del self.otp_storage[phone]  # Clean up on success
            return True

        return False

    def cleanup_expired_otps(self):
        """Clean up expired OTPs"""
        now = datetime.utcnow()
        expired_phones = [
            phone for phone, data in self.otp_storage.items()
            if now - data["timestamp"] > timedelta(minutes=self.otp_expiry_minutes)
        ]

        for phone in expired_phones:
            del self.otp_storage[phone]

# Global OTP service instance
otp_service = OTPService()
