"""
Tools for the LangGraph quiz agent.
Uses existing agent_helper tools directly.
"""
import random
from typing import Dict, List, Optional
import sys
import os

# Add the project root to the path so we can import agent_helper
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agent_helper.tools import get_all_topics as helper_get_topics
from agent_helper.response_service import ResponseService
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection string (same as insert_quiz_data.py)
DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    """Get database connection using the same method as insert_quiz_data.py"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def get_all_topics() -> List[str]:
    """Get all available topics from the database."""
    try:
        connection = get_db_connection()
        connection.autocommit = True
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT topic 
                FROM quiz_questions 
                ORDER BY topic
            """)
            
            topics = [row['topic'] for row in cursor.fetchall()]
            return topics
    except Exception as e:
        print(f"Error getting topics: {str(e)}")
        return []

def get_question_by_topic_and_difficulty(topic: str, difficulty: str) -> Optional[Dict]:
    """Get a question by topic and difficulty."""
    try:
        connection = get_db_connection()
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
                return None
            
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
                "question_id": row['id'],
                "question": row['question'],
                "options": options,
                "correct_answer": correct_letter,
                "topic": row['topic'],
                "difficulty": row['difficulty']
            }
    except Exception as e:
        print(f"Error getting question: {str(e)}")
        return None

def record_user_response(
    session_id: str, 
    question_id: int, 
    user_answer: str, 
    response_time_seconds: Optional[int] = None,
    additional_data: Optional[Dict] = None
) -> Dict:
    """Record a user's response to a question."""
    try:
        # Get question details first
        connection = get_db_connection()
        connection.autocommit = True
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT answer, topic, difficulty, option_a, option_b, option_c, option_d
                FROM quiz_questions 
                WHERE id = %s
            """, (question_id,))
            
            question = cursor.fetchone()
            if not question:
                return {"success": False, "error": "Question not found"}
        
        # Get the correct answer letter
        options = {
            "A": question['option_a'],
            "B": question['option_b'],
            "C": question['option_c'],
            "D": question['option_d']
        }
        
        correct_letter = "A"  # fallback
        for letter, option_text in options.items():
            if option_text == question['answer']:
                correct_letter = letter
                break
        
        is_correct = user_answer.upper() == correct_letter
        
        # Use ResponseService to record the response
        result = ResponseService.record_response(
            session_id=session_id,
            question_id=question_id,
            user_answer=user_answer.upper(),
            correct_answer=correct_letter,
            is_correct=is_correct,
            topic=question['topic'],
            difficulty=question['difficulty'],
            response_time_seconds=response_time_seconds,
            additional_data=additional_data
        )
        
        # Add the correctness information to the result
        if result.get("success"):
            result["is_correct"] = is_correct
            result["correct_answer"] = correct_letter
        
        return result
    except Exception as e:
        print(f"Error recording response: {str(e)}")
        return {"success": False, "error": str(e)}

def get_session_responses(session_id: str) -> List[Dict]:
    """Get all responses for a session."""
    try:
        return ResponseService.get_session_responses(session_id)
    except Exception as e:
        print(f"Error getting session responses: {str(e)}")
        return []

def get_session_performance(session_id: str) -> Optional[Dict]:
    """Get performance summary for a session."""
    try:
        return ResponseService.get_user_performance_summary(session_id)
    except Exception as e:
        print(f"Error getting session performance: {str(e)}")
        return None

def get_random_topic_from_list(topics: List[str]) -> Optional[str]:
    """Get a random topic from a list of topics."""
    if not topics:
        return None
    return random.choice(topics)

def filter_unasked_topics(all_topics: List[str], asked_topics: List[str]) -> List[str]:
    """Filter out topics that have already been asked."""
    return [topic for topic in all_topics if topic not in asked_topics]
