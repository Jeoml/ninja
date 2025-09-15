"""
Debug version for Railway deployment troubleshooting.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Create minimal FastAPI app
app = FastAPI(
    title="LangGraph Service Debug",
    description="Debug version for Railway troubleshooting",
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

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LangGraph Service Debug",
        "status": "running",
        "port": os.getenv("PORT", "8001"),
        "backend_url": os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
    }

@app.get("/health")
async def health():
    """Simple health check."""
    return {"status": "healthy", "service": "langgraph_debug"}

@app.get("/test-imports")
async def test_imports():
    """Test all imports to identify issues."""
    results = {}
    
    # Test basic imports
    try:
        import requests
        results["requests"] = "OK"
    except Exception as e:
        results["requests"] = f"Error: {str(e)}"
    
    try:
        import psycopg2
        results["psycopg2"] = "OK"
    except Exception as e:
        results["psycopg2"] = f"Error: {str(e)}"
    
    try:
        from langgraph_agent.tools import get_all_topics
        results["langgraph_tools"] = "OK"
    except Exception as e:
        results["langgraph_tools"] = f"Error: {str(e)}"
    
    try:
        from langgraph_agent.groq_client import groq_client
        results["groq_client"] = "OK"
    except Exception as e:
        results["groq_client"] = f"Error: {str(e)}"
    
    try:
        from langgraph_agent.quiz_agent import quiz_agent
        results["quiz_agent"] = "OK"
    except Exception as e:
        results["quiz_agent"] = f"Error: {str(e)}"
    
    try:
        from langgraph_agent.api import router
        results["langgraph_api"] = "OK"
    except Exception as e:
        results["langgraph_api"] = f"Error: {str(e)}"
    
    return {
        "message": "Import test results",
        "imports": results,
        "environment": {
            "PORT": os.getenv("PORT", "Not set"),
            "GROQ_API_KEY": "Set" if os.getenv("GROQ_API_KEY") else "Not set",
            "BACKEND_SERVICE_URL": os.getenv("BACKEND_SERVICE_URL", "Not set")
        }
    }

@app.get("/test-backend")
async def test_backend():
    """Test backend service connectivity."""
    try:
        import requests
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        
        # Test health endpoint
        response = requests.get(f"{backend_url}/health", timeout=10)
        
        if response.status_code == 200:
            backend_data = response.json()
            return {
                "backend_status": "connected",
                "backend_response": backend_data,
                "backend_url": backend_url
            }
        else:
            return {
                "backend_status": f"error_{response.status_code}",
                "backend_url": backend_url
            }
    except Exception as e:
        return {
            "backend_status": "failed",
            "error": str(e),
            "backend_url": os.getenv("BACKEND_SERVICE_URL", "Not set")
        }

@app.post("/ai-agents/langgraph/start-quiz")
async def start_quiz_debug():
    """Debug version of start-quiz endpoint."""
    try:
        # Test if we can import the quiz agent
        from langgraph_agent.quiz_agent import quiz_agent
        
        return {
            "success": False,
            "message": "Debug mode - quiz agent import successful but not running full assessment",
            "debug_info": {
                "quiz_agent_imported": True,
                "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
                "backend_url": os.getenv("BACKEND_SERVICE_URL")
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Quiz agent import failed: {str(e)}",
            "debug_info": {
                "quiz_agent_imported": False,
                "error": str(e)
            }
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Starting Debug LangGraph Service on port {port}")
    uvicorn.run(
        "main_debug:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="debug"
    )
