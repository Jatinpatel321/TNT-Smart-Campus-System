from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt

SECRET_KEY = "TNT_SUPER_SECRET_KEY"  # SAME as auth-service
ALGORITHM = "HS256"

security = HTTPBearer()

def verify_vendor_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        role = payload.get("role")
        phone = payload.get("sub")

        if role != "vendor":
            raise HTTPException(status_code=403, detail="Vendor access required")

        return {
            "phone": phone,
            "role": role
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
