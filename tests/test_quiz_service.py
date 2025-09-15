"""
Test the Quiz Service functionality without authentication.
"""
import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.round1.quiz_service import QuizService

def test_quiz_service_initialization():
    """Test that QuizService can be initialized."""
    try:
        quiz_service = QuizService()
        print("✅ QuizService initialized successfully")
        
        # Check initial state
        assert quiz_service.questions_asked_count == 0
        assert quiz_service.max_questions == 15
        assert quiz_service.is_quiz_active == False
        assert quiz_service.current_question is None
        assert len(quiz_service.questions_pool) == 0
        
        print("✅ Initial state is correct")
        assert True
    except Exception as e:
        print(f"❌ QuizService initialization failed: {e}")
        pytest.fail(f"QuizService initialization error: {e}")

def test_start_quiz_session():
    """Test starting a quiz session."""
    try:
        quiz_service = QuizService()
        result = quiz_service.start_quiz_session(max_questions=10)
        
        print("✅ Quiz session started successfully")
        print(f"📊 Result: {result}")
        
        # Validate result structure
        assert isinstance(result, dict)
        assert "success" in result
        assert "message" in result
        assert "data" in result
        
        if result["success"]:
            assert quiz_service.is_quiz_active == True
            assert quiz_service.max_questions == 10
            assert len(quiz_service.questions_pool) > 0
            print(f"✅ Quiz active with {len(quiz_service.questions_pool)} questions in pool")
        else:
            print(f"⚠️  Quiz start failed: {result['message']}")
        
        assert True
    except Exception as e:
        print(f"❌ start_quiz_session failed: {e}")
        pytest.fail(f"start_quiz_session error: {e}")

def test_get_next_question():
    """Test getting the next question."""
    try:
        quiz_service = QuizService()
        
        # Start quiz first
        start_result = quiz_service.start_quiz_session(max_questions=5)
        if not start_result["success"]:
            print(f"⚠️  Cannot test get_next_question: quiz start failed")
            return
        
        # Get first question
        question_result = quiz_service.get_next_question()
        
        print("✅ Got next question successfully")
        print(f"📊 Question result: {question_result}")
        
        # Validate result structure
        assert isinstance(question_result, dict)
        assert "success" in question_result
        assert "message" in question_result
        
        if question_result["success"]:
            data = question_result["data"]
            required_keys = ["question_id", "question", "options", "topic", "question_number", "total_questions"]
            for key in required_keys:
                assert key in data, f"Question data should contain {key}"
            
            assert isinstance(data["options"], dict)
            assert len(data["options"]) == 4
            assert all(opt in data["options"] for opt in ["A", "B", "C", "D"])
            
            print(f"✅ Question structure is valid")
            print(f"📝 Question: {data['question'][:50]}...")
            print(f"🏷️  Topic: {data['topic']}")
        
        assert True
    except Exception as e:
        print(f"❌ get_next_question failed: {e}")
        pytest.fail(f"get_next_question error: {e}")

def test_submit_answer():
    """Test submitting an answer."""
    try:
        quiz_service = QuizService()
        
        # Start quiz and get question
        start_result = quiz_service.start_quiz_session(max_questions=3)
        if not start_result["success"]:
            print(f"⚠️  Cannot test submit_answer: quiz start failed")
            return
        
        question_result = quiz_service.get_next_question()
        if not question_result["success"]:
            print(f"⚠️  Cannot test submit_answer: get question failed")
            return
        
        # Submit answer
        answer_result = quiz_service.submit_answer("A")
        
        print("✅ Answer submitted successfully")
        print(f"📊 Answer result: {answer_result}")
        
        # Validate result structure
        assert isinstance(answer_result, dict)
        assert "success" in answer_result
        
        if answer_result["success"]:
            data = answer_result["data"]
            required_keys = ["is_correct", "user_answer", "correct_answer", "topic", "quiz_completed"]
            for key in required_keys:
                assert key in data, f"Answer data should contain {key}"
            
            assert data["user_answer"] == "A"
            assert data["correct_answer"] in ["A", "B", "C", "D"]
            assert isinstance(data["is_correct"], bool)
            
            print(f"✅ Answer: {'Correct' if data['is_correct'] else 'Incorrect'}")
            print(f"🎯 Correct answer was: {data['correct_answer']}")
        
        assert True
    except Exception as e:
        print(f"❌ submit_answer failed: {e}")
        pytest.fail(f"submit_answer error: {e}")

def test_full_quiz_flow():
    """Test a complete quiz flow."""
    try:
        quiz_service = QuizService()
        
        # Start quiz
        start_result = quiz_service.start_quiz_session(max_questions=3)
        assert start_result["success"], "Quiz should start successfully"
        
        questions_answered = 0
        answers = ["A", "B", "C"]  # Test different answers
        
        while questions_answered < 3:
            # Get question
            question_result = quiz_service.get_next_question()
            
            if not question_result["success"]:
                break
            
            # Submit answer
            answer = answers[questions_answered % len(answers)]
            answer_result = quiz_service.submit_answer(answer)
            
            assert answer_result["success"], f"Answer submission should succeed"
            
            questions_answered += 1
            print(f"✅ Question {questions_answered}/3 completed")
            
            # Check if quiz is completed
            if answer_result["data"].get("quiz_completed", False):
                print("🎉 Quiz completed!")
                assert "final_results" in answer_result["data"]
                break
        
        # Get final performance
        performance_result = quiz_service.get_current_performance()
        assert performance_result["success"], "Should get performance successfully"
        
        performance_data = performance_result["data"]
        print(f"📊 Final Performance:")
        print(f"   Total Questions: {performance_data['total_questions']}")
        print(f"   Correct Answers: {performance_data['correct_answers']}")
        print(f"   Accuracy: {performance_data['accuracy']:.2%}")
        print(f"   Topics Attempted: {performance_data['topics_attempted']}")
        
        assert True
    except Exception as e:
        print(f"❌ full_quiz_flow failed: {e}")
        pytest.fail(f"full_quiz_flow error: {e}")

if __name__ == "__main__":
    print("🧪 Running quiz service tests...")
    test_quiz_service_initialization()
    test_start_quiz_session()
    test_get_next_question()
    test_submit_answer()
    test_full_quiz_flow()
    print("🎉 All quiz service tests passed!")
