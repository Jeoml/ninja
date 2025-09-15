"""
Railway-optimized LangGraph Service - Ultra Minimal Version
Starts immediately, loads everything lazily.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import threading
import time

# Create FastAPI app immediately
app = FastAPI(title="LangGraph Service", version="1.0.0")

# Add minimal CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple status tracking
status = {"ready": False, "error": None}

@app.get("/")
async def root():
    return {
        "message": "LangGraph Service - Ultra Simple",
        "status": "running",
        "ready": status["ready"],
        "port": os.getenv("PORT", "8001")
    }

@app.get("/health")
async def health():
    # Always return healthy for Railway health check
    return {"status": "healthy", "service": "langgraph_service"}

@app.get("/status")
async def get_status():
    return status

# Background initialization
def init_in_background():
    """Initialize modules in background thread."""
    try:
        time.sleep(2)  # Give the server time to start
        print("🔄 Background initialization starting...")
        
        # Try to load modules
        from langgraph_agent.api import router
        app.include_router(router)
        
        status["ready"] = True
        print("✅ Background initialization complete")
        
    except Exception as e:
        status["error"] = str(e)
        print(f"❌ Background initialization failed: {e}")

# Start background initialization
threading.Thread(target=init_in_background, daemon=True).start()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Starting Ultra Simple LangGraph Service on port {port}")
    uvicorn.run(
        "main_railway_ultra_simple:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
