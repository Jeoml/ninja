#!/usr/bin/env python3
"""
Railway Deployment Diagnostic Script
Run this to identify specific issues with the LangGraph service deployment.
"""
import os
import sys
import traceback

def test_basic_imports():
    """Test basic Python imports."""
    print("🔍 Testing basic imports...")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except Exception as e:
        print(f"❌ Uvicorn import failed: {e}")
    
    try:
        import psycopg2
        print(f"✅ psycopg2: {psycopg2.__version__}")
    except Exception as e:
        print(f"❌ psycopg2 import failed: {e}")

def test_ai_imports():
    """Test AI-related imports."""
    print("\n🔍 Testing AI imports...")
    
    try:
        import groq
        print(f"✅ Groq: {groq.__version__}")
    except Exception as e:
        print(f"❌ Groq import failed: {e}")
    
    try:
        import langgraph
        print(f"✅ LangGraph: {langgraph.__version__}")
    except Exception as e:
        print(f"❌ LangGraph import failed: {e}")
    
    try:
        import langchain_core
        print(f"✅ LangChain Core: {langchain_core.__version__}")
    except Exception as e:
        print(f"❌ LangChain Core import failed: {e}")

def test_local_imports():
    """Test local module imports."""
    print("\n🔍 Testing local imports...")
    
    try:
        from langgraph_agent.groq_client import groq_client
        print("✅ Groq client imported")
    except Exception as e:
        print(f"❌ Groq client import failed: {e}")
        traceback.print_exc()
    
    try:
        from langgraph_agent.tools import get_all_topics
        print("✅ Tools imported")
    except Exception as e:
        print(f"❌ Tools import failed: {e}")
        traceback.print_exc()
    
    try:
        from langgraph_agent.quiz_agent import quiz_agent
        print("✅ Quiz agent imported")
    except Exception as e:
        print(f"❌ Quiz agent import failed: {e}")
        traceback.print_exc()
    
    try:
        from langgraph_agent.api import router
        print("✅ API router imported")
    except Exception as e:
        print(f"❌ API router import failed: {e}")
        traceback.print_exc()

def test_environment():
    """Test environment variables."""
    print("\n🔍 Testing environment variables...")
    
    env_vars = ["PORT", "GROQ_API_KEY", "BACKEND_SERVICE_URL"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if var == "GROQ_API_KEY":
                print(f"✅ {var}: Set (length: {len(value)})")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set")

def test_database_connection():
    """Test database connectivity."""
    print("\n🔍 Testing database connection...")
    
    try:
        import psycopg2
        DATABASE_URL = "postgresql://neondb_owner:npg_gbCZGkeq8f7W@ep-small-forest-ad89jah2-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connected: {version[:50]}...")
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

def test_backend_service():
    """Test backend service connectivity."""
    print("\n🔍 Testing backend service connectivity...")
    
    try:
        import requests
        backend_url = os.getenv("BACKEND_SERVICE_URL", "https://ninja-production-6ed6.up.railway.app")
        
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Backend service reachable: {backend_url}")
        else:
            print(f"⚠️  Backend service returned HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Backend service unreachable: {e}")

def test_groq_api():
    """Test Groq API connectivity."""
    print("\n🔍 Testing Groq API connectivity...")
    
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️  GROQ_API_KEY not set")
            return
        
        from groq import Groq
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'test'"}],
            model="llama-3.1-70b-versatile",
            max_tokens=5
        )
        
        if response.choices[0].message.content:
            print("✅ Groq API working")
        else:
            print("⚠️  Groq API returned empty response")
            
    except Exception as e:
        print(f"❌ Groq API failed: {e}")

def main():
    """Run all diagnostic tests."""
    print("🚀 Railway Deployment Diagnostics")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[:3]}")
    
    test_basic_imports()
    test_environment()
    test_database_connection()
    test_backend_service()
    test_ai_imports()
    test_groq_api()
    test_local_imports()
    
    print("\n" + "=" * 50)
    print("🏁 Diagnostics complete!")

if __name__ == "__main__":
    main()
