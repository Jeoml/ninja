"""
FastAPI routes for Round 2 quiz system.
Handles medium difficulty questions to test depth of knowledge.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from .models import (
    Round2StartRequest, Round2SubmitAnswerRequest, Round2Response,
    Round2QuestionData, Round2AnswerResult, Round2PerformanceSummary,
    Round2QuizStatus, Round2DatabaseStats
)
from .quiz_service import Round2QuizService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ai-agents/round2", tags=["Round 2 Quiz"])

# Global quiz service instance (in production, use dependency injection)
quiz_service = Round2QuizService()

@router.post("/start", response_model=Round2Response)
async def start_round2_quiz(request: Round2StartRequest) -> Dict[str, Any]:
    """
    Start a Round 2 quiz session.
    Tests depth of knowledge on strong topics from Round 1 using medium difficulty questions.
    """
    try:
        logger.info(f"Starting Round 2 quiz with max_questions={request.max_questions}, "
                   f"round1_strong_topics={request.round1_strong_topics}")
        
        result = quiz_service.start_quiz_session(
            max_questions=request.max_questions,
            round1_strong_topics=request.round1_strong_topics,
            user_email=request.user_email
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        logger.info("Round 2 quiz started successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error starting Round 2 quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start Round 2 quiz: {str(e)}")

@router.get("/question", response_model=Round2Response)
async def get_next_round2_question() -> Dict[str, Any]:
    """
    Get the next Round 2 question.
    Returns medium difficulty questions based on intelligent selection algorithm.
    """
    try:
        logger.info("Getting next Round 2 question")
        
        result = quiz_service.get_next_question()
        
        if not result["success"]:
            if "No active" in result["message"]:
                raise HTTPException(status_code=400, detail=result["message"])
            else:
                raise HTTPException(status_code=404, detail=result["message"])
        
        logger.info(f"Retrieved Round 2 question: {result['data']['question_id']} "
                   f"from topic: {result['data']['topic']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Round 2 question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Round 2 question: {str(e)}")

@router.post("/answer", response_model=Round2Response)
async def submit_round2_answer(request: Round2SubmitAnswerRequest) -> Dict[str, Any]:
    """
    Submit an answer for the current Round 2 question.
    Tracks performance and updates the 'crazy good' topics catalog.
    """
    try:
        logger.info(f"Submitting Round 2 answer: {request.answer}")
        
        result = quiz_service.submit_answer(request.answer.value)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        is_correct = result["data"]["is_correct"]
        topic = result["data"]["topic"]
        
        logger.info(f"Round 2 answer submitted - Correct: {is_correct}, Topic: {topic}")
        
        if result["data"].get("quiz_completed"):
            logger.info("Round 2 quiz completed")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting Round 2 answer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit Round 2 answer: {str(e)}")

@router.get("/performance", response_model=Round2Response)
async def get_round2_performance() -> Dict[str, Any]:
    """
    Get current Round 2 performance summary.
    Shows expert, proficient, developing, and struggling topics.
    """
    try:
        logger.info("Getting Round 2 performance summary")
        
        result = quiz_service.get_current_performance()
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        logger.info("Round 2 performance summary retrieved")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Round 2 performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Round 2 performance: {str(e)}")

@router.get("/status", response_model=Round2Response)
async def get_round2_quiz_status() -> Dict[str, Any]:
    """
    Get current Round 2 quiz status.
    Shows if quiz is active, progress, and current state.
    """
    try:
        logger.info("Getting Round 2 quiz status")
        
        result = quiz_service.get_quiz_status()
        
        logger.info(f"Round 2 status: active={result['data']['is_active']}, "
                   f"questions_asked={result['data']['questions_asked']}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting Round 2 status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Round 2 status: {str(e)}")

@router.get("/database-stats", response_model=Round2Response)
async def get_round2_database_stats() -> Dict[str, Any]:
    """
    Get Round 2 database statistics.
    Shows available medium difficulty questions and topic distribution.
    """
    try:
        logger.info("Getting Round 2 database statistics")
        
        from .database_service import Round2DatabaseService
        stats = Round2DatabaseService.get_medium_database_stats()
        
        result = {
            "success": True,
            "message": "Round 2 database statistics retrieved",
            "data": stats
        }
        
        logger.info(f"Round 2 DB stats: {stats['total_medium_questions']} medium questions, "
                   f"{stats['available_medium_topics']} topics")
        return result
        
    except Exception as e:
        logger.error(f"Error getting Round 2 database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Round 2 database stats: {str(e)}")

@router.post("/reset", response_model=Round2Response)
async def reset_round2_quiz() -> Dict[str, Any]:
    """
    Reset the current Round 2 quiz session.
    Clears all progress and allows starting a new session.
    """
    try:
        logger.info("Resetting Round 2 quiz")
        
        # Reset the quiz service
        global quiz_service
        quiz_service = Round2QuizService()
        
        result = {
            "success": True,
            "message": "Round 2 quiz reset successfully",
            "data": {
                "reset_completed": True,
                "ready_for_new_session": True
            }
        }
        
        logger.info("Round 2 quiz reset completed")
        return result
        
    except Exception as e:
        logger.error(f"Error resetting Round 2 quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset Round 2 quiz: {str(e)}")

@router.get("/topics", response_model=Round2Response)
async def get_available_round2_topics() -> Dict[str, Any]:
    """
    Get all available topics for Round 2 (medium difficulty).
    Useful for understanding what topics can be tested in depth.
    """
    try:
        logger.info("Getting available Round 2 topics")
        
        from .database_service import Round2DatabaseService
        topics = Round2DatabaseService.get_all_medium_topics()
        
        result = {
            "success": True,
            "message": "Available Round 2 topics retrieved",
            "data": {
                "available_topics": topics,
                "total_topics": len(topics)
            }
        }
        
        logger.info(f"Found {len(topics)} available Round 2 topics")
        return result
        
    except Exception as e:
        logger.error(f"Error getting Round 2 topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Round 2 topics: {str(e)}")

# Health check endpoint
@router.get("/health", response_model=Round2Response)
async def round2_health_check() -> Dict[str, Any]:
    """Health check for Round 2 quiz system."""
    try:
        from .database_service import Round2DatabaseService
        
        # Test database connection
        stats = Round2DatabaseService.get_medium_database_stats()
        
        return {
            "success": True,
            "message": "Round 2 quiz system is healthy",
            "data": {
                "service_status": "healthy",
                "database_connected": True,
                "medium_questions_available": stats["total_medium_questions"] > 0,
                "topics_available": stats["available_medium_topics"] > 0
            }
        }
        
    except Exception as e:
        logger.error(f"Round 2 health check failed: {str(e)}")
        return {
            "success": False,
            "message": f"Round 2 health check failed: {str(e)}",
            "data": {
                "service_status": "unhealthy",
                "database_connected": False,
                "error": str(e)
            }
        }
