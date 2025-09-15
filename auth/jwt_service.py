"""
JWT token service for authentication.
"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from .config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_MINUTES
from .database import UserDB

class JWTService:
    """Service for JWT token operations."""
    
    @staticmethod
    def create_access_token(email: str) -> str:
        """Create JWT access token for user."""
        # Get user data
        user = UserDB.get_user_by_email(email)
        if not user:
            raise ValueError("User not found")
        
        # Create token payload
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": email,  # Subject (user identifier)
            "user_id": user["id"],
            "email": email,
            "is_verified": user["is_verified"],
            "exp": expire,  # Expiration time
            "iat": datetime.utcnow(),  # Issued at
            "type": "access"
        }
        
        # Generate token
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            # Decode token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Extract user email
            email = payload.get("sub")
            if email is None:
                raise JWTError("Invalid token payload")
            
            # Verify user still exists and is active
            user = UserDB.get_user_by_email(email)
            if not user or not user.get("is_active", True):
                raise JWTError("User not found or inactive")
            
            return {
                "valid": True,
                "payload": payload,
                "user": user
            }
            
        except JWTError as e:
            return {
                "valid": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Token verification error: {str(e)}"
            }
    
    @staticmethod
    def decode_token_without_verification(token: str) -> dict:
        """Decode token without verification (for debugging)."""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_token_expiry_info(token: str) -> dict:
        """Get token expiry information."""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get("exp")
            
            if exp:
                expiry_time = datetime.fromtimestamp(exp)
                current_time = datetime.utcnow()
                time_remaining = expiry_time - current_time
                
                return {
                    "expires_at": expiry_time.isoformat(),
                    "expired": current_time > expiry_time,
                    "time_remaining_seconds": max(0, int(time_remaining.total_seconds()))
                }
            
            return {"error": "No expiry information in token"}
            
        except Exception as e:
            return {"error": str(e)}
