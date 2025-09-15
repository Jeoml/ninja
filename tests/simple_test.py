"""
Simple test without Unicode emojis for Windows compatibility.
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_imports():
    """Test basic imports work."""
    print("Testing basic imports...")
    
    try:
        # Test auth imports
        from auth.config import DATABASE_URL
        from auth.database import get_db
        print("✓ Auth imports successful")
        
        # Test AI agents imports
        from ai_agents.round1.database_service import DatabaseService
        from ai_agents.round1.quiz_service import QuizService
        print("✓ AI agents imports successful")
        
        # Test main app
        import main
        print("✓ Main app import successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_database_connection():
    """Test database connection works."""
    print("Testing database connection...")
    
    try:
        from ai_agents.round1.database_service import DatabaseService
        
        # Test getting topics
        topics = DatabaseService.get_all_topics()
        print(f"✓ Got {len(topics)} topics from database")
        
        # Test getting stats
        stats = DatabaseService.get_database_stats()
        print(f"✓ Database has {stats['total_questions']} total questions")
        print(f"✓ Database has {stats['easy_questions']} easy questions")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_quiz_service():
    """Test quiz service functionality."""
    print("Testing quiz service...")
    
    try:
        from ai_agents.round1.quiz_service import QuizService
        
        quiz = QuizService()
        print("✓ Quiz service created")
        
        # Test starting quiz
        result = quiz.start_quiz_session(5)
        if result["success"]:
            print("✓ Quiz session started")
            
            # Test getting question
            question_result = quiz.get_next_question()
            if question_result["success"]:
                print("✓ Got first question")
                
                # Test submitting answer
                answer_result = quiz.submit_answer("A")
                if answer_result["success"]:
                    print("✓ Answer submitted")
                    print(f"  Answer was: {'Correct' if answer_result['data']['is_correct'] else 'Incorrect'}")
                else:
                    print(f"✗ Answer submission failed: {answer_result['message']}")
            else:
                print(f"✗ Get question failed: {question_result['message']}")
        else:
            print(f"✗ Quiz start failed: {result['message']}")
        
        return True
    except Exception as e:
        print(f"✗ Quiz service test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("QUIZ SYSTEM - SIMPLE TESTS")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Database Connection", test_database_connection), 
        ("Quiz Service", test_quiz_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("SUCCESS: All tests passed!")
        return 0
    else:
        print("FAILURE: Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
