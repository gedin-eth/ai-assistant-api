#!/usr/bin/env python3
"""
Comprehensive test script for AI Personal Assistant API
Tests all endpoints that weren't covered in the basic test
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}"

def test_get_specific_task():
    """Test getting a specific task by ID"""
    print("🔍 Testing get specific task...")
    try:
        # First get all tasks to get an ID
        response = requests.get(f"{API_URL}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                task_id = tasks[0]['id']
                response = requests.get(f"{API_URL}/tasks/{task_id}")
                if response.status_code == 200:
                    task = response.json()
                    print(f"✅ Retrieved task {task_id}: {task.get('title')}")
                    return True
                else:
                    print(f"❌ Failed to get task {task_id}: {response.status_code}")
                    return False
            else:
                print("❌ No tasks available to test")
                return False
        else:
            print(f"❌ Failed to get tasks: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get specific task error: {str(e)}")
        return False

def test_update_task():
    """Test updating a task"""
    print("🔍 Testing task update...")
    try:
        # First get all tasks to get an ID
        response = requests.get(f"{API_URL}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                task_id = tasks[0]['id']
                update_data = {
                    "title": f"Updated Task - {datetime.now().strftime('%H:%M:%S')}",
                    "priority": 4,
                    "status": "in_progress"
                }
                response = requests.put(f"{API_URL}/tasks/{task_id}", json=update_data)
                if response.status_code == 200:
                    task = response.json()
                    print(f"✅ Updated task {task_id}: {task.get('title')}")
                    return True
                else:
                    print(f"❌ Failed to update task {task_id}: {response.status_code}")
                    return False
            else:
                print("❌ No tasks available to test")
                return False
        else:
            print(f"❌ Failed to get tasks: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Update task error: {str(e)}")
        return False

def test_delete_task():
    """Test deleting a task"""
    print("🔍 Testing task deletion...")
    try:
        # First create a task to delete
        task_data = {
            "title": "Task to Delete",
            "description": "This task will be deleted",
            "priority": 1,
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "estimated_duration": 30
        }
        
        create_response = requests.post(f"{API_URL}/tasks", json=task_data)
        if create_response.status_code == 200:
            task = create_response.json()
            task_id = task['id']
            
            # Now delete it
            delete_response = requests.delete(f"{API_URL}/tasks/{task_id}")
            if delete_response.status_code == 200:
                print(f"✅ Successfully deleted task {task_id}")
                return True
            else:
                print(f"❌ Failed to delete task {task_id}: {delete_response.status_code}")
                return False
        else:
            print(f"❌ Failed to create task for deletion: {create_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Delete task error: {str(e)}")
        return False

def test_get_overdue_tasks():
    """Test getting overdue tasks"""
    print("🔍 Testing overdue tasks...")
    try:
        response = requests.get(f"{API_URL}/tasks/overdue")
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ Retrieved {len(tasks)} overdue tasks")
            return True
        else:
            print(f"❌ Failed to get overdue tasks: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Overdue tasks error: {str(e)}")
        return False

def test_task_improvements():
    """Test AI task improvements"""
    print("🔍 Testing task improvements...")
    try:
        # First get all tasks to get an ID
        response = requests.get(f"{API_URL}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                task_id = tasks[0]['id']
                response = requests.get(f"{API_URL}/tasks/{task_id}/improvements")
                if response.status_code == 200:
                    improvements = response.json()
                    print(f"✅ Got improvements for task {task_id}")
                    return True
                else:
                    print(f"❌ Failed to get improvements for task {task_id}: {response.status_code}")
                    return False
            else:
                print("❌ No tasks available to test")
                return False
        else:
            print(f"❌ Failed to get tasks: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Task improvements error: {str(e)}")
        return False

def test_schedule_generation():
    """Test AI schedule generation"""
    print("🔍 Testing schedule generation...")
    try:
        response = requests.post(f"{API_URL}/schedule/generate")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Schedule generation: {result.get('message')}")
            return True
        else:
            print(f"❌ Schedule generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Schedule generation error: {str(e)}")
        return False

def test_get_schedule():
    """Test getting schedule"""
    print("🔍 Testing get schedule...")
    try:
        response = requests.get(f"{API_URL}/schedule")
        if response.status_code == 200:
            schedules = response.json()
            print(f"✅ Retrieved {len(schedules)} schedule entries")
            return True
        else:
            print(f"❌ Failed to get schedule: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get schedule error: {str(e)}")
        return False

def test_calendar_events():
    """Test getting calendar events"""
    print("🔍 Testing calendar events...")
    try:
        response = requests.get(f"{API_URL}/calendar/events")
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Retrieved {len(events)} calendar events")
            return True
        else:
            print(f"❌ Failed to get calendar events: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Calendar events error: {str(e)}")
        return False

def test_productivity_analysis():
    """Test productivity analysis"""
    print("🔍 Testing productivity analysis...")
    try:
        response = requests.get(f"{API_URL}/productivity/analyze?time_period=week")
        if response.status_code == 200:
            analysis = response.json()
            print(f"✅ Productivity analysis completed")
            return True
        else:
            print(f"❌ Productivity analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Productivity analysis error: {str(e)}")
        return False

def test_email_send():
    """Test email sending"""
    print("🔍 Testing email sending...")
    try:
        email_data = {
            "to": "test@example.com",
            "subject": "Test Email from API",
            "body": "This is a test email from the AI Assistant API"
        }
        response = requests.post(f"{API_URL}/email/send", json=email_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email sent: {result.get('message')}")
            return True
        else:
            print(f"❌ Email sending failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Email sending error: {str(e)}")
        return False

def test_reminder_send():
    """Test reminder sending"""
    print("🔍 Testing reminder sending...")
    try:
        reminder_data = {
            "task_id": 1,
            "message": "Test reminder from API",
            "reminder_time": (datetime.now() + timedelta(minutes=5)).isoformat()
        }
        response = requests.post(f"{API_URL}/reminders/send", json=reminder_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Reminder sent: {result.get('message')}")
            return True
        else:
            print(f"❌ Reminder sending failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Reminder sending error: {str(e)}")
        return False

def main():
    """Run all comprehensive tests"""
    print("🚀 Starting Comprehensive API Endpoint Tests")
    print("=" * 60)
    
    tests = [
        ("Get Specific Task", test_get_specific_task),
        ("Update Task", test_update_task),
        ("Delete Task", test_delete_task),
        ("Get Overdue Tasks", test_get_overdue_tasks),
        ("Task Improvements", test_task_improvements),
        ("Schedule Generation", test_schedule_generation),
        ("Get Schedule", test_get_schedule),
        ("Calendar Events", test_calendar_events),
        ("Productivity Analysis", test_productivity_analysis),
        ("Email Send", test_email_send),
        ("Reminder Send", test_reminder_send),
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
    print("\n" + "=" * 60)
    print("📊 Comprehensive Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All comprehensive tests passed! API is fully functional.")
    else:
        print("⚠️  Some tests failed. Check the API configuration.")
    
    print(f"\n📖 API Documentation: {BASE_URL}/docs")
    print(f"🔗 Health Check: {BASE_URL}/health")

if __name__ == "__main__":
    main() 