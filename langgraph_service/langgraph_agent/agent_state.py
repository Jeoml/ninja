"""
State management for the LangGraph quiz agent.
"""
from typing import Dict, List, Optional, TypedDict
from datetime import datetime
import uuid

class AgentState(TypedDict):
    """State for the quiz agent."""
    session_id: str
    user_id: Optional[str]
    current_question: Optional[Dict]
    current_response: Optional[str]
    questions_asked: int
    total_questions_limit: int
    topics_asked: List[str]
    all_topics: List[str]
    current_topic: Optional[str]
    last_answer_correct: Optional[bool]
    responses_history: List[Dict]
    node_history: List[str]
    is_complete: bool
    performance_summary: Optional[Dict]
    user_summary: Optional[Dict]
    question_generation_result: Optional[Dict]
    user_summary_result: Optional[Dict]
    
def create_initial_state(user_id: Optional[str] = None) -> AgentState:
    """Create initial state for a new quiz session."""
    return AgentState(
        session_id=f"session_{uuid.uuid4().hex[:8]}",
        user_id=user_id,
        current_question=None,
        current_response=None,
        questions_asked=0,
        total_questions_limit=25,
        topics_asked=[],
        all_topics=[],
        current_topic=None,
        last_answer_correct=None,
        responses_history=[],
        node_history=[],
        is_complete=False,
        performance_summary=None,
        user_summary=None,
        question_generation_result=None,
        user_summary_result=None
    )
