# ---------------- IMPORTS ----------------
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel, validator
import random
import httpx

from database import get_db, engine
from models import User
from utils.response import success_response, error_response
from utils.jwt_service import jwt_service
from utils.otp_service import otp_service
from utils.audit_logger import audit_logger


# ---------------- APP INIT ----------------
app = FastAPI(title="TNT Auth Service")

User.metadata.create_all(bind=engine)

# ---------------- SECURITY SERVICES ----------------
security = HTTPBearer()


# ---------------- TOKEN VERIFICATION ----------------
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return jwt_service.get_phone_from_token(credentials)


# ---------------- ROLE BASED ACCESS ----------------
def require_role(required_role: str):
    def role_checker(payload=Depends(verify_jwt)):
        if payload.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Access Forbidden")

        return payload

    return role_checker


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return jwt_service.verify_token(credentials)


# ---------------- ROOT ROUTES ----------------
@app.get("/")
def home():
    return success_response("TNT Auth Service Running 🚀")


@app.get("/health")
def health():
    return success_response("Auth Service is healthy ✅")


# ---------------- REQUEST MODELS ----------------
class LoginRequest(BaseModel):
    phone: str

    @validator('phone')
    def validate_phone(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('Phone number must be exactly 10 digits')
        return v


class VerifyOTPRequest(BaseModel):
    phone: str
    otp: str


class AssignRoleRequest(BaseModel):
    phone: str
    role: str


# ---------------- LOGIN (SEND OTP) OTP generation----------------
@app.post("/login")
def login_user(data: LoginRequest):

    # Generate secure OTP using service
    otp = otp_service.generate_otp(data.phone)

    # Log audit event (non-blocking)
    try:
        audit_logger.log_otp_generation(data.phone)
    except Exception as e:
        print(f"Audit logging failed: {e}")

    print(f"OTP for {data.phone} is {otp}")

    return success_response(
        "OTP sent successfully",
        {"phone": data.phone}
    )


# ---------------- VERIFY OTP + USER REGISTER ----------------
@app.post("/verify-otp")
async def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):

    # Verify OTP using service
    if not otp_service.verify_otp(data.phone, data.otp):
        audit_logger.log_login_attempt(data.phone, success=False)
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.phone == data.phone).first()

    if not user:
        # Determine role by checking vendor existence
        is_vendor = await check_vendor_exists(data.phone)
        role = "vendor" if is_vendor else "student"

        user = User(phone=data.phone, role=role)
        db.add(user)
        db.commit()
    else:
        # Update role if user exists but role might be outdated
        is_vendor = await check_vendor_exists(data.phone)
        new_role = "vendor" if is_vendor else "student"
        if user.role != new_role:
            user.role = new_role
            db.commit()

    db.refresh(user)

    # Create JWT token
    token = jwt_service.create_access_token(user.phone, user.role)

    # Log successful login
    audit_logger.log_login_attempt(user.phone, success=True)

    return success_response(
        "Login Successful ✅",
        {
            "access_token": token,
            "token_type": "bearer",
            "phone": user.phone,
            "role": user.role
        }
    )


# ---------------- CURRENT USER ----------------
@app.get("/me")
def get_current_user(
    phone: str = Depends(verify_token),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        return error_response("User not found")

    return success_response(
        "User fetched successfully",
        {
            "id": user.id,
            "phone": user.phone,
            "role": user.role
        }
    )


# ---------------- VENDOR ROUTE ----------------
@app.get("/vendor/dashboard")
def vendor_dashboard(payload = Depends(require_role("vendor"))):

    return success_response(
        "Vendor dashboard access granted",
        {
            "phone": payload["sub"],
            "role": payload["role"]
        }
    )


# ---------------- ADMIN: GET ALL USERS ----------------
@app.get("/admin/users")
def get_all_users(
    payload = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):

    users = db.query(User).all()

    return success_response(
        "Users fetched successfully",
        [
            {
                "id": u.id,
                "phone": u.phone,
                "role": u.role
            }
            for u in users
        ]
    )


# ---------------- HELPER FUNCTIONS ----------------
async def check_vendor_exists(phone: str) -> bool:
    """Check if phone exists as vendor in vendor-service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8001/vendors/phone/{phone}")
            return response.status_code == 200
    except:
        # If vendor-service is down, assume not vendor
        return False


# ---------------- ADMIN: ASSIGN ROLE ----------------
@app.post("/admin/assign-role")
def assign_role(
    request: AssignRoleRequest,
    admin_payload = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):

    target_user = db.query(User).filter(User.phone == request.phone).first()

    if not target_user:
        return error_response("User not found")

    old_role = target_user.role
    target_user.role = request.role
    db.commit()
    db.refresh(target_user)

    # Log role change
    audit_logger.log_role_change(admin_payload["sub"], request.phone, old_role, request.role)

    return success_response(
        "Role updated successfully",
        {
            "phone": target_user.phone,
            "role": target_user.role
        }
    )
