"""
FastAPI application for authentication system.
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from auth.models import EmailRequest, OTPVerificationRequest, AuthResponse, TokenResponse
from auth.database import create_auth_tables, UserDB
from auth.otp_service import OTPService
from auth.jwt_service import JWTService
from auth.email_service import email_service
from auth.config import APP_NAME, DEBUG, JWT_ACCESS_TOKEN_EXPIRE_MINUTES

# Import AI Agents Round 1 and Round 2
from ai_agents.round1.api import router as round1_router
from ai_agents.round2.api import router as round2_router

# Security scheme
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting {APP_NAME}...")
    
    # Create database tables
    create_auth_tables()
    
    # Test email service connection
    if not email_service.test_connection():
        print("⚠️  Warning: Email service connection failed. Please check SMTP configuration.")
    
    print("✅ Application startup complete!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title=APP_NAME,
    description="Quiz system with authentication and AI-powered adaptive quizzes",
    version="1.0.0",
    lifespan=lifespan
)

# Include AI Agents routers
app.include_router(round1_router)
app.include_router(round2_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token."""
    token = credentials.credentials
    
    verification_result = JWTService.verify_token(token)
    
    if not verification_result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=verification_result["error"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return verification_result["user"]

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": "1.0.0",
        "services": {
            "authentication": {
                "send_otp": "POST /auth/send-otp",
                "verify_otp": "POST /auth/verify-otp", 
                "me": "GET /auth/me"
            },
            "ai_agents": {
                "round1": {
                    "intro": "GET /ai-agents/round1/chat/intro",
                    "start": "POST /ai-agents/round1/start",
                    "question": "GET /ai-agents/round1/question",
                    "answer": "POST /ai-agents/round1/answer",
                    "performance": "GET /ai-agents/round1/performance"
                },
                "round2": {
                    "start": "POST /ai-agents/round2/start",
                    "question": "GET /ai-agents/round2/question", 
                    "answer": "POST /ai-agents/round2/answer",
                    "performance": "GET /ai-agents/round2/performance",
                    "status": "GET /ai-agents/round2/status",
                    "topics": "GET /ai-agents/round2/topics"
                }
            },
            "utility": {
                "health": "GET /health",
                "docs": "GET /docs"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "service": APP_NAME
    }

@app.post("/auth/send-otp", response_model=AuthResponse)
async def send_otp(request: EmailRequest):
    """Send OTP to email address."""
    try:
        result = OTPService.send_otp(request.email)
        
        return AuthResponse(
            success=result["success"],
            message=result["message"],
            data={
                "email": request.email,
                "expires_in_minutes": result.get("expires_in_minutes")
            } if result["success"] else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send OTP: {str(e)}"
        )

@app.post("/auth/verify-otp", response_model=TokenResponse)
async def verify_otp(request: OTPVerificationRequest):
    """Verify OTP and return JWT token."""
    try:
        # Verify OTP
        verification_result = OTPService.verify_otp(request.email, request.otp_code)
        
        if not verification_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=verification_result["message"]
            )
        
        # Generate JWT token
        access_token = JWTService.create_access_token(request.email)
        
        # Update last login
        UserDB.update_last_login(request.email)
        
        # Get user info
        user = UserDB.get_user_by_email(request.email)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            user_info={
                "id": user["id"],
                "email": user["email"],
                "is_verified": user["is_verified"],
                "created_at": user["created_at"].isoformat() if user["created_at"] else None,
                "last_login": user["last_login"].isoformat() if user["last_login"] else None
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify OTP: {str(e)}"
        )

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return {
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "is_verified": current_user["is_verified"],
            "is_active": current_user["is_active"],
            "created_at": current_user["created_at"].isoformat() if current_user["created_at"] else None,
            "last_login": current_user["last_login"].isoformat() if current_user["last_login"] else None
        }
    }

@app.post("/auth/refresh-token")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token."""
    try:
        # Generate new token
        new_token = JWTService.create_access_token(current_user["email"])
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_info={
                "id": current_user["id"],
                "email": current_user["email"],
                "is_verified": current_user["is_verified"]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh token: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )
