"""
Railway-optimized LangGraph Service - Robust Version
Handles startup gracefully with proper error handling.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import asyncio
from typing import Dict, Any

# Create FastAPI app immediately
app = FastAPI(title="LangGraph Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
service_state = {
    "modules_loaded": False,
    "loading_error": None,
    "groq_available": False,
    "database_ready": False
}

@app.get("/")
async def root():
    """Root endpoint with service status."""
    return {
        "message": "LangGraph Service - Railway Robust",
        "status": "running",
        "service_state": service_state,
        "port": os.getenv("PORT", "8001"),
        "backend_url": os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
    }

@app.get("/health")
async def health():
    """Health check - always returns healthy for Railway."""
    return {
        "status": "healthy", 
        "service": "langgraph_service",
        "modules_loaded": service_state["modules_loaded"]
    }

@app.get("/status")
async def get_status():
    """Get detailed service status."""
    return {
        "service_state": service_state,
        "environment": {
            "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
            "backend_url": os.getenv("BACKEND_SERVICE_URL", "Not set"),
            "port": os.getenv("PORT", "8001")
        }
    }

# Initialize modules on startup
@app.on_event("startup")
async def startup_event():
    """Initialize LangGraph modules on startup."""
    global service_state
    
    print("🚀 Starting LangGraph service initialization...")
    
    try:
        # Test environment variables
        groq_key = os.getenv("GROQ_API_KEY")
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        
        print(f"🔑 Groq API Key: {'Set' if groq_key else 'Missing'}")
        print(f"🔗 Backend URL: {backend_url}")
        
        # Test Groq API if available
        if groq_key:
            try:
                from langgraph_agent.groq_client import groq_client
                test_response = groq_client.generate_response(
                    "You are a test assistant.", 
                    "Say 'OK'", 
                    max_tokens=5
                )
                service_state["groq_available"] = bool(test_response and "OK" in test_response)
                print(f"✅ Groq API: {'Available' if service_state['groq_available'] else 'Limited'}")
            except Exception as e:
                print(f"⚠️  Groq API warning: {str(e)}")
        
        # Test database connection
        try:
            from langgraph_agent.user_summary_service import user_summary_service
            user_summary_service.create_user_summaries_table()
            service_state["database_ready"] = True
            print("✅ Database: Ready")
        except Exception as e:
            print(f"⚠️  Database warning: {str(e)}")
        
        # Load LangGraph router
        try:
            from langgraph_agent.api import router as langgraph_router
            app.include_router(langgraph_router)
            service_state["modules_loaded"] = True
            print("✅ LangGraph modules: Loaded")
        except Exception as e:
            service_state["loading_error"] = str(e)
            print(f"❌ LangGraph modules failed: {str(e)}")
        
        print("🎯 Service initialization complete!")
        
    except Exception as e:
        service_state["loading_error"] = str(e)
        print(f"❌ Startup error: {str(e)}")

# Fallback endpoints for when modules aren't loaded
@app.post("/ai-agents/langgraph/start-quiz")
async def start_quiz_fallback():
    """Fallback quiz endpoint with proper error handling."""
    if not service_state["modules_loaded"]:
        return {
            "success": False,
            "message": "LangGraph modules not loaded",
            "error": service_state.get("loading_error", "Unknown error"),
            "service_state": service_state
        }
    
    # If we get here, modules should be loaded and the actual endpoint will handle it
    raise HTTPException(status_code=500, detail="This shouldn't happen - modules loaded but endpoint not found")

@app.get("/ai-agents/langgraph/health")
async def langgraph_health_fallback():
    """Fallback LangGraph health check."""
    if not service_state["modules_loaded"]:
        return {
            "success": False,
            "message": "LangGraph modules not loaded",
            "service_state": service_state
        }
    
    return {
        "success": True,
        "message": "LangGraph agent is healthy",
        "service_state": service_state
    }

@app.get("/ai-agents/langgraph/info")
async def langgraph_info_fallback():
    """Fallback LangGraph info endpoint."""
    return {
        "success": True,
        "message": "LangGraph Quiz Agent Information",
        "data": {
            "agent_type": "LangGraph Adaptive Quiz Agent",
            "model": "Qwen 3-32B (via Groq)",
            "status": "loaded" if service_state["modules_loaded"] else "not loaded",
            "service_state": service_state
        }
    }

# Test endpoint
@app.post("/test")
async def test_service():
    """Test endpoint to verify service functionality."""
    try:
        # Test backend connection
        import requests
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        
        try:
            response = requests.get(f"{backend_url}/health", timeout=10)
            backend_status = "connected" if response.status_code == 200 else f"error_{response.status_code}"
        except:
            backend_status = "unreachable"
        
        return {
            "success": True,
            "message": "Service test completed",
            "results": {
                "backend_communication": backend_status,
                "service_state": service_state,
                "environment": {
                    "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
                    "backend_url": backend_url
                }
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Test failed: {str(e)}",
            "service_state": service_state
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Starting Robust LangGraph Service on port {port}")
    uvicorn.run(
        "main_railway_robust:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
