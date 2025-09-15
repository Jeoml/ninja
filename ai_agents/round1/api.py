"""
FastAPI routes for Round 1 Quiz System.
Chat-based quiz interface with topic performance tracking.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from .models import (
    QuizStartRequest, SubmitAnswerRequest, QuizResponse, 
    AnswerChoice, QuestionData, PerformanceSummary, QuizStatus
)
from .quiz_service import QuizService

# Create router
router = APIRouter(prefix="/ai-agents/round1", tags=["Round 1 Quiz"])

# Global quiz service instance (in production, use dependency injection)
quiz_service = QuizService()

@router.post("/start", response_model=QuizResponse)
async def start_quiz(request: QuizStartRequest = QuizStartRequest()):
    """
    Start a new Round 1 quiz session.
    
    - Fetches 10-15 easy questions from database
    - Focuses on different topics
    - Initializes performance tracking
    """
    try:
        result = quiz_service.start_quiz_session(request.max_questions)
        return QuizResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start quiz: {str(e)}")

@router.get("/question", response_model=QuizResponse)
async def get_next_question():
    """
    Get the next question in the quiz.
    
    - Returns question with multiple choice options
    - Intelligently selects questions to cover different topics
    - Tracks progress through the quiz
    """
    try:
        result = quiz_service.get_next_question()
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return QuizResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get question: {str(e)}")

@router.post("/answer", response_model=QuizResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """
    Submit answer for current question.
    
    - Validates answer choice (A, B, C, or D)
    - Updates topic performance catalog
    - Returns correct answer and explanation
    - Tracks solved/unsolved topics
    """
    try:
        result = quiz_service.submit_answer(request.answer.value)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return QuizResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")

@router.get("/performance", response_model=QuizResponse)
async def get_performance():
    """
    Get current performance summary.
    
    - Shows solved vs unsolved topics
    - Displays accuracy statistics
    - Provides topic-wise breakdown
    """
    try:
        result = quiz_service.get_current_performance()
        return QuizResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance: {str(e)}")

@router.get("/status", response_model=QuizResponse)
async def get_quiz_status():
    """
    Get current quiz session status.
    
    - Shows if quiz is active
    - Displays progress information
    - Indicates if there's a pending question
    """
    try:
        result = quiz_service.get_quiz_status()
        return QuizResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.post("/end", response_model=QuizResponse)
async def end_quiz():
    """
    End current quiz session.
    
    - Provides final performance summary
    - Shows topic catalog (solved/unsolved)
    - Gives study recommendations
    """
    try:
        result = quiz_service.end_quiz_session()
        return QuizResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end quiz: {str(e)}")

@router.post("/reset", response_model=QuizResponse)
async def reset_session():
    """
    Reset the current quiz session.
    
    - Clears current question and progress
    - Keeps performance history
    - Allows starting fresh
    """
    try:
        result = quiz_service.reset_session()
        return QuizResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset session: {str(e)}")

# Chat-like endpoints for better user experience

@router.get("/chat/intro")
async def chat_introduction():
    """Get a friendly introduction to Round 1 quiz."""
    return {
        "message": """
🎯 Welcome to Round 1 Quiz!

I'll ask you 10-15 easy questions from different topics to assess your knowledge.

Here's how it works:
• Each question has 4 options (A, B, C, D)
• I'll track which topics you're strong in vs need work
• If you get a topic right AND wrong, I'll mark it as 'solved' 
• I'll try to ask questions from different topics

Ready to start? Use `/ai-agents/round1/start` to begin!
        """.strip(),
        "available_commands": [
            "POST /ai-agents/round1/start - Start quiz",
            "GET /ai-agents/round1/question - Get next question", 
            "POST /ai-agents/round1/answer - Submit answer",
            "GET /ai-agents/round1/performance - View performance",
            "GET /ai-agents/round1/status - Check quiz status"
        ]
    }

@router.get("/chat/help")
async def chat_help():
    """Get help with using the quiz system."""
    return {
        "message": """
🤖 Round 1 Quiz Help

**Chat Flow:**
1. Start: `POST /start` with optional max_questions
2. Get Question: `GET /question` 
3. Answer: `POST /answer` with {"answer": "A/B/C/D"}
4. Repeat steps 2-3 until quiz ends
5. View Results: `GET /performance`

**Key Features:**
• ✅ Solved topics: You got them right
• ❌ Unsolved topics: You need to review these
• 🎯 Smart question selection: Focuses on different topics
• 📊 Performance tracking: See your progress

**Example Usage:**
```
POST /start {"max_questions": 12}
GET /question
POST /answer {"answer": "B"}
GET /performance
```
        """.strip()
    }
