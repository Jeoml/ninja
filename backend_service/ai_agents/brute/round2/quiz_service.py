"""
Round 2 Quiz Service.
Tests depth of knowledge on strong topics from Round 1 using medium difficulty questions.
"""
from typing import Dict, List, Optional
import random
from .database_service import Round2DatabaseService
from .catalog_service import Round2CatalogService, Round2TopicStatus

class Round2QuizService:
    """Main service for Round 2 quiz functionality."""
    
    def __init__(self):
        self.db_service = Round2DatabaseService()
        self.catalog_service: Optional[Round2CatalogService] = None
        self.current_question: Optional[Dict] = None
        self.questions_pool: List[Dict] = []
        self.questions_asked_count: int = 0
        self.max_questions: int = 10
        self.is_quiz_active: bool = False
        self.round1_strong_topics: List[str] = []
    
    def start_quiz_session(self, max_questions: int = 10, round1_strong_topics: List[str] = None, user_email: str = None) -> Dict:
        """Start a Round 2 quiz session."""
        self.max_questions = max_questions
        self.questions_asked_count = 0
        self.is_quiz_active = True
        self.round1_strong_topics = round1_strong_topics or []
        
        # Initialize catalog service with Round 1 context
        self.catalog_service = Round2CatalogService(self.round1_strong_topics)
        
        # Determine question selection strategy
        strategy_info = self._determine_question_strategy()
        
        # Get questions based on strategy
        if strategy_info["strategy"] == "test_round1_strengths":
            # Test depth on Round 1 strong topics
            self.questions_pool = self.db_service.get_diverse_medium_questions(
                max_questions * 2,  # Get extra for variety
                preferred_topics=self.round1_strong_topics
            )
            
        elif strategy_info["strategy"] == "explore_medium_topics":
            # User doesn't have enough strong topics, explore medium questions
            self.questions_pool = self.db_service.get_random_medium_questions(max_questions * 2)
        
        if not self.questions_pool:
            return {
                "success": False,
                "message": "No medium difficulty questions available",
                "data": None
            }
        
        # Get database stats
        stats = self.db_service.get_medium_database_stats()
        
        return {
            "success": True,
            "message": f"Round 2 started! Testing {strategy_info['description']}",
            "data": {
                "max_questions": max_questions,
                "available_questions": len(self.questions_pool),
                "strategy": strategy_info["strategy"],
                "strategy_description": strategy_info["description"],
                "round1_strong_topics": self.round1_strong_topics,
                "database_stats": stats,
                "user_email": user_email,
                "session_id": f"round2_{random.randint(1000, 9999)}"
            }
        }
    
    def _determine_question_strategy(self) -> Dict:
        """Determine the question selection strategy based on Round 1 results."""
        if len(self.round1_strong_topics) >= 2:
            # User has enough strong topics from Round 1, test depth
            available_topics_with_medium = []
            for topic in self.round1_strong_topics:
                if self.db_service.check_topic_has_medium_questions(topic):
                    available_topics_with_medium.append(topic)
            
            if available_topics_with_medium:
                return {
                    "strategy": "test_round1_strengths",
                    "description": f"depth on your strong topics: {', '.join(available_topics_with_medium)}"
                }
        
        # Fallback: explore medium topics to find strengths
        return {
            "strategy": "explore_medium_topics", 
            "description": "medium difficulty questions to identify your strong areas"
        }
    
    def get_next_question(self) -> Dict:
        """Get the next question for Round 2."""
        if not self.is_quiz_active:
            return {
                "success": False,
                "message": "No active Round 2 quiz session. Please start a quiz first.",
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
            "message": f"Round 2 Question {self.questions_asked_count} of {self.max_questions}",
            "data": {
                "question_id": next_question["id"],
                "question": next_question["question"],
                "options": next_question["options"],
                "topic": next_question["topic"],
                "difficulty": "medium",
                "question_number": self.questions_asked_count,
                "total_questions": self.max_questions,
                "progress": (self.questions_asked_count / self.max_questions) * 100,
                "from_round1_strength": next_question["topic"] in self.round1_strong_topics
            }
        }
    
    def submit_answer(self, user_answer: str) -> Dict:
        """Submit answer for current Round 2 question."""
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
            "difficulty": "medium",
            "from_round1_strength": self.current_question["topic"] in self.round1_strong_topics,
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
    
    def _select_next_question(self) -> Optional[Dict]:
        """Intelligently select the next Round 2 question."""
        if not self.questions_pool:
            return None
        
        # Get topics we should prioritize
        available_topics = list(set(q["topic"] for q in self.questions_pool))
        recommended_topics = self.catalog_service.get_recommended_topics_for_next_questions(available_topics)
        
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
        """End Round 2 quiz session and return final results."""
        self.is_quiz_active = False
        final_results = self.catalog_service.get_performance_summary()
        
        return {
            "success": True,
            "message": f"Round 2 completed! You answered {self.questions_asked_count} medium difficulty questions.",
            "data": {
                "quiz_completed": True,
                "questions_answered": self.questions_asked_count,
                "final_results": final_results,
                "recommendations": self._generate_round2_recommendations(final_results)
            }
        }
    
    def _get_answer_explanation(self, is_correct: bool, topic: str) -> str:
        """Generate explanation for Round 2 answer."""
        if is_correct:
            return f"✅ Excellent! You're showing strong depth in {topic} at medium difficulty."
        else:
            return f"❌ Not quite. This medium-level {topic} question shows an area to strengthen."
    
    def _generate_round2_recommendations(self, results: Dict) -> Dict:
        """Generate recommendations based on Round 2 performance."""
        expert_topics = results["expert_topics"]
        proficient_topics = results["proficient_topics"]
        crazy_good_topics = results["crazy_good_topics"]
        accuracy = results["accuracy"]
        
        recommendations = {
            "overall_performance": "excellent" if accuracy >= 0.8 else "good" if accuracy >= 0.6 else "developing",
            "expert_topics": expert_topics,
            "proficient_topics": proficient_topics,
            "crazy_good_topics": crazy_good_topics,
            "next_steps": []
        }
        
        if len(expert_topics) > 0:
            recommendations["next_steps"].append(f"🌟 You're an expert in: {', '.join(expert_topics)}")
        
        if len(proficient_topics) > 0:
            recommendations["next_steps"].append(f"💪 You're proficient in: {', '.join(proficient_topics)}")
        
        if len(crazy_good_topics) >= 3:
            recommendations["next_steps"].append("🚀 Ready for Round 3 - Advanced level questions!")
        elif len(crazy_good_topics) >= 1:
            recommendations["next_steps"].append("📈 Good progress! Continue building depth in your strong areas.")
        else:
            recommendations["next_steps"].append("📚 Focus on strengthening your foundational knowledge before advancing.")
        
        return recommendations
    
    def get_current_performance(self) -> Dict:
        """Get current Round 2 performance summary."""
        if not self.catalog_service:
            return {
                "success": False,
                "message": "No active quiz session",
                "data": None
            }
        
        return {
            "success": True,
            "message": "Current Round 2 performance retrieved",
            "data": self.catalog_service.get_performance_summary()
        }
    
    def get_quiz_status(self) -> Dict:
        """Get current Round 2 quiz status."""
        return {
            "success": True,
            "message": "Round 2 quiz status retrieved",
            "data": {
                "is_active": self.is_quiz_active,
                "questions_asked": self.questions_asked_count,
                "max_questions": self.max_questions,
                "has_current_question": self.current_question is not None,
                "current_question_id": self.current_question["id"] if self.current_question else None,
                "round1_strong_topics": self.round1_strong_topics
            }
        }
