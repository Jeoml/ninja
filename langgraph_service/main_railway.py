"""
Railway-optimized LangGraph Service
Simplified startup for faster Railway deployment.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    try:
        print("🚀 LangGraph Service starting on Railway...")
        
        # Test backend service connection
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        print(f"🔗 Backend service URL: {backend_url}")
        
        # Test Groq API connection
        try:
            from langgraph_agent.groq_client import groq_client
            test_response = groq_client.generate_response(
                "You are a test assistant.", 
                "Say 'OK' if you can hear me.", 
                max_tokens=5
            )
            if test_response and "OK" in test_response:
                print("✅ Groq API connection successful")
            else:
                print("⚠️  Groq API connection warning")
        except Exception as e:
            print(f"⚠️  Groq API warning: {str(e)}")
        
        # Import and register LangGraph router after startup
        from langgraph_agent.api import router as langgraph_router
        app.include_router(langgraph_router)
        print("✅ LangGraph Agent APIs loaded")
        
        # Create database tables (non-blocking)
        try:
            from langgraph_agent.user_summary_service import user_summary_service
            user_summary_service.create_user_summaries_table()
            print("✅ User summary tables ready")
        except Exception as e:
            print(f"⚠️  Database setup deferred: {str(e)}")
        
        print("✅ LangGraph Service ready on Railway!")
        
    except Exception as e:
        print(f"❌ Startup error: {str(e)}")
    
    yield  # This is crucial - the service runs here
    
    # Shutdown
    print("👋 Shutting down LangGraph Service...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="LangGraph Service",
    description="AI-Powered Adaptive Quiz Agent",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins for development
        "https://ninja-frontend-production.up.railway.app",
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
    backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
    return {
        "message": "LangGraph Service - Railway Deployment",
        "version": "1.0.0",
        "status": "running",
        "backend_service_url": backend_url,
        "port": os.getenv("PORT", "8001")
    }

@app.get("/health")
async def health_check():
    """Railway health check endpoint."""
    try:
        # Test backend connection
        import requests
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        backend_health = "unknown"
        
        try:
            response = requests.get(f"{backend_url}/health", timeout=5)
            backend_health = "connected" if response.status_code == 200 else f"error_{response.status_code}"
        except:
            backend_health = "unreachable"
        
        return {
            "status": "healthy",
            "service": "langgraph_service",
            "environment": "railway",
            "port": os.getenv("PORT", "8001"),
            "backend_status": backend_health,
            "backend_url": backend_url
        }
    except Exception as e:
        return {
            "status": "degraded",
            "service": "langgraph_service",
            "error": str(e)
        }



# Simple test endpoint for Railway
@app.post("/ai-agents/langgraph/test")
async def test_langgraph():
    """Simple test endpoint for Railway verification."""
    try:
        # Test backend communication
        import requests
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        
        response = requests.get(f"{backend_url}/health", timeout=10)
        backend_status = "connected" if response.status_code == 200 else f"error_{response.status_code}"
        
        return {
            "success": True,
            "message": "LangGraph service test successful",
            "backend_communication": backend_status,
            "backend_url": backend_url
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Test failed: {str(e)}"
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Starting LangGraph Service on port {port}")
    uvicorn.run(
        "main_railway:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
