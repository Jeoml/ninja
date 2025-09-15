"""
Catalog service for tracking user performance in Round 2.
Focuses on identifying topics where user has deep/expert knowledge.
"""
from typing import Dict, List, Set
from dataclasses import dataclass, field
from enum import Enum

class Round2TopicStatus(Enum):
    """Status of a topic based on Round 2 performance."""
    EXPERT = "expert"           # High performance on medium questions
    PROFICIENT = "proficient"   # Good performance on medium questions  
    DEVELOPING = "developing"   # Mixed performance on medium questions
    STRUGGLING = "struggling"   # Poor performance on medium questions

@dataclass
class Round2TopicPerformance:
    """Performance data for a specific topic in Round 2."""
    topic: str
    correct_answers: int = 0
    incorrect_answers: int = 0
    questions_attempted: List[int] = field(default_factory=list)
    from_round1_strength: bool = False  # Was this a strong topic from Round 1?
    
    @property
    def total_attempts(self) -> int:
        return self.correct_answers + self.incorrect_answers
    
    @property
    def accuracy(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.correct_answers / self.total_attempts
    
    @property
    def status(self) -> Round2TopicStatus:
        """Determine topic status based on Round 2 medium-level performance."""
        if self.total_attempts == 0:
            return Round2TopicStatus.DEVELOPING
        
        accuracy = self.accuracy
        
        # Expert level: 80%+ accuracy on medium questions
        if accuracy >= 0.8:
            return Round2TopicStatus.EXPERT
        # Proficient level: 60-79% accuracy  
        elif accuracy >= 0.6:
            return Round2TopicStatus.PROFICIENT
        # Developing: 40-59% accuracy
        elif accuracy >= 0.4:
            return Round2TopicStatus.DEVELOPING
        # Struggling: <40% accuracy
        else:
            return Round2TopicStatus.STRUGGLING

class Round2CatalogService:
    """Service for managing Round 2 performance catalog."""
    
    def __init__(self, round1_strong_topics: List[str] = None):
        self.topic_performance: Dict[str, Round2TopicPerformance] = {}
        self.session_questions: List[Dict] = []
        self.round1_strong_topics = round1_strong_topics or []
        self.current_question_index: int = 0
    
    def record_answer(self, question: Dict, user_answer: str, is_correct: bool) -> None:
        """Record user's answer for a Round 2 question."""
        topic = question["topic"]
        question_id = question["id"]
        
        # Initialize topic performance if not exists
        if topic not in self.topic_performance:
            self.topic_performance[topic] = Round2TopicPerformance(
                topic=topic,
                from_round1_strength=(topic in self.round1_strong_topics)
            )
        
        # Update performance
        performance = self.topic_performance[topic]
        
        if is_correct:
            performance.correct_answers += 1
        else:
            performance.incorrect_answers += 1
        
        # Track question ID to avoid duplicates
        if question_id not in performance.questions_attempted:
            performance.questions_attempted.append(question_id)
        
        # Store the question and answer in session
        self.session_questions.append({
            "question": question,
            "user_answer": user_answer,
            "correct_answer": question["correct_answer"],
            "is_correct": is_correct,
            "topic": topic,
            "difficulty": "medium",
            "from_round1_strength": topic in self.round1_strong_topics
        })
    
    def get_expert_topics(self) -> List[str]:
        """Get list of expert-level topics (80%+ accuracy on medium questions)."""
        return [
            topic for topic, performance in self.topic_performance.items()
            if performance.status == Round2TopicStatus.EXPERT
        ]
    
    def get_proficient_topics(self) -> List[str]:
        """Get list of proficient topics (60-79% accuracy)."""
        return [
            topic for topic, performance in self.topic_performance.items()
            if performance.status == Round2TopicStatus.PROFICIENT
        ]
    
    def get_developing_topics(self) -> List[str]:
        """Get list of developing topics (40-59% accuracy)."""
        return [
            topic for topic, performance in self.topic_performance.items()
            if performance.status == Round2TopicStatus.DEVELOPING
        ]
    
    def get_struggling_topics(self) -> List[str]:
        """Get list of struggling topics (<40% accuracy)."""
        return [
            topic for topic, performance in self.topic_performance.items()
            if performance.status == Round2TopicStatus.STRUGGLING
        ]
    
    def get_crazy_good_topics(self) -> List[str]:
        """Get topics where user is 'crazy good' (expert + proficient)."""
        expert = self.get_expert_topics()
        proficient = self.get_proficient_topics()
        return expert + proficient
    
    def get_performance_summary(self) -> Dict:
        """Get overall Round 2 performance summary."""
        if not self.topic_performance:
            return {
                "total_questions": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "accuracy": 0.0,
                "topics_attempted": 0,
                "expert_topics": [],
                "proficient_topics": [],
                "developing_topics": [],
                "struggling_topics": [],
                "crazy_good_topics": [],
                "round1_progression": {},
                "topic_breakdown": {}
            }
        
        total_correct = sum(p.correct_answers for p in self.topic_performance.values())
        total_incorrect = sum(p.incorrect_answers for p in self.topic_performance.values())
        total_questions = total_correct + total_incorrect
        
        accuracy = (total_correct / total_questions) if total_questions > 0 else 0.0
        
        # Analyze Round 1 to Round 2 progression
        round1_progression = {}
        for topic, performance in self.topic_performance.items():
            if performance.from_round1_strength:
                round1_progression[topic] = {
                    "was_round1_strength": True,
                    "round2_status": performance.status.value,
                    "maintained_strength": performance.status in [Round2TopicStatus.EXPERT, Round2TopicStatus.PROFICIENT]
                }
        
        # Topic breakdown
        topic_breakdown = {}
        for topic, performance in self.topic_performance.items():
            topic_breakdown[topic] = {
                "correct": performance.correct_answers,
                "incorrect": performance.incorrect_answers,
                "total": performance.total_attempts,
                "accuracy": performance.accuracy,
                "status": performance.status.value,
                "from_round1_strength": performance.from_round1_strength
            }
        
        return {
            "total_questions": total_questions,
            "correct_answers": total_correct,
            "incorrect_answers": total_incorrect,
            "accuracy": accuracy,
            "topics_attempted": len(self.topic_performance),
            "expert_topics": self.get_expert_topics(),
            "proficient_topics": self.get_proficient_topics(),
            "developing_topics": self.get_developing_topics(),
            "struggling_topics": self.get_struggling_topics(),
            "crazy_good_topics": self.get_crazy_good_topics(),
            "round1_progression": round1_progression,
            "topic_breakdown": topic_breakdown
        }
    
    def get_recommended_topics_for_next_questions(self, available_topics: List[str]) -> List[str]:
        """Get recommended topics for next questions in Round 2."""
        # Priority 1: Round 1 strong topics that haven't been tested yet
        untested_round1_strengths = [
            topic for topic in self.round1_strong_topics 
            if topic not in self.topic_performance and topic in available_topics
        ]
        
        if untested_round1_strengths:
            return untested_round1_strengths
        
        # Priority 2: Topics that need more data (less than 3 attempts)
        needs_more_data = [
            topic for topic, performance in self.topic_performance.items()
            if performance.total_attempts < 3 and topic in available_topics
        ]
        
        if needs_more_data:
            return needs_more_data
        
        # Priority 3: Any available topics
        return [topic for topic in available_topics if topic not in self.topic_performance]
    
    def should_continue_testing_topic(self, topic: str) -> bool:
        """Determine if we should continue testing a topic."""
        if topic not in self.topic_performance:
            return True
        
        performance = self.topic_performance[topic]
        
        # Continue testing if we don't have enough data yet
        if performance.total_attempts < 2:
            return True
        
        # If topic is clearly expert level with multiple attempts, we can stop
        if performance.status == Round2TopicStatus.EXPERT and performance.total_attempts >= 3:
            return False
        
        # Continue testing struggling topics to confirm (up to 4 attempts)
        if performance.status == Round2TopicStatus.STRUGGLING and performance.total_attempts >= 4:
            return False
        
        return True
    
    def reset_session(self) -> None:
        """Reset the current session while keeping performance data."""
        self.session_questions = []
        self.current_question_index = 0
    
    def reset_all(self) -> None:
        """Reset all data."""
        self.topic_performance = {}
        self.session_questions = []
        self.current_question_index = 0
