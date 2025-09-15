"""
Authentication module for Quiz Auth System.
Provides email OTP verification and JWT token authentication.
"""

__version__ = "1.0.0"
__author__ = "Quiz Auth System"

# Import main components for easier access
from .otp_service import OTPService
from .jwt_service import JWTService
from .email_service import email_service
from .database import UserDB, OTPDB, create_auth_tables

__all__ = [
    "OTPService",
    "JWTService", 
    "email_service",
    "UserDB",
    "OTPDB",
    "create_auth_tables"
]
