#!/usr/bin/env python3
"""
Test the deployed LangGraph service to identify what's not working.
"""
import requests
import json
import os

# Railway service URL - update this with your actual Railway URL
RAILWAY_SERVICE_URL = "https://your-langgraph-service.up.railway.app"
LOCAL_SERVICE_URL = "http://localhost:8001"

def test_endpoint(url, endpoint, method="GET", data=None):
    """Test a specific endpoint."""
    try:
        full_url = f"{url}{endpoint}"
        print(f"Testing {method} {full_url}")
        
        if method == "GET":
            response = requests.get(full_url, timeout=10)
        elif method == "POST":
            response = requests.post(full_url, json=data, timeout=10)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Response: {json.dumps(result, indent=2)[:200]}...")
            return True, result
        else:
            print(f"  Error: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"  Exception: {str(e)}")
        return False, str(e)

def test_service(base_url):
    """Test all endpoints of the service."""
    print(f"\n🧪 Testing service at: {base_url}")
    print("=" * 60)
    
    # Basic endpoints
    endpoints_to_test = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/status", "GET"),
        ("/debug", "GET"),
    ]
    
    # Test basic endpoints
    for endpoint, method in endpoints_to_test:
        success, result = test_endpoint(base_url, endpoint, method)
        if not success:
            print(f"❌ {endpoint} failed")
        else:
            print(f"✅ {endpoint} working")
    
    # Test initialization
    print(f"\n🔄 Testing initialization...")
    success, result = test_endpoint(base_url, "/initialize", "POST")
    if success:
        print("✅ Initialization endpoint working")
        print(f"Service status: {result.get('service_status', 'Unknown')}")
    else:
        print("❌ Initialization failed")
    
    # Test LangGraph endpoints (if modules loaded)
    langgraph_endpoints = [
        ("/ai-agents/langgraph/test", "POST"),
        ("/ai-agents/langgraph/health", "GET"),
        ("/ai-agents/langgraph/info", "GET"),
    ]
    
    print(f"\n🤖 Testing LangGraph endpoints...")
    for endpoint, method in langgraph_endpoints:
        success, result = test_endpoint(base_url, endpoint, method)
        if not success:
            print(f"❌ {endpoint} failed")
        else:
            print(f"✅ {endpoint} working")
    
    # Test the main quiz endpoint
    print(f"\n🎯 Testing main quiz functionality...")
    quiz_data = {"user_id": "test_user_123"}
    success, result = test_endpoint(base_url, "/ai-agents/langgraph/start-quiz", "POST", quiz_data)
    if success:
        print("✅ Quiz endpoint working")
    else:
        print("❌ Quiz endpoint failed")

def main():
    """Run comprehensive tests."""
    print("🚀 LangGraph Service Deployment Test")
    print("=" * 60)
    
    # Test locally first (if running)
    print("\n📍 Testing local service (if available)...")
    try:
        test_service(LOCAL_SERVICE_URL)
    except Exception as e:
        print(f"Local service not available: {e}")
    
    # Test Railway deployment
    print(f"\n☁️  Testing Railway deployment...")
    print(f"Update RAILWAY_SERVICE_URL in this script with your actual Railway URL")
    print(f"Current URL: {RAILWAY_SERVICE_URL}")
    
    if "your-langgraph-service" not in RAILWAY_SERVICE_URL:
        test_service(RAILWAY_SERVICE_URL)
    else:
        print("⚠️  Please update RAILWAY_SERVICE_URL with your actual Railway deployment URL")

if __name__ == "__main__":
    main()
