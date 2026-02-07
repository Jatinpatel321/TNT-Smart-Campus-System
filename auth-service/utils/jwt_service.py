import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

class JWTService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "TNT_SUPER_SECRET_KEY")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 10))

    def create_access_token(self, phone: str, role: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "sub": phone,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "tnt-auth-service"
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                credentials.credentials,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            phone = payload.get("sub")
            if not phone:
                raise HTTPException(status_code=401, detail="Invalid token: missing subject")

            return payload

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired token: {str(e)}"
            )

    def get_phone_from_token(self, credentials: HTTPAuthorizationCredentials) -> str:
        """Extract phone from JWT token"""
        payload = self.verify_token(credentials)
        return payload.get("sub")

# Global JWT service instance
jwt_service = JWTService()
