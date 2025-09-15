"""
Pydantic models for Round 2 quiz API.
"""
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional, Any
from enum import Enum

class AnswerChoice(str, Enum):
    """Valid answer choices."""
    A = "A"
    B = "B" 
    C = "C"
    D = "D"

class Round2StartRequest(BaseModel):
    """Request to start a Round 2 quiz session."""
    max_questions: Optional[int] = 10
    round1_strong_topics: Optional[List[str]] = []
    user_email: Optional[str] = None

class Round2SubmitAnswerRequest(BaseModel):
    """Request to submit an answer in Round 2."""
    answer: AnswerChoice

class Round2Response(BaseModel):
    """Standard response for Round 2 quiz operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class Round2QuestionData(BaseModel):
    """Round 2 question data structure."""
    question_id: int
    question: str
    options: Dict[str, str]  # {"A": "option1", "B": "option2", ...}
    topic: str
    difficulty: str  # "medium"
    question_number: int
    total_questions: int
    progress: float
    from_round1_strength: bool

class Round2AnswerResult(BaseModel):
    """Result of submitting an answer in Round 2."""
    is_correct: bool
    user_answer: str
    correct_answer: str
    correct_option: str
    topic: str
    difficulty: str
    from_round1_strength: bool
    explanation: str
    quiz_completed: bool
    questions_remaining: Optional[int] = None
    final_results: Optional[Dict] = None

class Round2PerformanceSummary(BaseModel):
    """Round 2 user performance summary."""
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    accuracy: float
    topics_attempted: int
    expert_topics: List[str]        # 80%+ accuracy (crazy good)
    proficient_topics: List[str]    # 60-79% accuracy (crazy good)
    developing_topics: List[str]    # 40-59% accuracy
    struggling_topics: List[str]    # <40% accuracy
    crazy_good_topics: List[str]    # expert + proficient combined
    round1_progression: Dict[str, Dict]
    topic_breakdown: Dict[str, Dict]

class Round2QuizStatus(BaseModel):
    """Current Round 2 quiz status."""
    is_active: bool
    questions_asked: int
    max_questions: int
    has_current_question: bool
    current_question_id: Optional[int] = None
    round1_strong_topics: List[str]

class Round2DatabaseStats(BaseModel):
    """Round 2 database statistics."""
    total_medium_questions: int
    available_medium_topics: int
    topic_distribution: List[Dict[str, Any]]

class Round1ResultsInput(BaseModel):
    """Input model for Round 1 results to inform Round 2 strategy."""
    solved_topics: List[str]
    accuracy: float
    topics_attempted: int
    topic_breakdown: Dict[str, Dict]

class UserProgressionData(BaseModel):
    """Model for tracking user progression from Round 1 to Round 2."""
    user_email: str
    round1_completed: bool
    round1_strong_topics: List[str]
    round1_accuracy: float
    round2_eligible: bool
    recommended_round2_strategy: str
