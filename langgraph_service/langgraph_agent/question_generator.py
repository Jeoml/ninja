"""
AI-powered question generation service for improving the questionnaire.
Analyzes user responses and generates new questions based on their performance.
"""
from typing import Dict, List, Any
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from .groq_client import groq_client

# Database connection string (same as insert_quiz_data.py)
DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    """Get database connection using the same method as insert_quiz_data.py"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

class QuestionGenerator:
    """Service for generating new questions based on user performance."""
    
    def __init__(self):
        self.groq_client = groq_client
    
    def analyze_user_responses(self, session_responses: List[Dict]) -> Dict[str, Any]:
        """Analyze user responses to identify patterns and areas for improvement."""
        if not session_responses:
            return {"topics": [], "strengths": [], "weaknesses": [], "patterns": []}
        
        # Categorize responses by topic and correctness
        topic_performance = {}
        difficulty_performance = {}
        
        for response in session_responses:
            topic = response.get('topic', 'Unknown')
            difficulty = response.get('response_data', {}).get('difficulty', 'easy')
            is_correct = response.get('is_correct', False)
            
            # Track topic performance
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            topic_performance[topic]['total'] += 1
            if is_correct:
                topic_performance[topic]['correct'] += 1
            
            # Track difficulty performance
            if difficulty not in difficulty_performance:
                difficulty_performance[difficulty] = {'correct': 0, 'total': 0}
            difficulty_performance[difficulty]['total'] += 1
            if is_correct:
                difficulty_performance[difficulty]['correct'] += 1
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        for topic, perf in topic_performance.items():
            accuracy = perf['correct'] / perf['total'] if perf['total'] > 0 else 0
            if accuracy >= 0.7 and perf['total'] >= 2:  # Strong performance
                strengths.append(topic)
            elif accuracy < 0.5 and perf['total'] >= 2:  # Weak performance
                weaknesses.append(topic)
        
        return {
            "topics": list(topic_performance.keys()),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "topic_performance": topic_performance,
            "difficulty_performance": difficulty_performance,
            "total_responses": len(session_responses)
        }
    
    def generate_questions_with_ai(self, analysis: Dict[str, Any], count: int = 5) -> List[Dict]:
        """Use AI to generate new questions based on user performance analysis."""
        system_prompt = """You are an expert quiz question generator. Based on the user's performance analysis, generate high-quality multiple-choice questions that will help improve the assessment system.

Rules for question generation:
1. Create questions that target the user's weak areas to help identify knowledge gaps
2. Include some questions in their strong areas but at higher difficulty levels
3. Each question must have exactly 4 options (A, B, C, D)
4. Provide the correct answer
5. Focus on practical, real-world scenarios
6. Ensure questions are clear and unambiguous
7. Target difficulty should be appropriate for the topic and user's performance

Return ONLY a valid JSON array of questions in this exact format:
[
  {
    "question": "Question text here?",
    "option_a": "First option",
    "option_b": "Second option", 
    "option_c": "Third option",
    "option_d": "Fourth option",
    "answer": "Correct option text (must match one of the options exactly)",
    "topic": "Topic name",
    "difficulty": "easy|medium|hard"
  }
]"""

        user_prompt = f"""
Based on this user performance analysis, generate {count} new quiz questions:

Performance Analysis:
{json.dumps(analysis, indent=2)}

Guidelines:
- Focus on weak areas: {analysis.get('weaknesses', [])}
- Challenge strong areas: {analysis.get('strengths', [])} 
- Total responses analyzed: {analysis.get('total_responses', 0)}

Generate questions that will help better assess users with similar performance patterns.
Ensure variety in topics and difficulty levels.
"""

        try:
            response = self.groq_client.generate_response(
                system_prompt, 
                user_prompt, 
                max_tokens=2000,
                temperature=0.7
            )
            
            if not response:
                return []
            
            # Parse the JSON response
            questions = json.loads(response.strip())
            
            # Validate the questions format
            validated_questions = []
            for q in questions:
                if self._validate_question_format(q):
                    validated_questions.append(q)
            
            return validated_questions[:count]  # Ensure we don't exceed requested count
            
        except Exception as e:
            print(f"Error generating questions with AI: {str(e)}")
            return []
    
    def _validate_question_format(self, question: Dict) -> bool:
        """Validate that a generated question has the correct format."""
        required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'answer', 'topic', 'difficulty']
        
        # Check all required fields exist
        for field in required_fields:
            if field not in question or not question[field]:
                return False
        
        # Check difficulty is valid
        if question['difficulty'] not in ['easy', 'medium', 'hard']:
            return False
        
        # Check answer matches one of the options
        options = [question['option_a'], question['option_b'], question['option_c'], question['option_d']]
        if question['answer'] not in options:
            return False
        
        return True
    
    def save_questions_to_database(self, questions: List[Dict]) -> Dict[str, Any]:
        """Save generated questions to the database."""
        if not questions:
            return {"success": False, "message": "No questions to save", "saved_count": 0}
        
        try:
            connection = get_db_connection()
            connection.autocommit = True
            
            saved_count = 0
            errors = []
            
            with connection.cursor() as cursor:
                for question in questions:
                    try:
                        cursor.execute("""
                            INSERT INTO quiz_questions 
                            (question, option_a, option_b, option_c, option_d, answer, difficulty, topic, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        """, (
                            question['question'],
                            question['option_a'],
                            question['option_b'],
                            question['option_c'],
                            question['option_d'],
                            question['answer'],
                            question['difficulty'],
                            question['topic']
                        ))
                        saved_count += 1
                    except Exception as e:
                        errors.append(f"Failed to save question: {str(e)}")
            
            connection.close()
            
            return {
                "success": True,
                "message": f"Successfully saved {saved_count} questions to database",
                "saved_count": saved_count,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Database error: {str(e)}",
                "saved_count": 0
            }
    
    def generate_and_save_questions(self, session_responses: List[Dict], count: int = 5) -> Dict[str, Any]:
        """Complete workflow: analyze responses, generate questions, and save to database."""
        print(f"🤖 Analyzing {len(session_responses)} user responses...")
        
        # Analyze user performance
        analysis = self.analyze_user_responses(session_responses)
        print(f"📊 Analysis complete: {len(analysis['strengths'])} strengths, {len(analysis['weaknesses'])} weaknesses")
        
        # Generate questions using AI
        print(f"🧠 Generating {count} new questions based on performance...")
        generated_questions = self.generate_questions_with_ai(analysis, count)
        print(f"✨ Generated {len(generated_questions)} questions")
        
        if not generated_questions:
            return {
                "success": False,
                "message": "Failed to generate questions",
                "analysis": analysis,
                "generated_count": 0,
                "saved_count": 0
            }
        
        # Save to database
        print("💾 Saving questions to database...")
        save_result = self.save_questions_to_database(generated_questions)
        
        return {
            "success": save_result["success"],
            "message": save_result["message"],
            "analysis": analysis,
            "generated_questions": generated_questions,
            "generated_count": len(generated_questions),
            "saved_count": save_result["saved_count"],
            "errors": save_result.get("errors", [])
        }

# Global instance
question_generator = QuestionGenerator()
