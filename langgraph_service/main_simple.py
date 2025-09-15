"""
Ultra-simple Railway service to test basic functionality.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="LangGraph Simple")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "LangGraph Service Simple",
        "status": "running",
        "port": os.getenv("PORT", "unknown")
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/ai-agents/langgraph/start-quiz")
def start_quiz():
    return {
        "success": False,
        "message": "Simple mode - full agent not loaded",
        "debug": {
            "port": os.getenv("PORT", "unknown"),
            "groq_key": "set" if os.getenv("GROQ_API_KEY") else "missing"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"Starting simple service on port {port}")
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=port
    )
