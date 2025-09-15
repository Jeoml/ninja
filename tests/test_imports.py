"""
Test all module imports to catch any import errors.
"""
import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_auth_module_imports():
    """Test that all auth module components import correctly."""
    try:
        from auth.config import DATABASE_URL, JWT_SECRET_KEY, APP_NAME
        from auth.database import get_db, get_db_connection, create_auth_tables, UserDB, OTPDB
        from auth.email_service import EmailService, email_service
        from auth.jwt_service import JWTService
        from auth.otp_service import OTPService
        from auth.models import EmailRequest, OTPVerificationRequest, AuthResponse, TokenResponse
        print("✅ All auth module imports successful")
        assert True
    except ImportError as e:
        print(f"❌ Auth module import failed: {e}")
        pytest.fail(f"Auth module import error: {e}")

def test_ai_agents_module_imports():
    """Test that all AI agents module components import correctly."""
    try:
        from ai_agents.round1.database_service import DatabaseService
        from ai_agents.round1.catalog_service import CatalogService, TopicStatus, TopicPerformance
        from ai_agents.round1.quiz_service import QuizService
        from ai_agents.round1.models import QuizStartRequest, SubmitAnswerRequest, QuizResponse, AnswerChoice
        from ai_agents.round1.api import router
        print("✅ All AI agents module imports successful")
        assert True
    except ImportError as e:
        print(f"❌ AI agents module import failed: {e}")
        pytest.fail(f"AI agents module import error: {e}")

def test_main_app_import():
    """Test that the main FastAPI app imports correctly."""
    try:
        import main
        print("✅ Main app import successful")
        assert hasattr(main, 'app')
        assert hasattr(main.app, 'routes')
        print(f"✅ Main app has {len(main.app.routes)} routes configured")
        assert True
    except ImportError as e:
        print(f"❌ Main app import failed: {e}")
        pytest.fail(f"Main app import error: {e}")

def test_cross_module_dependencies():
    """Test that cross-module dependencies work correctly."""
    try:
        # Test that AI agents can import auth database utilities
        from ai_agents.round1.database_service import DatabaseService
        from auth.database import get_db
        
        # Verify that AI agents is using auth's database function
        import inspect
        ai_db_source = inspect.getsource(DatabaseService.get_all_topics)
        assert 'get_db()' in ai_db_source, "AI agents should use auth's get_db function"
        
        print("✅ Cross-module dependencies working correctly")
        assert True
    except Exception as e:
        print(f"❌ Cross-module dependency test failed: {e}")
        pytest.fail(f"Cross-module dependency error: {e}")

if __name__ == "__main__":
    print("Running import tests...")
    test_auth_module_imports()
    test_ai_agents_module_imports()
    test_main_app_import()
    test_cross_module_dependencies()
    print("All import tests passed!")
