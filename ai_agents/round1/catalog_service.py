"""
Catalog service for tracking user performance by topic in Round 1.
"""
from typing import Dict, List, Set
from dataclasses import dataclass, field
from enum import Enum

class TopicStatus(Enum):
    """Status of a topic based on user performance."""
    SOLVED = "solved"
    UNSOLVED = "unsolved"
    MIXED = "mixed"  # Has both correct and incorrect answers

@dataclass
class TopicPerformance:
    """Performance data for a specific topic."""
    topic: str
    correct_answers: int = 0
    incorrect_answers: int = 0
    questions_attempted: List[int] = field(default_factory=list)
    
    @property
    def total_attempts(self) -> int:
        return self.correct_answers + self.incorrect_answers
    
    @property
    def accuracy(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.correct_answers / self.total_attempts
    
    @property
    def status(self) -> TopicStatus:
        """Determine topic status based on performance."""
        if self.correct_answers > 0 and self.incorrect_answers == 0:
            return TopicStatus.SOLVED
        elif self.correct_answers == 0 and self.incorrect_answers > 0:
            return TopicStatus.UNSOLVED
        elif self.correct_answers > 0 and self.incorrect_answers > 0:
            # As per requirement: if same topic has been solved and unsolved, keep it in solved
            return TopicStatus.SOLVED
        else:
            return TopicStatus.UNSOLVED

class CatalogService:
    """Service for managing user performance catalog."""
    
    def __init__(self):
        self.topic_performance: Dict[str, TopicPerformance] = {}
        self.session_questions: List[Dict] = []  # Questions asked in current session
        self.current_question_index: int = 0
    
    def record_answer(self, question: Dict, user_answer: str, is_correct: bool) -> None:
        """Record user's answer for a question."""
        topic = question["topic"]
        question_id = question["id"]
        
        # Initialize topic performance if not exists
        if topic not in self.topic_performance:
            self.topic_performance[topic] = TopicPerformance(topic=topic)
        
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
            "topic": topic
        })
    
    def get_topic_status(self, topic: str) -> TopicStatus:
        """Get the current status of a topic."""
        if topic not in self.topic_performance:
            return TopicStatus.UNSOLVED
        
        return self.topic_performance[topic].status
    
    def get_solved_topics(self) -> List[str]:
        """Get list of solved topics."""
        return [
            topic for topic, performance in self.topic_performance.items()
            if performance.status == TopicStatus.SOLVED
        ]
    
    def get_unsolved_topics(self) -> List[str]:
        """Get list of unsolved topics."""
        return [
            topic for topic, performance in self.topic_performance.items()
            if performance.status == TopicStatus.UNSOLVED
        ]
    
    def get_attempted_topics(self) -> Set[str]:
        """Get set of topics that have been attempted."""
        return set(self.topic_performance.keys())
    
    def get_performance_summary(self) -> Dict:
        """Get overall performance summary."""
        if not self.topic_performance:
            return {
                "total_questions": 0,
                "correct_answers": 0,
                "incorrect_answers": 0,
                "accuracy": 0.0,
                "topics_attempted": 0,
                "solved_topics": [],
                "unsolved_topics": [],
                "topic_breakdown": {}
            }
        
        total_correct = sum(p.correct_answers for p in self.topic_performance.values())
        total_incorrect = sum(p.incorrect_answers for p in self.topic_performance.values())
        total_questions = total_correct + total_incorrect
        
        accuracy = (total_correct / total_questions) if total_questions > 0 else 0.0
        
        # Topic breakdown
        topic_breakdown = {}
        for topic, performance in self.topic_performance.items():
            topic_breakdown[topic] = {
                "correct": performance.correct_answers,
                "incorrect": performance.incorrect_answers,
                "total": performance.total_attempts,
                "accuracy": performance.accuracy,
                "status": performance.status.value
            }
        
        return {
            "total_questions": total_questions,
            "correct_answers": total_correct,
            "incorrect_answers": total_incorrect,
            "accuracy": accuracy,
            "topics_attempted": len(self.topic_performance),
            "solved_topics": self.get_solved_topics(),
            "unsolved_topics": self.get_unsolved_topics(),
            "topic_breakdown": topic_breakdown
        }
    
    def get_session_history(self) -> List[Dict]:
        """Get the history of questions asked in current session."""
        return self.session_questions.copy()
    
    def should_ask_from_topic(self, topic: str) -> bool:
        """Determine if we should ask more questions from this topic."""
        # Prioritize topics that haven't been attempted yet
        if topic not in self.topic_performance:
            return True
        
        performance = self.topic_performance[topic]
        
        # If topic is already solved with high confidence, deprioritize
        if performance.status == TopicStatus.SOLVED and performance.total_attempts >= 2:
            return False
        
        # If topic is unsolved, we might want to give another chance
        if performance.status == TopicStatus.UNSOLVED and performance.total_attempts < 3:
            return True
        
        return True
    
    def get_recommended_topics(self, available_topics: List[str]) -> List[str]:
        """Get recommended topics to ask questions from, prioritized."""
        unattempted = [t for t in available_topics if t not in self.topic_performance]
        
        # Priority 1: Unattempted topics
        if unattempted:
            return unattempted
        
        # Priority 2: Topics that need more attempts
        needs_more_attempts = [
            topic for topic in available_topics
            if self.should_ask_from_topic(topic)
        ]
        
        return needs_more_attempts if needs_more_attempts else available_topics
    
    def reset_session(self) -> None:
        """Reset the current session while keeping performance data."""
        self.session_questions = []
        self.current_question_index = 0
    
    def reset_all(self) -> None:
        """Reset all data."""
        self.topic_performance = {}
        self.session_questions = []
        self.current_question_index = 0
