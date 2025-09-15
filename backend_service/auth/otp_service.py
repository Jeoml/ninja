"""
OTP generation and verification service.
"""
import random
import string
from datetime import datetime, timedelta
from .database import OTPDB, UserDB
from .email_service import email_service
from .config import OTP_EXPIRE_MINUTES, OTP_LENGTH

class OTPService:
    """Service for OTP generation and verification."""
    
    @staticmethod
    def generate_otp() -> str:
        """Generate a random OTP code."""
        return ''.join(random.choices(string.digits, k=OTP_LENGTH))
    
    @staticmethod
    def send_otp(email: str) -> dict:
        """Send OTP to email address."""
        try:
            # Generate OTP
            otp_code = OTPService.generate_otp()
            
            # Calculate expiry time
            expires_at = datetime.now() + timedelta(minutes=OTP_EXPIRE_MINUTES)
            
            # Save OTP to database
            OTPDB.create_otp(email, otp_code, expires_at)
            
            # Create or get user
            UserDB.create_user(email)
            
            # Send email
            email_sent = email_service.send_otp_email(email, otp_code)
            
            if email_sent:
                return {
                    "success": True,
                    "message": f"OTP sent successfully to {email}",
                    "expires_in_minutes": OTP_EXPIRE_MINUTES
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to send OTP email. Please check your email configuration."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending OTP: {str(e)}"
            }
    
    @staticmethod
    def verify_otp(email: str, otp_code: str) -> dict:
        """Verify OTP code."""
        try:
            # Verify OTP in database
            is_valid = OTPDB.verify_otp(email, otp_code)
            
            if is_valid:
                # Mark user as verified
                UserDB.verify_user(email)
                
                return {
                    "success": True,
                    "message": "OTP verified successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid or expired OTP code"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error verifying OTP: {str(e)}"
            }
