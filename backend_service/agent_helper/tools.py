"""
Tools API for agent helper.
Provides endpoints to retrieve topics and select questions from the database.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

# Create router
router = APIRouter(prefix="/agent-helper", tags=["Agent Helper"])

@router.get("/topics")
async def get_all_topics():
    """Get all unique topics from the database."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Database connection string (same as insert_quiz_data.py)
        DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        connection.autocommit = True
        
        with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT topic 
                    FROM quiz_questions 
                    ORDER BY topic
                """)
                
                topics = [row['topic'] for row in cursor.fetchall()]
                
                return {
                    "success": True,
                    "message": f"Found {len(topics)} topics",
                    "data": {
                        "topics": topics,
                        "total_count": len(topics)
                    }
                }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")

@router.get("/get-question")
async def get_question_by_topic_and_difficulty(
    topic: str = Query(..., description="Topic name"),
    difficulty: str = Query(..., description="Difficulty level (easy, medium, hard)")
):
    """Get a random question based on topic and difficulty."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Database connection string (same as insert_quiz_data.py)
        DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        
        # Validate difficulty
        valid_difficulties = ['easy', 'medium', 'hard']
        if difficulty.lower() not in valid_difficulties:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid difficulty. Must be one of: {', '.join(valid_difficulties)}"
            )
        
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        connection.autocommit = True
        
        with connection.cursor() as cursor:
            # Get a random question for the specified topic and difficulty
                cursor.execute("""
                    SELECT id, question, option_a, option_b, option_c, option_d, answer, topic, difficulty
                    FROM quiz_questions 
                    WHERE topic = %s AND difficulty = %s
                    ORDER BY RANDOM()
                    LIMIT 1
                """, (topic, difficulty.lower()))
                
                row = cursor.fetchone()
                
                if not row:
                    # Check if topic exists
                    cursor.execute("SELECT DISTINCT topic FROM quiz_questions WHERE topic = %s", (topic,))
                    topic_exists = cursor.fetchone()
                    
                    if not topic_exists:
                        raise HTTPException(
                            status_code=404, 
                            detail=f"Topic '{topic}' not found in database"
                        )
                    
                    # Check if difficulty exists for this topic
                    cursor.execute("""
                        SELECT DISTINCT difficulty FROM quiz_questions 
                        WHERE topic = %s
                    """, (topic,))
                    available_difficulties = [row['difficulty'] for row in cursor.fetchall()]
                    
                    raise HTTPException(
                        status_code=404, 
                        detail=f"No {difficulty} questions found for topic '{topic}'. Available difficulties: {', '.join(available_difficulties)}"
                    )
                
                # Convert answer to letter format
                options = {
                    "A": row['option_a'],
                    "B": row['option_b'],
                    "C": row['option_c'],
                    "D": row['option_d']
                }
                
                # Find correct answer letter
                correct_letter = "A"  # fallback
                for letter, option_text in options.items():
                    if option_text == row['answer']:
                        correct_letter = letter
                        break
                
                return {
                    "success": True,
                    "message": f"Question found for topic '{topic}' with {difficulty} difficulty",
                    "data": {
                        "question_id": row['id'],
                        "question": row['question'],
                        "options": options,
                        "topic": row['topic'],
                        "difficulty": row['difficulty']
                    }
                }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get question: {str(e)}")

@router.post("/record-response")
async def record_user_response(
    session_id: str = Query(..., description="Session ID for tracking user responses"),
    question_id: int = Query(..., description="Question ID"),
    user_answer: str = Query(..., description="User's answer (A, B, C, or D)"),
    response_time_seconds: int = Query(None, description="Time taken to answer in seconds"),
    additional_data: str = Query(None, description="Additional data as JSON string")
):
    """Record a user's response to a question."""
    try:
        from .response_service import ResponseService
        from auth.database import get_db
        import json
        
        # Validate user answer
        if user_answer.upper() not in ['A', 'B', 'C', 'D']:
            raise HTTPException(
                status_code=400,
                detail="Invalid user answer. Must be A, B, C, or D"
            )
        
        # Get question details to verify it exists and get correct answer
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        connection.autocommit = True
        
        with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, answer, topic, difficulty
                    FROM quiz_questions 
                    WHERE id = %s
                """, (question_id,))
                
                question = cursor.fetchone()
                if not question:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Question with ID {question_id} not found"
                    )
        
        # Get the correct answer letter
        connection2 = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        connection2.autocommit = True
        
        with connection2.cursor() as cursor:
                cursor.execute("""
                    SELECT option_a, option_b, option_c, option_d, answer
                    FROM quiz_questions 
                    WHERE id = %s
                """, (question_id,))
                
                row = cursor.fetchone()
                options = {
                    "A": row['option_a'],
                    "B": row['option_b'],
                    "C": row['option_c'],
                    "D": row['option_d']
                }
                
                # Find correct answer letter
                correct_letter = "A"  # fallback
                for letter, option_text in options.items():
                    if option_text == row['answer']:
                        correct_letter = letter
                        break
        
        # Check if answer is correct
        is_correct = user_answer.upper() == correct_letter
        
        # Parse additional data if provided
        extra_data = None
        if additional_data:
            try:
                extra_data = json.loads(additional_data)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON format for additional_data"
                )
        
        # Record the response
        result = ResponseService.record_response(
            session_id=session_id,
            question_id=question_id,
            user_answer=user_answer.upper(),
            correct_answer=correct_letter,
            is_correct=is_correct,
            topic=question['topic'],
            difficulty=question['difficulty'],
            response_time_seconds=response_time_seconds,
            additional_data=extra_data
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return {
            "success": True,
            "message": "Response recorded successfully",
            "data": {
                "response_id": result["response_id"],
                "is_correct": is_correct,
                "user_answer": user_answer.upper(),
                "correct_answer": correct_letter,
                "topic": question['topic'],
                "difficulty": question['difficulty']
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record response: {str(e)}")

@router.get("/session-responses")
async def get_session_responses(
    session_id: str = Query(..., description="Session ID to get responses for")
):
    """Get all responses for a specific session."""
    try:
        from .response_service import ResponseService
        
        responses = ResponseService.get_session_responses(session_id)
        
        return {
            "success": True,
            "message": f"Found {len(responses)} responses for session {session_id}",
            "data": {
                "session_id": session_id,
                "responses": responses,
                "total_count": len(responses)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session responses: {str(e)}")

@router.get("/session-performance")
async def get_session_performance(
    session_id: str = Query(..., description="Session ID to get performance for")
):
    """Get performance summary for a specific session."""
    try:
        from .response_service import ResponseService
        
        performance = ResponseService.get_user_performance_summary(session_id)
        
        if "error" in performance:
            raise HTTPException(status_code=500, detail=performance["error"])
        
        return {
            "success": True,
            "message": f"Performance summary for session {session_id}",
            "data": performance
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session performance: {str(e)}")
