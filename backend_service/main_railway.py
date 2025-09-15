"""
Railway-optimized Backend Service
Simplified startup for faster Railway deployment.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Create FastAPI app with minimal startup
app = FastAPI(
    title="Backend Service",
    description="Authentication and Agent Helper APIs for Quiz System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for development
        "https://ninja-frontend-production.up.railway.app",
        "https://ninja-production-8034.up.railway.app",  # LangGraph service
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Backend Service - Railway Deployment",
        "version": "1.0.0",
        "status": "running",
        "port": os.getenv("PORT", "8000")
    }

@app.get("/health")
async def health_check():
    """Railway health check endpoint."""
    return {
        "status": "healthy",
        "service": "backend_service",
        "environment": "railway",
        "port": os.getenv("PORT", "8000")
    }

# Lazy import endpoints to avoid startup delays
@app.on_event("startup")
async def startup_event():
    """Lazy startup - import modules after service starts."""
    try:
        print("🚀 Backend Service starting on Railway...")
        
        # Import and register routers after startup
        from agent_helper.tools import router as agent_helper_router
        app.include_router(agent_helper_router)
        print("✅ Agent Helper APIs loaded")
        
        from ai_agents.brute.round1.api import router as round1_router
        from ai_agents.brute.round2.api import router as round2_router
        app.include_router(round1_router)
        app.include_router(round2_router)
        print("✅ Quiz APIs loaded")
        
        # Create database tables (non-blocking)
        try:
            from auth.database import create_auth_tables
            create_auth_tables()
            from agent_helper.response_service import ResponseService
            ResponseService.create_responses_table()
            print("✅ Database tables ready")
        except Exception as e:
            print(f"⚠️  Database setup deferred: {str(e)}")
        
        print("✅ Backend Service ready on Railway!")
        
    except Exception as e:
        print(f"❌ Startup error: {str(e)}")

# Simple auth endpoints (inline to avoid import issues)
@app.post("/auth/send-otp")
async def send_otp_simple():
    """Simplified OTP endpoint for Railway testing."""
    return {
        "success": True,
        "message": "OTP service available",
        "note": "Full auth implementation loaded after startup"
    }

@app.get("/agent-helper/topics")
async def get_topics_simple():
    """Simplified topics endpoint for Railway testing."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        connection.autocommit = True
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT topic FROM quiz_questions ORDER BY topic")
            topics = [row['topic'] for row in cursor.fetchall()]
        
        connection.close()
        
        return {
            "success": True,
            "message": f"Found {len(topics)} topics",
            "data": {
                "topics": topics,
                "total_count": len(topics)
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Database error: {str(e)}"
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting Backend Service on port {port}")
    uvicorn.run(
        "main_railway:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
