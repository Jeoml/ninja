"""
Minimal test version to debug Railway deployment issues.
"""
from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(title="Backend Service Test")

@app.get("/")
async def root():
    return {"message": "Backend Service Test", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "backend_test"}

@app.get("/test-imports")
async def test_imports():
    try:
        # Test basic imports
        from auth.config import APP_NAME
        auth_status = "OK"
    except Exception as e:
        auth_status = f"Error: {str(e)}"
    
    try:
        from agent_helper.tools import router
        helper_status = "OK"
    except Exception as e:
        helper_status = f"Error: {str(e)}"
    
    try:
        from ai_agents.brute.round1.api import router
        round1_status = "OK"
    except Exception as e:
        round1_status = f"Error: {str(e)}"
    
    return {
        "auth_import": auth_status,
        "agent_helper_import": helper_status,
        "round1_import": round1_status
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "test_minimal:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
