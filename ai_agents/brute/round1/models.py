"""
Pydantic models for Round 1 quiz API.
"""
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from enum import Enum

class AnswerChoice(str, Enum):
    """Valid answer choices."""
    A = "A"
    B = "B" 
    C = "C"
    D = "D"

class QuizStartRequest(BaseModel):
    """Request to start a quiz session."""
    max_questions: Optional[int] = 15

class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer."""
    answer: AnswerChoice

class QuizResponse(BaseModel):
    """Standard response for quiz operations."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class QuestionData(BaseModel):
    """Question data structure."""
    question_id: int
    question: str
    options: Dict[str, str]  # {"A": "option1", "B": "option2", ...}
    topic: str
    question_number: int
    total_questions: int
    progress: float

class AnswerResult(BaseModel):
    """Result of submitting an answer."""
    is_correct: bool
    user_answer: str
    correct_answer: str
    correct_option: str
    topic: str
    explanation: str
    quiz_completed: bool
    questions_remaining: Optional[int] = None
    final_results: Optional[Dict] = None

class PerformanceSummary(BaseModel):
    """User performance summary."""
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    accuracy: float
    topics_attempted: int
    solved_topics: List[str]
    unsolved_topics: List[str]
    topic_breakdown: Dict[str, Dict]

class QuizStatus(BaseModel):
    """Current quiz status."""
    is_active: bool
    questions_asked: int
    max_questions: int
    has_current_question: bool
    current_question_id: Optional[int] = None

class DatabaseStats(BaseModel):
    """Database statistics."""
    total_questions: int
    easy_questions: int
    available_topics: int
    topic_distribution: List[Dict[str, Any]]
