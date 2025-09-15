"""
Test the AI agents database service functionality.
"""
import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.round1.database_service import DatabaseService

def test_database_service_initialization():
    """Test that DatabaseService can be initialized."""
    try:
        db_service = DatabaseService()
        print("✅ DatabaseService initialized successfully")
        assert True
    except Exception as e:
        print(f"❌ DatabaseService initialization failed: {e}")
        pytest.fail(f"DatabaseService initialization error: {e}")

def test_get_all_topics():
    """Test getting all topics from database."""
    try:
        topics = DatabaseService.get_all_topics()
        print(f"✅ Retrieved {len(topics)} topics from database")
        
        # Basic validations
        assert isinstance(topics, list), "Topics should be a list"
        assert len(topics) > 0, "Should have at least some topics"
        
        # Check that topics are strings
        for topic in topics:
            assert isinstance(topic, str), f"Topic should be string, got {type(topic)}"
            assert len(topic) > 0, "Topic should not be empty"
        
        print(f"📊 Available topics: {topics[:5]}..." if len(topics) > 5 else f"📊 Available topics: {topics}")
        assert True
    except Exception as e:
        print(f"❌ get_all_topics failed: {e}")
        pytest.fail(f"get_all_topics error: {e}")

def test_get_database_stats():
    """Test getting database statistics."""
    try:
        stats = DatabaseService.get_database_stats()
        print("✅ Retrieved database statistics")
        
        # Validate stats structure
        required_keys = ['total_questions', 'easy_questions', 'available_topics', 'topic_distribution']
        for key in required_keys:
            assert key in stats, f"Stats should contain {key}"
        
        assert stats['total_questions'] > 0, "Should have questions in database"
        assert stats['easy_questions'] > 0, "Should have easy questions"
        assert stats['available_topics'] > 0, "Should have topics"
        assert isinstance(stats['topic_distribution'], list), "Topic distribution should be a list"
        
        print(f"📊 Database Stats:")
        print(f"   Total Questions: {stats['total_questions']}")
        print(f"   Easy Questions: {stats['easy_questions']}")
        print(f"   Available Topics: {stats['available_topics']}")
        print(f"   Top 3 Topics: {[t['topic'] for t in stats['topic_distribution'][:3]]}")
        
        assert True
    except Exception as e:
        print(f"❌ get_database_stats failed: {e}")
        pytest.fail(f"get_database_stats error: {e}")

def test_get_diverse_easy_questions():
    """Test getting diverse easy questions."""
    try:
        questions = DatabaseService.get_diverse_easy_questions(10)
        print(f"✅ Retrieved {len(questions)} diverse easy questions")
        
        # Basic validations
        assert isinstance(questions, list), "Questions should be a list"
        assert len(questions) <= 10, "Should not exceed requested limit"
        assert len(questions) > 0, "Should return at least some questions"
        
        # Check question structure
        for question in questions:
            required_keys = ['id', 'question', 'options', 'correct_answer', 'topic']
            for key in required_keys:
                assert key in question, f"Question should contain {key}"
            
            assert isinstance(question['options'], dict), "Options should be a dict"
            assert len(question['options']) == 4, "Should have 4 options (A, B, C, D)"
            assert all(opt in question['options'] for opt in ['A', 'B', 'C', 'D']), "Should have A, B, C, D options"
            assert question['correct_answer'] in ['A', 'B', 'C', 'D'], "Correct answer should be A, B, C, or D"
        
        # Check topic diversity
        topics_in_questions = set(q['topic'] for q in questions)
        print(f"📊 Topics covered: {len(topics_in_questions)} out of {len(questions)} questions")
        print(f"📝 Sample question: {questions[0]['question'][:50]}...")
        
        assert True
    except Exception as e:
        print(f"❌ get_diverse_easy_questions failed: {e}")
        pytest.fail(f"get_diverse_easy_questions error: {e}")

def test_get_questions_by_topic():
    """Test getting questions for a specific topic."""
    try:
        # First get available topics
        topics = DatabaseService.get_all_topics()
        if not topics:
            print("⚠️  No topics available, skipping topic-specific test")
            return
        
        test_topic = topics[0]  # Use first available topic
        questions = DatabaseService.get_questions_by_topic(test_topic, 3)
        
        print(f"✅ Retrieved {len(questions)} questions for topic '{test_topic}'")
        
        # Validate all questions are from the requested topic
        for question in questions:
            assert question['topic'] == test_topic, f"Question topic should be {test_topic}"
        
        assert True
    except Exception as e:
        print(f"❌ get_questions_by_topic failed: {e}")
        pytest.fail(f"get_questions_by_topic error: {e}")

if __name__ == "__main__":
    print("🧪 Running database service tests...")
    test_database_service_initialization()
    test_get_all_topics()
    test_get_database_stats()
    test_get_diverse_easy_questions()
    test_get_questions_by_topic()
    print("🎉 All database service tests passed!")
