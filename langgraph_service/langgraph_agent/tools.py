"""
Tools for the LangGraph quiz agent.
Communicates with backend service via HTTP API.
"""
import random
import requests
import os
from typing import Dict, List, Optional

# Backend service URL (configurable via environment variable)
BACKEND_SERVICE_URL = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")

def get_all_topics() -> List[str]:
    """Get all available topics from the backend service."""
    try:
        response = requests.get(f"{BACKEND_SERVICE_URL}/agent-helper/topics")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["data"]["topics"]
        print(f"Error getting topics: HTTP {response.status_code}")
        return []
    except Exception as e:
        print(f"Error getting topics: {str(e)}")
        return []

def get_question_by_topic_and_difficulty(topic: str, difficulty: str) -> Optional[Dict]:
    """Get a question by topic and difficulty from backend service."""
    try:
        params = {"topic": topic, "difficulty": difficulty}
        response = requests.get(f"{BACKEND_SERVICE_URL}/agent-helper/get-question", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                question_data = data["data"]
                # We need to get the correct answer separately since it's not in the API response
                # For now, we'll fetch it directly from database for internal use
                correct_answer = _get_correct_answer_for_question(question_data["question_id"])
                question_data["correct_answer"] = correct_answer
                return question_data
        
        print(f"Error getting question: HTTP {response.status_code}")
        return None
    except Exception as e:
        print(f"Error getting question: {str(e)}")
        return None

def _get_correct_answer_for_question(question_id: int) -> str:
    """Internal function to get correct answer for validation (not exposed to frontend)."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Database connection string (same as insert_quiz_data.py)
        DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        
        connection = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        connection.autocommit = True
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT option_a, option_b, option_c, option_d, answer
                FROM quiz_questions 
                WHERE id = %s
            """, (question_id,))
            
            row = cursor.fetchone()
            if not row:
                return "A"
            
            options = {
                "A": row['option_a'],
                "B": row['option_b'],
                "C": row['option_c'],
                "D": row['option_d']
            }
            
            # Find correct answer letter
            for letter, option_text in options.items():
                if option_text == row['answer']:
                    return letter
            return "A"
            
    except Exception as e:
        print(f"Error getting correct answer: {str(e)}")
        return "A"

def record_user_response(
    session_id: str, 
    question_id: int, 
    user_answer: str, 
    response_time_seconds: Optional[int] = None,
    additional_data: Optional[Dict] = None
) -> Dict:
    """Record a user's response via backend service."""
    try:
        import json
        
        params = {
            "session_id": session_id,
            "question_id": question_id,
            "user_answer": user_answer
        }
        
        if response_time_seconds is not None:
            params["response_time_seconds"] = response_time_seconds
            
        if additional_data:
            params["additional_data"] = json.dumps(additional_data)
        
        response = requests.post(f"{BACKEND_SERVICE_URL}/agent-helper/record-response", params=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                # Add correctness information from the response
                return {
                    "success": True,
                    "is_correct": result["data"]["is_correct"],
                    "correct_answer": result["data"]["correct_answer"],
                    "response_id": result.get("response_id")
                }
            return result
        
        return {"success": False, "error": f"HTTP {response.status_code}"}
        
    except Exception as e:
        print(f"Error recording response: {str(e)}")
        return {"success": False, "error": str(e)}

def get_session_responses(session_id: str) -> List[Dict]:
    """Get all responses for a session via backend service."""
    try:
        params = {"session_id": session_id}
        response = requests.get(f"{BACKEND_SERVICE_URL}/agent-helper/session-responses", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["data"]["responses"]
        
        print(f"Error getting session responses: HTTP {response.status_code}")
        return []
    except Exception as e:
        print(f"Error getting session responses: {str(e)}")
        return []

def get_session_performance(session_id: str) -> Optional[Dict]:
    """Get performance summary for a session via backend service."""
    try:
        params = {"session_id": session_id}
        response = requests.get(f"{BACKEND_SERVICE_URL}/agent-helper/session-performance", params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data["data"]
        
        print(f"Error getting session performance: HTTP {response.status_code}")
        return None
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
