"""
Railway-optimized LangGraph Service - Fixed Version
Handles startup errors gracefully to prevent service crashes.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Create FastAPI app without lifespan first
app = FastAPI(
    title="LangGraph Service",
    description="AI-Powered Adaptive Quiz Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to track if modules are loaded
modules_loaded = False
langgraph_router = None

@app.on_event("startup")
async def startup_event():
    """Load modules after FastAPI starts."""
    global modules_loaded, langgraph_router
    
    print("🚀 LangGraph Service starting on Railway...")
    
    try:
        # Test environment variables
        groq_key = os.getenv("GROQ_API_KEY", "")
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        
        print(f"🔗 Backend URL: {backend_url}")
        print(f"🔑 Groq API Key: {'Set' if groq_key else 'Missing'}")
        
        # Try to import and register LangGraph router
        from langgraph_agent.api import router as lg_router
        app.include_router(lg_router)
        langgraph_router = lg_router
        modules_loaded = True
        print("✅ LangGraph Agent APIs loaded successfully")
        
        # Test database connection
        try:
            from langgraph_agent.user_summary_service import user_summary_service
            user_summary_service.create_user_summaries_table()
            print("✅ Database tables ready")
        except Exception as e:
            print(f"⚠️  Database setup warning: {str(e)}")
        
        print("✅ LangGraph Service ready!")
        
    except Exception as e:
        print(f"❌ Module loading error: {str(e)}")
        print("Service will run in limited mode")
        modules_loaded = False

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LangGraph Service - Railway",
        "status": "running",
        "modules_loaded": modules_loaded,
        "port": os.getenv("PORT", "8001"),
        "backend_url": os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        # Test backend connectivity
        import requests
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        
        try:
            response = requests.get(f"{backend_url}/health", timeout=5)
            backend_status = "connected" if response.status_code == 200 else f"error_{response.status_code}"
        except:
            backend_status = "unreachable"
        
        return {
            "status": "healthy",
            "service": "langgraph_service",
            "modules_loaded": modules_loaded,
            "backend_status": backend_status,
            "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
            "port": os.getenv("PORT", "8001")
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }

@app.get("/debug")
async def debug_info():
    """Debug information endpoint."""
    try:
        import sys
        return {
            "python_version": sys.version,
            "environment_variables": {
                "PORT": os.getenv("PORT", "Not set"),
                "GROQ_API_KEY": "Set" if os.getenv("GROQ_API_KEY") else "Not set",
                "BACKEND_SERVICE_URL": os.getenv("BACKEND_SERVICE_URL", "Not set")
            },
            "modules_loaded": modules_loaded,
            "working_directory": os.getcwd(),
            "python_path": sys.path[:3]  # First 3 entries
        }
    except Exception as e:
        return {"error": str(e)}

# Fallback endpoint if main LangGraph fails
@app.post("/ai-agents/langgraph/start-quiz")
async def start_quiz_fallback():
    """Fallback start-quiz endpoint."""
    if not modules_loaded:
        return {
            "success": False,
            "message": "LangGraph modules not loaded - service in limited mode",
            "debug": {
                "modules_loaded": modules_loaded,
                "groq_key_set": bool(os.getenv("GROQ_API_KEY")),
                "backend_url": os.getenv("BACKEND_SERVICE_URL")
            }
        }
    
    try:
        # If modules are loaded, try to run the actual quiz
        from langgraph_agent.quiz_agent import quiz_agent
        result = quiz_agent.run_quiz(user_id="railway_test")
        return {
            "success": True,
            "message": "Quiz completed successfully!",
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Quiz execution failed: {str(e)}"
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Starting Fixed LangGraph Service on port {port}")
    uvicorn.run(
        "main_railway_fixed:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
