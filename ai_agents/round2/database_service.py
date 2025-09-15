"""
Database service for Round 2 quiz system.
Handles fetching medium difficulty questions from PostgreSQL database.
"""
from typing import List, Dict, Optional
import random

# Import database utilities from auth module
from auth.database import get_db

class Round2DatabaseService:
    """Service for database operations related to Round 2 quiz questions."""
    
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
        
        correct_letter = Round2DatabaseService._convert_answer_to_letter(row['answer'], options)
        
        return {
            "id": row['id'],
            "question": row['question'],
            "options": options,
            "correct_answer": correct_letter,
            "topic": row['topic'],
            "difficulty": row['difficulty']
        }
    
    @staticmethod
    def get_all_medium_topics() -> List[str]:
        """Get all unique topics from medium difficulty questions."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT topic 
                    FROM quiz_questions 
                    WHERE difficulty = 'medium'
                    ORDER BY topic
                """)
                topics = [row['topic'] for row in cursor.fetchall()]
                return topics
    
    @staticmethod
    def get_medium_questions_by_topics(topics: List[str], limit: int = 10) -> List[Dict]:
        """Get medium questions for specific topics."""
        if not topics:
            return []
            
        with get_db() as connection:
            with connection.cursor() as cursor:
                # Create placeholders for topics
                placeholders = ','.join(['%s'] * len(topics))
                
                cursor.execute(f"""
                    SELECT id, question, option_a, option_b, option_c, option_d, answer, topic, difficulty
                    FROM quiz_questions 
                    WHERE topic IN ({placeholders}) AND difficulty = 'medium'
                    ORDER BY RANDOM()
                    LIMIT %s
                """, topics + [limit])
                
                questions = []
                for row in cursor.fetchall():
                    questions.append(Round2DatabaseService._create_question_object(row))
                
                return questions
    
    @staticmethod
    def get_random_medium_questions(limit: int = 10) -> List[Dict]:
        """Get random medium difficulty questions when user doesn't have enough strong topics."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, question, option_a, option_b, option_c, option_d, answer, topic, difficulty
                    FROM quiz_questions 
                    WHERE difficulty = 'medium'
                    ORDER BY RANDOM()
                    LIMIT %s
                """, (limit,))
                
                questions = []
                for row in cursor.fetchall():
                    questions.append(Round2DatabaseService._create_question_object(row))
                
                return questions
    
    @staticmethod
    def get_medium_database_stats() -> Dict:
        """Get statistics about medium difficulty questions."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                # Total medium questions
                cursor.execute("SELECT COUNT(*) as total FROM quiz_questions WHERE difficulty = 'medium'")
                total = cursor.fetchone()['total']
                
                # Topics in medium questions
                cursor.execute("""
                    SELECT COUNT(DISTINCT topic) as topics 
                    FROM quiz_questions 
                    WHERE difficulty = 'medium'
                """)
                topics = cursor.fetchone()['topics']
                
                # Questions per topic (medium)
                cursor.execute("""
                    SELECT topic, COUNT(*) as count 
                    FROM quiz_questions 
                    WHERE difficulty = 'medium'
                    GROUP BY topic 
                    ORDER BY count DESC
                """)
                topic_distribution = [dict(row) for row in cursor.fetchall()]
                
                return {
                    "total_medium_questions": total,
                    "available_medium_topics": topics,
                    "topic_distribution": topic_distribution
                }
    
    @staticmethod
    def get_diverse_medium_questions(target_count: int = 10, preferred_topics: List[str] = None) -> List[Dict]:
        """Get a diverse set of medium questions, optionally prioritizing specific topics."""
        if preferred_topics:
            # First try to get questions from preferred topics
            preferred_questions = Round2DatabaseService.get_medium_questions_by_topics(
                preferred_topics, 
                target_count
            )
            
            if len(preferred_questions) >= target_count:
                return preferred_questions[:target_count]
            
            # If not enough from preferred topics, fill with random medium questions
            remaining_needed = target_count - len(preferred_questions)
            additional_questions = Round2DatabaseService.get_random_medium_questions(remaining_needed)
            
            # Combine and shuffle
            all_questions = preferred_questions + additional_questions
            random.shuffle(all_questions)
            return all_questions[:target_count]
        else:
            # No preferred topics, get random medium questions
            return Round2DatabaseService.get_random_medium_questions(target_count)
    
    @staticmethod
    def check_topic_has_medium_questions(topic: str) -> bool:
        """Check if a topic has medium difficulty questions available."""
        with get_db() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM quiz_questions 
                    WHERE topic = %s AND difficulty = 'medium'
                """, (topic,))
                
                count = cursor.fetchone()['count']
                return count > 0
