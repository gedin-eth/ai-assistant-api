#!/usr/bin/env python3
"""
Google Sheets Test Script
This script helps diagnose Google Sheets API connectivity and permission issues.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.google_service import GoogleService

def test_google_sheets():
    """Test Google Sheets connectivity and permissions"""
    print("🧪 Testing Google Sheets API...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'todo-assitant-464319-5d1327fc302a.json')
    
    print(f"📋 Configuration:")
    print(f"   Sheet ID: {sheet_id}")
    print(f"   Credentials: {credentials_path}")
    print()
    
    # Check if files exist
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        return False
    
    if not sheet_id:
        print("❌ GOOGLE_SHEET_ID not configured in environment")
        return False
    
    try:
        # Initialize Google Service
        print("🔐 Initializing Google Service...")
        google_service = GoogleService()
        print("✅ Google Service initialized successfully")
        print()
        
        # Test reading the sheet
        print("📖 Testing sheet read access...")
        try:
            data = google_service.read_sheet(sheet_id, 'A:Z')
            print(f"✅ Successfully read {len(data)} rows from sheet")
            
            if data:
                print("📊 Sample data (first 3 rows):")
                for i, row in enumerate(data[:3]):
                    print(f"   Row {i+1}: {row}")
            else:
                print("📊 Sheet is empty")
                
        except Exception as e:
            print(f"❌ Failed to read sheet: {str(e)}")
            print()
            print("🔧 Troubleshooting steps:")
            print("1. Go to your Google Sheet")
            print("2. Click 'Share' button")
            print("3. Remove any existing sharing with the service account")
            print("4. Add: ai-assistant-api@todo-assitant-464319.iam.gserviceaccount.com")
            print("5. Give 'Editor' permissions")
            print("6. Wait 2-3 minutes before testing again")
            print()
            print("📋 Sheet URL: https://docs.google.com/spreadsheets/d/" + sheet_id)
            return False
        
        # Test writing to the sheet
        print()
        print("📝 Testing sheet write access...")
        try:
            # Create a test task object
            class TestTask:
                def __init__(self):
                    self.title = "Test Task - " + str(int(time.time()))
                    self.description = "This is a test task from the diagnostic script"
                    self.priority = "Medium"
                    self.status = "Pending"
                    self.due_date = None
                    self.estimated_duration = "1 hour"
            
            test_task = TestTask()
            result = google_service.add_task_to_sheet(test_task, sheet_id)
            print("✅ Successfully added test task to sheet")
            
        except Exception as e:
            print(f"❌ Failed to write to sheet: {str(e)}")
            return False
        
        print()
        print("🎉 All Google Sheets tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize Google Service: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_google_sheets()
    sys.exit(0 if success else 1) 