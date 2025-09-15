"""
Test script for the LangGraph Quiz Agent.
"""
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ai_agents.langgraph_agent.quiz_agent import quiz_agent

def test_agent():
    """Test the quiz agent."""
    print("🧪 Testing LangGraph Quiz Agent...")
    
    try:
        # Run a test quiz
        result = quiz_agent.run_quiz(user_id="test_user_123")
        
        print("✅ Agent test completed successfully!")
        print(f"📊 Results: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)
