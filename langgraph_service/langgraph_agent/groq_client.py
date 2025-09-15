"""
Groq API client for Qwen 3-32B model integration.
"""
from groq import Groq
from typing import Dict, Any, Optional
import json
import os

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Get from environment variable
MODEL_NAME = "llama-3.1-70b-versatile"  # Updated to current available model

class GroqClient:
    """Client for interacting with Groq API."""
    
    def __init__(self):
        if not GROQ_API_KEY:
            print("⚠️  Warning: GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    
    def generate_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Optional[str]:
        """Generate a response using the Groq API."""
        if not self.client:
            return "AI service temporarily unavailable - please check GROQ_API_KEY configuration."
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=MODEL_NAME,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating response with Groq: {str(e)}")
            return None
    
    def ask_question_to_user(self, question_data: Dict) -> str:
        """Present a question to the user and get their response."""
        system_prompt = """You are a quiz assistant. Present the given question to the user in a clear, engaging way. 
        Ask them to choose from the given options (A, B, C, or D). Be encouraging and supportive."""
        
        user_prompt = f"""
        Please present this question to the user:
        
        Question: {question_data['question']}
        
        Options:
        A) {question_data['options']['A']}
        B) {question_data['options']['B']}
        C) {question_data['options']['C']}
        D) {question_data['options']['D']}
        
        Topic: {question_data['topic']}
        Difficulty: {question_data['difficulty']}
        
        Ask the user to choose their answer (A, B, C, or D).
        """
        
        return self.generate_response(system_prompt, user_prompt)
    
    def provide_feedback(self, is_correct: bool, correct_answer: str, topic: str) -> str:
        """Provide feedback on the user's answer."""
        system_prompt = """You are a supportive quiz tutor conducting an interview. Provide encouraging feedback to the user about their answer.
        Be positive and constructive, whether they got it right or wrong. NEVER reveal the correct answer - this is an interview/assessment."""
        
        if is_correct:
            user_prompt = f"The user got the answer correct! This was a {topic} question. Provide positive encouragement without revealing the correct answer."
        else:
            user_prompt = f"The user got the answer wrong. This was a {topic} question. Provide supportive feedback and encouragement to keep trying, but do NOT reveal the correct answer since this is an assessment."
        
        return self.generate_response(system_prompt, user_prompt)
    
    def generate_performance_summary(self, performance_data: Dict) -> str:
        """Generate a comprehensive performance summary."""
        system_prompt = """You are an educational assessment expert. Analyze the user's quiz performance data and provide a comprehensive, encouraging summary with insights and recommendations."""
        
        user_prompt = f"""
        Analyze this quiz performance data and provide a detailed summary:
        
        Performance Data:
        {json.dumps(performance_data, indent=2)}
        
        Please provide:
        1. Overall performance assessment
        2. Strengths and areas for improvement
        3. Topic-wise analysis
        4. Recommendations for further study
        5. Encouraging conclusion
        """
        
        return self.generate_response(system_prompt, user_prompt, max_tokens=1500)

# Global client instance
groq_client = GroqClient()
