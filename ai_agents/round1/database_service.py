"""
Database service for Round 1 quiz system.
Handles fetching questions from the PostgreSQL database.
"""
from typing import List, Dict, Optional
import random

# Import database utilities from auth module
from auth.database import get_db

class DatabaseService:
    """Service for database operations related to quiz questions."""
    
    @staticmethod
    def _convert_answer_to_letter(answer_text: str, options: dict) -> str:
        """Convert full answer text to corresponding letter (A/B/C/D)."""
        for letter, option_text in options.items():
            if option_text == answer_text:
                return letter
        return "A"  # fallback to A if no match found
    
    @staticmethod
    def _create_question_object(row) -> dict:
        """Create a standardized question object from database row."""
        options = {
            "A": row['option_a'],
            "B": row['option_b'],
            "C": row['option_c'],
            "D": row['option_d']
        }
        
        correct_letter = DatabaseService._convert_answer_to_letter(row['answer'], options)
        
        return {
            "id": row['id'],
            "question": row['question'],
            "options": options,
            "correct_answer": correct_letter,
            "topic": row['topic']
        }
    
    @staticmethod
    def get_all_topics() -> List[str]:
        """Get all unique topics from the database."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT topic 
                    FROM quiz_questions 
                    WHERE difficulty = 'easy'
                    ORDER BY topic
                """)
                topics = [row['topic'] for row in cursor.fetchall()]
                return topics
    
    @staticmethod
    def get_questions_by_topic(topic: str, limit: int = 5) -> List[Dict]:
        """Get easy questions for a specific topic."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, question, option_a, option_b, option_c, option_d, answer, topic
                    FROM quiz_questions 
                    WHERE topic = %s AND difficulty = 'easy'
                    ORDER BY RANDOM()
                    LIMIT %s
                """, (topic, limit))
                
                questions = []
                for row in cursor.fetchall():
                    questions.append(DatabaseService._create_question_object(row))
                
                return questions
    
    @staticmethod
    def get_mixed_easy_questions(limit: int = 15, exclude_topics: List[str] = None) -> List[Dict]:
        """Get a mix of easy questions from different topics."""
        if exclude_topics is None:
            exclude_topics = []
        
        with get_db() as connection:
            with connection.cursor() as cursor:
                # Build the exclusion clause
                exclude_clause = ""
                params = []
                
                if exclude_topics:
                    placeholders = ','.join(['%s'] * len(exclude_topics))
                    exclude_clause = f"AND topic NOT IN ({placeholders})"
                    params.extend(exclude_topics)
                
                params.append(limit)  # Add limit at the end
                
                query = f"""
                    SELECT id, question, option_a, option_b, option_c, option_d, answer, topic
                    FROM quiz_questions 
                    WHERE difficulty = 'easy' {exclude_clause}
                    ORDER BY RANDOM()
                    LIMIT %s
                """
                
                cursor.execute(query, params)
                
                questions = []
                for row in cursor.fetchall():
                    questions.append(DatabaseService._create_question_object(row))
                
                return questions
    
    @staticmethod
    def get_diverse_easy_questions(target_count: int = 15) -> List[Dict]:
        """Get a diverse set of easy questions, trying to cover different topics."""
        topics = DatabaseService.get_all_topics()
        questions = []
        used_topics = set()
        
        # First, try to get 1-2 questions from each topic
        questions_per_topic = max(1, target_count // len(topics)) if topics else 1
        
        for topic in topics:
            if len(questions) >= target_count:
                break
                
            topic_questions = DatabaseService.get_questions_by_topic(
                topic, 
                min(questions_per_topic, target_count - len(questions))
            )
            
            if topic_questions:
                questions.extend(topic_questions)
                used_topics.add(topic)
        
        # If we don't have enough questions, get more from any topic
        if len(questions) < target_count:
            remaining_needed = target_count - len(questions)
            additional_questions = DatabaseService.get_mixed_easy_questions(
                remaining_needed, 
                list(used_topics)
            )
            questions.extend(additional_questions)
        
        # Shuffle the final list
        random.shuffle(questions)
        return questions[:target_count]
    
    @staticmethod
    def get_question_by_id(question_id: int) -> Optional[Dict]:
        """Get a specific question by ID."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, question, option_a, option_b, option_c, option_d, answer, topic
                    FROM quiz_questions 
                    WHERE id = %s
                """, (question_id,))
                
                row = cursor.fetchone()
                if row:
                    return DatabaseService._create_question_object(row)
                return None
    
    @staticmethod
    def get_database_stats() -> Dict:
        """Get statistics about the questions database."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                # Total questions
                cursor.execute("SELECT COUNT(*) as total FROM quiz_questions")
                total = cursor.fetchone()['total']
                
                # Easy questions
                cursor.execute("SELECT COUNT(*) as easy FROM quiz_questions WHERE difficulty = 'easy'")
                easy = cursor.fetchone()['easy']
                
                # Topics
                cursor.execute("SELECT COUNT(DISTINCT topic) as topics FROM quiz_questions WHERE difficulty = 'easy'")
                topics = cursor.fetchone()['topics']
                
                # Questions per topic
                cursor.execute("""
                    SELECT topic, COUNT(*) as count 
                    FROM quiz_questions 
                    WHERE difficulty = 'easy'
                    GROUP BY topic 
                    ORDER BY count DESC
                """)
                topic_distribution = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "total_questions": total,
                    "easy_questions": easy,
                    "available_topics": topics,
                    "topic_distribution": topic_distribution
                }
