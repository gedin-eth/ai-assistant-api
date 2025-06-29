#!/usr/bin/env python3
"""
Test script for AI Personal Assistant API
Run this script to test the basic functionality
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    print("🔍 Testing root endpoint...")
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working: {data.get('message')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")
        return False

def test_task_creation():
    """Test task creation"""
    print("🔍 Testing task creation...")
    try:
        task_data = {
            "title": "Test Task",
            "description": "This is a test task created by the test script",
            "priority": 3,
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "estimated_duration": 60
        }
        
        response = requests.post(f"{API_URL}/tasks", json=task_data)
        if response.status_code == 200:
            task = response.json()
            print(f"✅ Task created successfully: {task.get('title')}")
            return task.get('id')
        else:
            print(f"❌ Task creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Task creation error: {str(e)}")
        return None

def test_task_retrieval():
    """Test task retrieval"""
    print("🔍 Testing task retrieval...")
    try:
        response = requests.get(f"{API_URL}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ Retrieved {len(tasks)} tasks")
            return len(tasks) > 0
        else:
            print(f"❌ Task retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Task retrieval error: {str(e)}")
        return False

def test_ai_task_processing():
    """Test AI task processing"""
    print("🔍 Testing AI task processing...")
    try:
        description = "Finish the quarterly report by Friday, should take about 3 hours"
        response = requests.post(f"{API_URL}/tasks/ai-process", params={"description": description})
        if response.status_code == 200:
            processed = response.json()
            print(f"✅ AI processing successful: {processed.get('title')}")
            return True
        else:
            print(f"❌ AI processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ AI processing error: {str(e)}")
        return False

def test_statistics():
    """Test statistics endpoint"""
    print("🔍 Testing statistics...")
    try:
        response = requests.get(f"{API_URL}/tasks/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistics retrieved: {stats.get('total_tasks')} total tasks")
            return True
        else:
            print(f"❌ Statistics failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Statistics error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI Personal Assistant API Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Task Creation", test_task_creation),
        ("Task Retrieval", test_task_retrieval),
        ("AI Task Processing", test_ai_task_processing),
        ("Statistics", test_statistics),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API configuration.")
    
    print(f"\n📖 API Documentation: {BASE_URL}/docs")
    print(f"🔗 Health Check: {BASE_URL}/health")

if __name__ == "__main__":
    main() 