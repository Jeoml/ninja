"""
User Summary service for storing comprehensive user assessments.
"""
from typing import Dict, List, Optional
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from .groq_client import groq_client

# Database connection string (same as insert_quiz_data.py)
DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    """Get database connection using the same method as insert_quiz_data.py"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

class UserSummaryService:
    """Service for generating and storing comprehensive user summaries."""
    
    def __init__(self):
        self.groq_client = groq_client
    
    @staticmethod
    def create_user_summaries_table():
        """Create the user_summaries table if it doesn't exist."""
        try:
            connection = get_db_connection()
            connection.autocommit = True
            
            with connection.cursor() as cursor:
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS user_summaries (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL,
                    user_id VARCHAR(100),
                    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Performance Metrics
                    total_questions INTEGER NOT NULL,
                    correct_answers INTEGER NOT NULL,
                    accuracy DECIMAL(5,4) NOT NULL,
                    avg_response_time DECIMAL(8,2),
                    
                    -- Topic Analysis
                    topics_covered TEXT[] NOT NULL,
                    strong_topics TEXT[],
                    weak_topics TEXT[],
                    topic_breakdown JSONB,
                    
                    -- AI-Generated Analysis
                    cognitive_profile TEXT,
                    learning_style TEXT,
                    knowledge_gaps TEXT,
                    strengths_analysis TEXT,
                    improvement_recommendations TEXT,
                    skill_level_assessment TEXT,
                    
                    -- Comprehensive Summary
                    executive_summary TEXT NOT NULL,
                    detailed_analysis JSONB NOT NULL,
                    
                    -- Metadata
                    node_history TEXT[],
                    assessment_duration INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                cursor.execute(create_table_sql)
                print("✅ Table 'user_summaries' created or verified successfully")
                
            connection.close()
            return True
            
        except Exception as e:
            print(f"❌ Error creating user_summaries table: {str(e)}")
            return False
    
    def generate_comprehensive_summary(self, session_data: Dict, session_responses: List[Dict]) -> Dict[str, str]:
        """Generate a comprehensive user summary using AI analysis."""
        
        # Prepare data for AI analysis
        performance_data = session_data.get('performance_summary', {})
        
        system_prompt = """You are an expert educational psychologist and assessment specialist. Analyze the user's quiz performance and provide a comprehensive psychological and educational profile.

Your analysis should be professional, insightful, and actionable. Focus on:
1. Cognitive patterns and learning style
2. Knowledge strengths and gaps
3. Problem-solving approach
4. Recommendations for improvement
5. Overall skill level assessment

Provide detailed, evidence-based insights that would be valuable for educational planning."""

        user_prompt = f"""
Analyze this user's assessment performance and provide a comprehensive summary:

SESSION DATA:
- Session ID: {session_data.get('session_id')}
- Total Questions: {performance_data.get('total_responses', 0)}
- Correct Answers: {performance_data.get('correct_responses', 0)}
- Accuracy: {performance_data.get('accuracy', 0):.2%}
- Topics Covered: {session_data.get('topics_asked', [])}
- Questions Asked: {session_data.get('questions_asked', 0)}
- Node History: {session_data.get('node_history', [])}

DETAILED PERFORMANCE:
{json.dumps(performance_data.get('topic_breakdown', []), indent=2)}

RESPONSE PATTERNS:
{json.dumps([{
    'topic': r.get('topic'),
    'correct': r.get('is_correct'),
    'response_data': r.get('response_data', {})
} for r in session_responses[:10]], indent=2)}

Please provide:

1. COGNITIVE_PROFILE: Analyze their thinking patterns, decision-making style, and cognitive strengths (2-3 sentences)

2. LEARNING_STYLE: Identify their preferred learning approach based on performance patterns (2-3 sentences)

3. KNOWLEDGE_GAPS: Specific areas where they need improvement (2-3 sentences)

4. STRENGTHS_ANALYSIS: Their key strengths and what they excel at (2-3 sentences)

5. IMPROVEMENT_RECOMMENDATIONS: Specific, actionable recommendations for growth (3-4 sentences)

6. SKILL_LEVEL_ASSESSMENT: Overall skill level and readiness for advanced topics (2-3 sentences)

7. EXECUTIVE_SUMMARY: A comprehensive 4-5 sentence summary suitable for managers or educators

Format your response as a JSON object with these exact keys.
"""

        try:
            response = self.groq_client.generate_response(
                system_prompt, 
                user_prompt, 
                max_tokens=1500,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            if not response:
                return self._generate_fallback_summary(session_data, performance_data)
            
            # Try to parse as JSON
            try:
                summary_data = json.loads(response.strip())
                return summary_data
            except json.JSONDecodeError:
                # If not valid JSON, create structured response from text
                return {
                    "cognitive_profile": "Analysis generated but format parsing failed.",
                    "learning_style": "Unable to determine from current data.",
                    "knowledge_gaps": "Requires further assessment.",
                    "strengths_analysis": "Multiple areas showing potential.",
                    "improvement_recommendations": "Continue practicing across all topics.",
                    "skill_level_assessment": "Developing proficiency level.",
                    "executive_summary": response[:500] + "..." if len(response) > 500 else response
                }
                
        except Exception as e:
            print(f"Error generating AI summary: {str(e)}")
            return self._generate_fallback_summary(session_data, performance_data)
    
    def _generate_fallback_summary(self, session_data: Dict, performance_data: Dict) -> Dict[str, str]:
        """Generate a basic summary when AI analysis fails."""
        accuracy = performance_data.get('accuracy', 0)
        total_questions = performance_data.get('total_responses', 0)
        correct_answers = performance_data.get('correct_responses', 0)
        topics = session_data.get('topics_asked', [])
        
        return {
            "cognitive_profile": f"Completed {total_questions} questions with {accuracy:.1%} accuracy, showing systematic approach to problem-solving.",
            "learning_style": "Demonstrates engagement with multiple topic areas, suggesting adaptable learning approach.",
            "knowledge_gaps": f"Areas requiring focus based on {total_questions - correct_answers} incorrect responses across various topics.",
            "strengths_analysis": f"Successfully answered {correct_answers} questions, showing competency in {len(topics)} different topic areas.",
            "improvement_recommendations": "Continue practicing across all topic areas with focus on accuracy and consistency. Consider targeted review of challenging concepts.",
            "skill_level_assessment": f"Current performance level shows {'strong' if accuracy > 0.7 else 'developing'} foundational knowledge with room for growth.",
            "executive_summary": f"User completed comprehensive assessment covering {len(topics)} topics with {accuracy:.1%} accuracy. Shows {'strong' if accuracy > 0.7 else 'developing'} foundational skills and systematic problem-solving approach. Recommended for {'advanced' if accuracy > 0.8 else 'continued foundational'} training programs."
        }
    
    def save_user_summary(self, session_data: Dict, session_responses: List[Dict]) -> Dict[str, any]:
        """Generate and save comprehensive user summary to database."""
        
        # Ensure table exists
        self.create_user_summaries_table()
        
        print("🧠 Generating comprehensive user summary...")
        
        # Generate AI analysis
        ai_summary = self.generate_comprehensive_summary(session_data, session_responses)
        
        # Extract performance data
        performance_data = session_data.get('performance_summary', {})
        
        # Prepare topic analysis
        topic_breakdown = performance_data.get('topic_breakdown', [])
        topics_covered = [t['topic'] for t in topic_breakdown]
        strong_topics = [t['topic'] for t in topic_breakdown if t.get('accuracy', 0) >= 0.7]
        weak_topics = [t['topic'] for t in topic_breakdown if t.get('accuracy', 0) < 0.5]
        
        # Calculate assessment duration (approximate)
        assessment_duration = session_data.get('questions_asked', 0) * 60  # Assume 1 minute per question
        
        try:
            connection = get_db_connection()
            connection.autocommit = True
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_summaries (
                        session_id, user_id, total_questions, correct_answers, accuracy,
                        topics_covered, strong_topics, weak_topics, topic_breakdown,
                        cognitive_profile, learning_style, knowledge_gaps, strengths_analysis,
                        improvement_recommendations, skill_level_assessment, executive_summary,
                        detailed_analysis, node_history, assessment_duration
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    ) RETURNING id
                """, (
                    session_data.get('session_id'),
                    session_data.get('user_id'),
                    performance_data.get('total_responses', 0),
                    performance_data.get('correct_responses', 0),
                    performance_data.get('accuracy', 0),
                    topics_covered,
                    strong_topics,
                    weak_topics,
                    json.dumps(topic_breakdown),
                    ai_summary.get('cognitive_profile', ''),
                    ai_summary.get('learning_style', ''),
                    ai_summary.get('knowledge_gaps', ''),
                    ai_summary.get('strengths_analysis', ''),
                    ai_summary.get('improvement_recommendations', ''),
                    ai_summary.get('skill_level_assessment', ''),
                    ai_summary.get('executive_summary', ''),
                    json.dumps(ai_summary),
                    session_data.get('node_history', []),
                    assessment_duration
                ))
                
                summary_id = cursor.fetchone()['id']
            
            connection.close()
            
            print(f"✅ User summary saved with ID: {summary_id}")
            
            return {
                "success": True,
                "message": "User summary generated and saved successfully",
                "summary_id": summary_id,
                "ai_summary": ai_summary
            }
            
        except Exception as e:
            print(f"❌ Error saving user summary: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to save user summary: {str(e)}",
                "ai_summary": ai_summary
            }
    
    def get_user_summary(self, session_id: str) -> Optional[Dict]:
        """Retrieve user summary by session ID."""
        try:
            connection = get_db_connection()
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM user_summaries 
                    WHERE session_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (session_id,))
                
                result = cursor.fetchone()
            
            connection.close()
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            print(f"Error retrieving user summary: {str(e)}")
            return None

# Global instance
user_summary_service = UserSummaryService()
