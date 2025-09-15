"""
FastAPI routes for LangGraph Quiz Agent.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel

from .quiz_agent import quiz_agent

# Create router
router = APIRouter(prefix="/ai-agents/langgraph", tags=["LangGraph Quiz Agent"])

class StartQuizRequest(BaseModel):
    user_id: Optional[str] = None

class QuizResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/start-quiz", response_model=QuizResponse)
async def start_quiz(request: StartQuizRequest):
    """Start a new LangGraph quiz session."""
    try:
        print(f"🚀 Starting LangGraph quiz for user: {request.user_id}")
        
        # This would typically run in background, but for demo we'll run synchronously
        final_state = quiz_agent.run_quiz(user_id=request.user_id)
        
        return QuizResponse(
            success=True,
            message="Quiz completed successfully!",
            data={
                "session_id": final_state["session_id"],
                "questions_asked": final_state["questions_asked"],
                "topics_covered": final_state["topics_asked"],
                "performance_summary": final_state.get("performance_summary"),
                "user_summary": final_state.get("user_summary"),
                "question_generation_result": final_state.get("question_generation_result"),
                "user_summary_result": final_state.get("user_summary_result"),
                "node_history": final_state["node_history"]
            }
        )
        
    except Exception as e:
        print(f"❌ Error running quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to run quiz: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for LangGraph agent."""
    return {
        "success": True,
        "message": "LangGraph Quiz Agent is healthy",
        "service": "langgraph_quiz_agent"
    }

@router.get("/user-summary/{session_id}")
async def get_user_summary(session_id: str):
    """Get comprehensive user summary for a session."""
    try:
        from .user_summary_service import user_summary_service
        
        summary = user_summary_service.get_user_summary(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail=f"No summary found for session {session_id}")
        
        return QuizResponse(
            success=True,
            message="User summary retrieved successfully",
            data=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user summary: {str(e)}")

@router.get("/info")
async def get_agent_info():
    """Get information about the LangGraph quiz agent."""
    return {
        "success": True,
        "message": "LangGraph Quiz Agent Information",
        "data": {
            "agent_type": "LangGraph Adaptive Quiz Agent",
            "model": "Qwen 3-32B (via Groq)",
            "nodes": [
                "node_1_initial_shortcuts",
                "node_2_check_response", 
                "node_3a_correct_followup",
                "node_3b_topic_catalog",
                "node_4_select_new_topic",
                "node_5_ask_question",
                "node_6_generate_questions_and_summary"
            ],
            "features": [
                "Adaptive question difficulty",
                "Topic-based progression",
                "Performance tracking",
                "AI-powered feedback",
                "Database integration",
                "AI-generated question creation",
                "Comprehensive user profiling",
                "Self-improving questionnaire"
            ],
            "max_questions": 25
        }
    }
