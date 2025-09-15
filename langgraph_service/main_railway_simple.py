"""
Railway-optimized LangGraph Service - Ultra Simple Version
Minimal startup with graceful degradation for Railway deployment.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Create FastAPI app with minimal configuration
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

# Global state
service_status = {
    "modules_loaded": False,
    "database_ready": False,
    "groq_available": False,
    "startup_errors": []
}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LangGraph Service - Railway Simple",
        "status": "running",
        "service_status": service_status,
        "port": os.getenv("PORT", "8001"),
        "backend_url": os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
    }

@app.get("/health")
async def health():
    """Health check endpoint - always returns healthy for Railway."""
    return {
        "status": "healthy",
        "service": "langgraph_service",
        "environment": "railway",
        "port": os.getenv("PORT", "8001"),
        "service_status": service_status
    }

@app.get("/debug")
async def debug_info():
    """Debug information endpoint."""
    return {
        "environment_variables": {
            "PORT": os.getenv("PORT", "Not set"),
            "GROQ_API_KEY": "Set" if os.getenv("GROQ_API_KEY") else "Not set",
            "BACKEND_SERVICE_URL": os.getenv("BACKEND_SERVICE_URL", "Not set")
        },
        "service_status": service_status,
        "working_directory": os.getcwd()
    }

# Lazy loading endpoint to test modules
@app.post("/initialize")
async def initialize_modules():
    """Initialize LangGraph modules on demand."""
    global service_status
    
    try:
        # Test Groq API
        try:
            if os.getenv("GROQ_API_KEY"):
                from langgraph_agent.groq_client import groq_client
                test_response = groq_client.generate_response(
                    "You are a test assistant.", 
                    "Say 'OK'", 
                    max_tokens=5
                )
                service_status["groq_available"] = bool(test_response and "OK" in test_response)
            else:
                service_status["startup_errors"].append("GROQ_API_KEY not set")
        except Exception as e:
            service_status["startup_errors"].append(f"Groq error: {str(e)}")
        
        # Test database
        try:
            from langgraph_agent.user_summary_service import user_summary_service
            user_summary_service.create_user_summaries_table()
            service_status["database_ready"] = True
        except Exception as e:
            service_status["startup_errors"].append(f"Database error: {str(e)}")
        
        # Load main modules
        try:
            from langgraph_agent.api import router as langgraph_router
            app.include_router(langgraph_router)
            service_status["modules_loaded"] = True
        except Exception as e:
            service_status["startup_errors"].append(f"Module loading error: {str(e)}")
        
        return {
            "success": True,
            "message": "Initialization attempted",
            "service_status": service_status
        }
        
    except Exception as e:
        service_status["startup_errors"].append(f"General error: {str(e)}")
        return {
            "success": False,
            "message": f"Initialization failed: {str(e)}",
            "service_status": service_status
        }

# Simple test endpoint
@app.post("/ai-agents/langgraph/test")
async def test_langgraph():
    """Simple test endpoint."""
    try:
        # Test backend communication
        import requests
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        
        try:
            response = requests.get(f"{backend_url}/health", timeout=10)
            backend_status = "connected" if response.status_code == 200 else f"error_{response.status_code}"
        except:
            backend_status = "unreachable"
        
        return {
            "success": True,
            "message": "LangGraph service test successful",
            "backend_communication": backend_status,
            "backend_url": backend_url,
            "service_status": service_status
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Test failed: {str(e)}",
            "service_status": service_status
        }

# Fallback quiz endpoint
@app.post("/ai-agents/langgraph/start-quiz")
async def start_quiz_simple():
    """Simplified start-quiz endpoint."""
    if not service_status["modules_loaded"]:
        return {
            "success": False,
            "message": "LangGraph modules not loaded. Call /initialize first.",
            "service_status": service_status
        }
    
    try:
        # Try to run actual quiz if modules are loaded
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
            "message": f"Quiz execution failed: {str(e)}",
            "service_status": service_status
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Starting Simple LangGraph Service on port {port}")
    uvicorn.run(
        "main_railway_simple:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
