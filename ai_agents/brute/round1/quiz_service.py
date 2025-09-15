"""
Main quiz service for Round 1.
Orchestrates the quiz flow, question selection, and user interaction.
"""
from typing import Dict, List, Optional, Tuple
import random
from .database_service import DatabaseService
from .catalog_service import CatalogService, TopicStatus

class QuizService:
    """Main service for Round 1 quiz functionality."""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.catalog_service = CatalogService()
        self.current_question: Optional[Dict] = None
        self.questions_pool: List[Dict] = []
        self.questions_asked_count: int = 0
        self.max_questions: int = 15
        self.is_quiz_active: bool = False
    
    def start_quiz_session(self, max_questions: int = 15) -> Dict:
        """Start a new quiz session."""
        self.max_questions = max_questions
        self.questions_asked_count = 0
        self.is_quiz_active = True
        
        # Get diverse questions from database
        self.questions_pool = self.db_service.get_diverse_easy_questions(max_questions * 2)  # Get extra for variety
        
        if not self.questions_pool:
            return {
                "success": False,
                "message": "No questions available in database",
                "data": None
            }
        
        # Get database stats
        stats = self.db_service.get_database_stats()
        
        return {
            "success": True,
            "message": f"Quiz session started! You'll be asked up to {max_questions} questions.",
            "data": {
                "max_questions": max_questions,
                "available_questions": len(self.questions_pool),
                "database_stats": stats,
                "session_id": f"round1_{random.randint(1000, 9999)}"
            }
        }
    
    def get_next_question(self) -> Dict:
        """Get the next question for the user."""
        if not self.is_quiz_active:
            return {
                "success": False,
                "message": "No active quiz session. Please start a quiz first.",
                "data": None
            }
        
        if self.questions_asked_count >= self.max_questions:
            return self._end_quiz_session()
        
        # Select next question intelligently
        next_question = self._select_next_question()
        
        if not next_question:
            return self._end_quiz_session()
        
        self.current_question = next_question
        self.questions_asked_count += 1
        
        # Format question for API response
        return {
            "success": True,
            "message": f"Question {self.questions_asked_count} of {self.max_questions}",
            "data": {
                "question_id": next_question["id"],
                "question": next_question["question"],
                "options": next_question["options"],
                "topic": next_question["topic"],
                "question_number": self.questions_asked_count,
                "total_questions": self.max_questions,
                "progress": (self.questions_asked_count / self.max_questions) * 100
            }
        }
    
    def submit_answer(self, user_answer: str) -> Dict:
        """Submit answer for current question."""
        if not self.is_quiz_active or not self.current_question:
            return {
                "success": False,
                "message": "No active question to answer",
                "data": None
            }
        
        # Validate answer format
        if user_answer.upper() not in ['A', 'B', 'C', 'D']:
            return {
                "success": False,
                "message": "Invalid answer format. Please choose A, B, C, or D.",
                "data": None
            }
        
        user_answer = user_answer.upper()
        correct_answer = self.current_question["correct_answer"]
        is_correct = user_answer == correct_answer
        
        # Record the answer in catalog
        self.catalog_service.record_answer(
            self.current_question,
            user_answer,
            is_correct
        )
        
        # Prepare response
        response_data = {
            "is_correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "correct_option": self.current_question["options"][correct_answer],
            "topic": self.current_question["topic"],
            "explanation": self._get_answer_explanation(is_correct, self.current_question["topic"])
        }
        
        # Check if quiz should end
        if self.questions_asked_count >= self.max_questions:
            response_data["quiz_completed"] = True
            response_data["final_results"] = self.catalog_service.get_performance_summary()
            self.is_quiz_active = False
        else:
            response_data["quiz_completed"] = False
            response_data["questions_remaining"] = self.max_questions - self.questions_asked_count
        
        # Clear current question
        self.current_question = None
        
        return {
            "success": True,
            "message": "Answer submitted successfully",
            "data": response_data
        }
    
    def get_current_performance(self) -> Dict:
        """Get current performance summary."""
        return {
            "success": True,
            "message": "Current performance retrieved",
            "data": self.catalog_service.get_performance_summary()
        }
    
    def get_quiz_status(self) -> Dict:
        """Get current quiz status."""
        return {
            "success": True,
            "message": "Quiz status retrieved",
            "data": {
                "is_active": self.is_quiz_active,
                "questions_asked": self.questions_asked_count,
                "max_questions": self.max_questions,
                "has_current_question": self.current_question is not None,
                "current_question_id": self.current_question["id"] if self.current_question else None
            }
        }
    
    def end_quiz_session(self) -> Dict:
        """Manually end the current quiz session."""
        if not self.is_quiz_active:
            return {
                "success": False,
                "message": "No active quiz session to end",
                "data": None
            }
        
        return self._end_quiz_session()
    
    def _select_next_question(self) -> Optional[Dict]:
        """Intelligently select the next question based on performance."""
        if not self.questions_pool:
            return None
        
        # Get topics we haven't fully explored
        attempted_topics = self.catalog_service.get_attempted_topics()
        available_topics = list(set(q["topic"] for q in self.questions_pool))
        
        # Get recommended topics
        recommended_topics = self.catalog_service.get_recommended_topics(available_topics)
        
        # Filter questions by recommended topics
        preferred_questions = [
            q for q in self.questions_pool
            if q["topic"] in recommended_topics and q["id"] != (self.current_question["id"] if self.current_question else -1)
        ]
        
        # If no preferred questions, use any available
        if not preferred_questions:
            preferred_questions = [
                q for q in self.questions_pool
                if q["id"] != (self.current_question["id"] if self.current_question else -1)
            ]
        
        if not preferred_questions:
            return None
        
        # Select randomly from preferred questions
        selected_question = random.choice(preferred_questions)
        
        # Remove from pool to avoid repetition
        self.questions_pool = [q for q in self.questions_pool if q["id"] != selected_question["id"]]
        
        return selected_question
    
    def _end_quiz_session(self) -> Dict:
        """End the quiz session and return final results."""
        self.is_quiz_active = False
        final_results = self.catalog_service.get_performance_summary()
        session_history = self.catalog_service.get_session_history()
        
        return {
            "success": True,
            "message": f"Quiz completed! You answered {self.questions_asked_count} questions.",
            "data": {
                "quiz_completed": True,
                "questions_answered": self.questions_asked_count,
                "final_results": final_results,
                "session_history": session_history,
                "recommendations": self._generate_recommendations(final_results)
            }
        }
    
    def _get_answer_explanation(self, is_correct: bool, topic: str) -> str:
        """Generate explanation for the answer."""
        if is_correct:
            return f"✅ Correct! Great job on this {topic} question."
        else:
            return f"❌ Incorrect. This was a {topic} question - consider reviewing this topic."
    
    def _generate_recommendations(self, results: Dict) -> Dict:
        """Generate study recommendations based on performance."""
        solved_topics = results["solved_topics"]
        unsolved_topics = results["unsolved_topics"]
        accuracy = results["accuracy"]
        
        recommendations = {
            "overall_performance": "excellent" if accuracy >= 0.8 else "good" if accuracy >= 0.6 else "needs_improvement",
            "strong_topics": solved_topics,
            "topics_to_review": unsolved_topics,
            "next_steps": []
        }
        
        if accuracy >= 0.8:
            recommendations["next_steps"].append("You're doing great! Ready for more challenging questions.")
        elif accuracy >= 0.6:
            recommendations["next_steps"].append("Good progress! Focus on reviewing the topics you missed.")
        else:
            recommendations["next_steps"].append("Consider reviewing the basics for the topics you struggled with.")
        
        if unsolved_topics:
            recommendations["next_steps"].append(f"Pay special attention to: {', '.join(unsolved_topics[:3])}")
        
        return recommendations
    
    def reset_session(self) -> Dict:
        """Reset the current session."""
        self.is_quiz_active = False
        self.current_question = None
        self.questions_pool = []
        self.questions_asked_count = 0
        self.catalog_service.reset_session()
        
        return {
            "success": True,
            "message": "Session reset successfully",
            "data": None
        }
