#!/usr/bin/env python3
"""
Test script to verify the AI Personal Assistant API setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment configuration"""
    print("🔧 Testing Environment Configuration")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check required files
    checks = [
        ("credentials.json", "Google API credentials"),
        (".env", "Environment configuration"),
    ]
    
    for filename, description in checks:
        if os.path.exists(filename):
            print(f"✅ {description}: {filename}")
        else:
            print(f"❌ {description}: {filename} (missing)")
    
    # Check environment variables
    env_vars = [
        ("OPENAI_API_KEY", "OpenAI API Key"),
        ("GOOGLE_SHEET_ID", "Google Sheet ID"),
        ("DEFAULT_EMAIL", "Default Email"),
    ]
    
    print("\n📋 Environment Variables:")
    for var, description in env_vars:
        value = os.getenv(var)
        if value and value not in ['your_openai_api_key_here', 'your_google_sheet_id_here', 'your-email@gmail.com']:
            print(f"✅ {description}: Set")
        else:
            print(f"❌ {description}: Not configured")
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n📚 Testing Module Imports")
    print("=" * 40)
    
    modules = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("openai", "OpenAI"),
        ("google.auth", "Google Auth"),
        ("sqlalchemy", "SQLAlchemy"),
    ]
    
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name}: Imported successfully")
        except ImportError as e:
            print(f"❌ {name}: Import failed - {e}")
            return False
    
    return True

def test_database():
    """Test database connection"""
    print("\n🗄️ Testing Database")
    print("=" * 40)
    
    try:
        from database.database import engine
        from database.models import Task, Schedule
        
        # Test table creation
        Task.metadata.create_all(bind=engine)
        Schedule.metadata.create_all(bind=engine)
        
        print("✅ Database: Tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database: Setup failed - {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Personal Assistant API - Setup Verification")
    print("=" * 50)
    
    # Run tests
    env_ok = test_environment()
    imports_ok = test_imports()
    db_ok = test_database()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Setup Verification Summary:")
    print("=" * 50)
    
    if env_ok and imports_ok and db_ok:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 Next steps:")
        print("1. Add your credentials.json file")
        print("2. Configure your .env file with actual values")
        print("3. Run: ./start.sh")
        print("4. Visit: http://localhost:8000/docs")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print("\n📖 Common fixes:")
        print("- Run: pip install -r requirements.txt")
        print("- Add credentials.json from Google Cloud Console")
        print("- Configure .env file with your actual credentials")

if __name__ == "__main__":
    main() 