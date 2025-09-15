#!/usr/bin/env python3
"""
Test runner for Quiz Auth System.
Runs all tests systematically and reports results.
"""
import sys
import os
import subprocess
import time

def run_test_file(test_file):
    """Run a specific test file and return results."""
    print(f"\n{'='*60}")
    print(f"🧪 RUNNING: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Run the test file directly
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {test_file} - PASSED")
            return True
        else:
            print(f"❌ {test_file} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_file} - TIMEOUT (>30s)")
        return False
    except Exception as e:
        print(f"💥 {test_file} - ERROR: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Quiz Auth System - Test Runner")
    print("=" * 60)
    
    # Change to tests directory (go up one level from scripts)
    test_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests")
    if not os.path.exists(test_dir):
        print("❌ Tests directory not found!")
        sys.exit(1)
    
    # List of test files to run
    test_files = [
        "test_imports.py",
        "test_database_service.py", 
        "test_quiz_service.py",
        "test_api_endpoints.py"
    ]
    
    results = {}
    total_tests = len(test_files)
    
    # Run each test file
    for test_file in test_files:
        test_path = os.path.join(test_dir, test_file)
        
        if not os.path.exists(test_path):
            print(f"⚠️  Test file not found: {test_file}")
            results[test_file] = False
            continue
        
        results[test_file] = run_test_file(test_path)
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for result in results.values() if result)
    failed = total_tests - passed
    
    for test_file, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_file:<30} {status}")
    
    print(f"\n📈 RESULTS: {passed}/{total_tests} tests passed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"💥 {failed} TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
