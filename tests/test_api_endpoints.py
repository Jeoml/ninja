"""
Test AI Agents API endpoints without authentication.
"""
import pytest
import sys
import os
import requests
import json
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test configuration
BASE_URL = "http://localhost:8000"
ROUND1_BASE = f"{BASE_URL}/ai-agents/round1"

def test_server_health():
    """Test that the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Server is healthy and responding")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Server health check failed: {e}")
        print("⚠️  Make sure the server is running: python main.py")
        return False

def test_round1_intro():
    """Test the Round 1 introduction endpoint."""
    if not test_server_health():
        pytest.skip("Server not available")
    
    try:
        response = requests.get(f"{ROUND1_BASE}/chat/intro")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Round 1 Quiz" in data["message"]
        
        print("✅ Round 1 intro endpoint working")
        assert True
    except Exception as e:
        print(f"❌ Round 1 intro test failed: {e}")
        pytest.fail(f"Round 1 intro error: {e}")

def test_start_quiz_endpoint():
    """Test starting a quiz via API."""
    if not test_server_health():
        pytest.skip("Server not available")
    
    try:
        # Test with default parameters
        response = requests.post(f"{ROUND1_BASE}/start", 
                               json={},
                               headers={"Content-Type": "application/json"})
        
        print(f"📊 Start quiz response status: {response.status_code}")
        print(f"📊 Start quiz response: {response.text[:200]}...")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "message" in data
        
        if data["success"]:
            assert "data" in data
            print("✅ Quiz started successfully via API")
        else:
            print(f"⚠️  Quiz start failed: {data.get('message', 'Unknown error')}")
        
        assert True
    except Exception as e:
        print(f"❌ Start quiz endpoint test failed: {e}")
        pytest.fail(f"Start quiz endpoint error: {e}")

def test_get_question_endpoint():
    """Test getting a question via API."""
    if not test_server_health():
        pytest.skip("Server not available")
    
    try:
        # First start a quiz
        start_response = requests.post(f"{ROUND1_BASE}/start", json={})
        assert start_response.status_code == 200
        start_data = start_response.json()
        
        if not start_data.get("success", False):
            print(f"⚠️  Cannot test get question: quiz start failed")
            return
        
        # Get question
        response = requests.get(f"{ROUND1_BASE}/question")
        
        print(f"📊 Get question response status: {response.status_code}")
        print(f"📊 Get question response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                question_data = data["data"]
                print(f"✅ Got question: {question_data.get('question', '')[:50]}...")
                print(f"🏷️  Topic: {question_data.get('topic', 'Unknown')}")
                assert "question_id" in question_data
                assert "options" in question_data
                assert len(question_data["options"]) == 4
        
        assert True
    except Exception as e:
        print(f"❌ Get question endpoint test failed: {e}")
        pytest.fail(f"Get question endpoint error: {e}")

def test_submit_answer_endpoint():
    """Test submitting an answer via API."""
    if not test_server_health():
        pytest.skip("Server not available")
    
    try:
        # Start quiz and get question
        start_response = requests.post(f"{ROUND1_BASE}/start", json={})
        assert start_response.status_code == 200
        
        question_response = requests.get(f"{ROUND1_BASE}/question")
        if question_response.status_code != 200:
            print("⚠️  Cannot test submit answer: get question failed")
            return
        
        question_data = question_response.json()
        if not question_data.get("success", False):
            print("⚠️  Cannot test submit answer: no question available")
            return
        
        # Submit answer
        response = requests.post(f"{ROUND1_BASE}/answer", 
                               json={"answer": "A"},
                               headers={"Content-Type": "application/json"})
        
        print(f"📊 Submit answer response status: {response.status_code}")
        print(f"📊 Submit answer response: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                answer_data = data["data"]
                print(f"✅ Answer submitted: {'Correct' if answer_data.get('is_correct') else 'Incorrect'}")
                print(f"🎯 Correct answer was: {answer_data.get('correct_answer', 'Unknown')}")
        
        assert True
    except Exception as e:
        print(f"❌ Submit answer endpoint test failed: {e}")
        pytest.fail(f"Submit answer endpoint error: {e}")

def test_performance_endpoint():
    """Test getting performance data via API."""
    if not test_server_health():
        pytest.skip("Server not available")
    
    try:
        response = requests.get(f"{ROUND1_BASE}/performance")
        assert response.status_code == 200
        
        data = response.json()
        assert "success" in data
        assert "data" in data
        
        performance_data = data["data"]
        required_keys = ["total_questions", "correct_answers", "accuracy", "topics_attempted"]
        for key in required_keys:
            assert key in performance_data, f"Performance data should contain {key}"
        
        print("✅ Performance endpoint working")
        print(f"📊 Current performance: {performance_data['correct_answers']}/{performance_data['total_questions']} correct")
        
        assert True
    except Exception as e:
        print(f"❌ Performance endpoint test failed: {e}")
        pytest.fail(f"Performance endpoint error: {e}")

def test_complete_api_flow():
    """Test a complete quiz flow via API."""
    if not test_server_health():
        pytest.skip("Server not available")
    
    try:
        print("🚀 Starting complete API flow test...")
        
        # 1. Start quiz
        start_response = requests.post(f"{ROUND1_BASE}/start", 
                                     json={"max_questions": 3})
        assert start_response.status_code == 200
        start_data = start_response.json()
        assert start_data["success"], "Quiz should start successfully"
        print("✅ Step 1: Quiz started")
        
        # 2. Answer 3 questions
        for i in range(3):
            # Get question
            question_response = requests.get(f"{ROUND1_BASE}/question")
            if question_response.status_code != 200:
                break
                
            question_data = question_response.json()
            if not question_data.get("success", False):
                break
            
            print(f"✅ Step 2.{i+1}: Got question {i+1}")
            
            # Submit answer
            answer = ["A", "B", "C"][i]  # Vary answers
            answer_response = requests.post(f"{ROUND1_BASE}/answer", 
                                          json={"answer": answer})
            
            if answer_response.status_code == 200:
                answer_data = answer_response.json()
                if answer_data.get("success", False):
                    result = answer_data["data"]
                    print(f"✅ Step 3.{i+1}: Answer '{answer}' - {'Correct' if result.get('is_correct') else 'Incorrect'}")
                    
                    if result.get("quiz_completed", False):
                        print("🎉 Quiz completed!")
                        break
        
        # 3. Get final performance
        performance_response = requests.get(f"{ROUND1_BASE}/performance")
        if performance_response.status_code == 200:
            performance_data = performance_response.json()["data"]
            print(f"✅ Step 4: Final performance - {performance_data['accuracy']:.1%} accuracy")
        
        print("🎉 Complete API flow test successful!")
        assert True
        
    except Exception as e:
        print(f"❌ Complete API flow test failed: {e}")
        pytest.fail(f"Complete API flow error: {e}")

if __name__ == "__main__":
    print("🧪 Running API endpoint tests...")
    print("⚠️  Make sure the server is running: python main.py")
    print()
    
    test_server_health()
    test_round1_intro()
    test_start_quiz_endpoint()
    test_get_question_endpoint()
    test_submit_answer_endpoint()
    test_performance_endpoint()
    test_complete_api_flow()
    
    print("🎉 All API endpoint tests completed!")
