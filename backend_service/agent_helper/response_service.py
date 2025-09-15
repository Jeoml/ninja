"""
Response service for storing and managing user quiz responses.
"""
from typing import Dict, List, Optional
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database connection string (same as insert_quiz_data.py)
DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    """Get database connection using the same method as insert_quiz_data.py"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

class ResponseService:
    """Service for managing user quiz responses in the database."""
    
    @staticmethod
    def create_responses_table():
        """Create the user_responses table if it doesn't exist."""
        connection = get_db_connection()
        connection.autocommit = True
        
        with connection.cursor() as cursor:
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS user_responses (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL,
                    question_id INTEGER NOT NULL,
                    user_answer VARCHAR(10) NOT NULL,
                    correct_answer VARCHAR(10) NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    topic VARCHAR(50) NOT NULL,
                    difficulty VARCHAR(10) NOT NULL,
                    response_time_seconds INTEGER,
                    response_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_id) REFERENCES quiz_questions(id)
                );
                """
                cursor.execute(create_table_sql)
                connection.commit()
                print("✅ Table 'user_responses' created or verified successfully")
    
    @staticmethod
    def record_response(
        session_id: str,
        question_id: int,
        user_answer: str,
        correct_answer: str,
        is_correct: bool,
        topic: str,
        difficulty: str,
        response_time_seconds: Optional[int] = None,
        additional_data: Optional[Dict] = None
    ) -> Dict:
        """Record a user's response to a question."""
        try:
            # Ensure table exists
            ResponseService.create_responses_table()
            
            connection = get_db_connection()
            connection.autocommit = True
            
            with connection.cursor() as cursor:
                    # Prepare response data as JSON
                    response_data = {
                        "user_answer": user_answer,
                        "correct_answer": correct_answer,
                        "is_correct": is_correct,
                        "topic": topic,
                        "difficulty": difficulty,
                        "response_time_seconds": response_time_seconds,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Add any additional data
                    if additional_data:
                        if isinstance(additional_data, dict):
                            response_data.update(additional_data)
                        else:
                            response_data["additional_data"] = additional_data
                    
                    # Insert response record
                    cursor.execute("""
                        INSERT INTO user_responses 
                        (session_id, question_id, user_answer, correct_answer, is_correct, 
                         topic, difficulty, response_time_seconds, response_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        session_id, question_id, user_answer, correct_answer, is_correct,
                        topic, difficulty, response_time_seconds, json.dumps(response_data)
                    ))
                    
                    response_id = cursor.fetchone()['id']
                    connection.commit()
                    
                    return {
                        "success": True,
                        "message": "Response recorded successfully",
                        "response_id": response_id
                    }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to record response: {str(e)}",
                "error": str(e)
            }
    
    @staticmethod
    def get_session_responses(session_id: str) -> List[Dict]:
        """Get all responses for a specific session."""
        try:
            connection = get_db_connection()
            connection.autocommit = True
            
            with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, question_id, user_answer, correct_answer, is_correct,
                               topic, difficulty, response_time_seconds, response_data, created_at
                        FROM user_responses 
                        WHERE session_id = %s
                        ORDER BY created_at ASC
                    """, (session_id,))
                    
                    responses = []
                    for row in cursor.fetchall():
                        response_data = json.loads(row['response_data']) if row['response_data'] else {}
                        
                        responses.append({
                            "id": row['id'],
                            "question_id": row['question_id'],
                            "user_answer": row['user_answer'],
                            "correct_answer": row['correct_answer'],
                            "is_correct": row['is_correct'],
                            "topic": row['topic'],
                            "difficulty": row['difficulty'],
                            "response_time_seconds": row['response_time_seconds'],
                            "response_data": response_data,
                            "created_at": row['created_at'].isoformat() if row['created_at'] else None
                        })
                    
                    return responses
        
        except Exception as e:
            print(f"Error getting session responses: {str(e)}")
            return []
    
    @staticmethod
    def get_user_performance_summary(session_id: str) -> Dict:
        """Get performance summary for a user session."""
        try:
            connection = get_db_connection()
            connection.autocommit = True
            
            with connection.cursor() as cursor:
                    # Get basic stats
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_responses,
                            SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_responses,
                            AVG(response_time_seconds) as avg_response_time
                        FROM user_responses 
                        WHERE session_id = %s
                    """, (session_id,))
                    
                    stats = cursor.fetchone()
                    
                    # Get topic breakdown
                    cursor.execute("""
                        SELECT 
                            topic,
                            difficulty,
                            COUNT(*) as total_questions,
                            SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_answers,
                            AVG(response_time_seconds) as avg_time
                        FROM user_responses 
                        WHERE session_id = %s
                        GROUP BY topic, difficulty
                        ORDER BY topic, difficulty
                    """, (session_id,))
                    
                    topic_breakdown = []
                    for row in cursor.fetchall():
                        topic_breakdown.append({
                            "topic": row['topic'],
                            "difficulty": row['difficulty'],
                            "total_questions": row['total_questions'],
                            "correct_answers": row['correct_answers'],
                            "accuracy": row['correct_answers'] / row['total_questions'] if row['total_questions'] > 0 else 0,
                            "avg_response_time": float(row['avg_time']) if row['avg_time'] else None
                        })
                    
                    total_responses = stats['total_responses'] or 0
                    correct_responses = stats['correct_responses'] or 0
                    accuracy = correct_responses / total_responses if total_responses > 0 else 0
                    
                    return {
                        "session_id": session_id,
                        "total_responses": total_responses,
                        "correct_responses": correct_responses,
                        "accuracy": accuracy,
                        "avg_response_time": float(stats['avg_response_time']) if stats['avg_response_time'] else None,
                        "topic_breakdown": topic_breakdown
                    }
        
        except Exception as e:
            return {
                "error": f"Failed to get performance summary: {str(e)}"
            }
