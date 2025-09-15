"""
Pydantic models for API request/response validation.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class EmailRequest(BaseModel):
    """Request model for email input."""
    email: EmailStr

class OTPVerificationRequest(BaseModel):
    """Request model for OTP verification."""
    email: EmailStr
    otp_code: str

class AuthResponse(BaseModel):
    """Response model for authentication operations."""
    success: bool
    message: str
    data: Optional[dict] = None

class TokenResponse(BaseModel):
    """Response model for JWT token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict

class UserInfo(BaseModel):
    """User information model."""
    id: int
    email: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class TokenPayload(BaseModel):
    """JWT token payload model."""
    sub: str  # subject (email)
    user_id: int
    email: str
    is_verified: bool
    exp: datetime
    iat: datetime
    type: str
