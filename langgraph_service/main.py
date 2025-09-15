"""
LangGraph Service - AI-Powered Adaptive Quiz Agent
Handles intelligent quiz assessments with question generation.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

# Import LangGraph Agent
from langgraph_agent.api import router as langgraph_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print(f"🚀 Starting LangGraph Service...")
    
    # Create database tables for user summaries
    from langgraph_agent.user_summary_service import user_summary_service
    user_summary_service.create_user_summaries_table()
    
    # Test Groq API connection
    try:
        from langgraph_agent.groq_client import groq_client
        test_response = groq_client.generate_response(
            "You are a test assistant.", 
            "Say 'Hello' if you can hear me.", 
            max_tokens=10
        )
        if test_response:
            print("✅ Groq API connection successful")
        else:
            print("⚠️  Warning: Groq API connection failed")
    except Exception as e:
        print(f"⚠️  Warning: Groq API test failed: {str(e)}")
    
    print("✅ LangGraph Service startup complete!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down LangGraph Service...")

# Create FastAPI app
app = FastAPI(
    title="LangGraph Service",
    description="AI-Powered Adaptive Quiz Agent with Question Generation",
    version="1.0.0",
    lifespan=lifespan
)

# Include LangGraph router
app.include_router(langgraph_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your backend service URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LangGraph Service - AI-Powered Adaptive Quiz Agent",
        "version": "1.0.0",
        "services": {
            "langgraph_agent": {
                "start_quiz": "POST /ai-agents/langgraph/start-quiz",
                "user_summary": "GET /ai-agents/langgraph/user-summary/{session_id}",
                "health": "GET /ai-agents/langgraph/health",
                "info": "GET /ai-agents/langgraph/info"
            },
            "utility": {
                "health": "GET /health",
                "docs": "GET /docs"
            }
        },
        "features": [
            "6-node adaptive workflow",
            "AI-powered question generation", 
            "Comprehensive user profiling",
            "Self-improving questionnaire",
            "Groq API integration",
            "Performance analytics"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "langgraph_service",
        "timestamp": "2024-01-01T00:00:00Z",
        "ai_model": "Qwen 3-32B (via Groq)",
        "nodes": 6
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))  # Use PORT env var for Railway, default to 8001
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload for production
        log_level="info"
    )
