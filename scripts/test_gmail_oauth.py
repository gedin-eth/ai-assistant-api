#!/usr/bin/env python3
"""
Test script for Gmail OAuth2 integration
Run this script to test the Gmail OAuth2 setup
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.gmail_oauth_service import GmailOAuthService

def test_gmail_oauth_setup():
    """Test Gmail OAuth2 setup"""
    print("🧪 Testing Gmail OAuth2 Setup")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if credentials file exists
    credentials_path = os.getenv('GMAIL_OAUTH_CREDENTIALS_PATH', 'gmail_oauth_credentials.json')
    if not os.path.exists(credentials_path):
        print(f"❌ OAuth2 credentials file not found: {credentials_path}")
        print("\n📋 Please follow the setup guide:")
        print("1. Go to Google Cloud Console")
        print("2. Create OAuth2 credentials")
        print("3. Download as 'gmail_oauth_credentials.json'")
        print("4. Place in project root directory")
        return False
    
    print(f"✅ OAuth2 credentials file found: {credentials_path}")
    
    try:
        # Initialize Gmail OAuth service
        print("\n🔐 Initializing Gmail OAuth2 service...")
        gmail_service = GmailOAuthService()
        
        # Test connection
        print("\n🔍 Testing Gmail connection...")
        if gmail_service.test_connection():
            print("✅ Gmail OAuth2 connection successful!")
            
            # Test email sending
            print("\n📧 Testing email sending...")
            test_email = "kahlil.gedin@gmail.com"
            result = gmail_service.send_email(
                subject="Test Email from AI Assistant OAuth2",
                body="This is a test email to verify that Gmail OAuth2 is working correctly!\n\nIf you receive this email, the OAuth2 setup is successful.",
                to=test_email
            )
            
            print(f"✅ Test email sent successfully!")
            print(f"   Message ID: {result.get('id')}")
            print(f"   Thread ID: {result.get('threadId')}")
            print(f"\n📬 Check your email at: {test_email}")
            
            return True
        else:
            print("❌ Gmail OAuth2 connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Gmail OAuth2 setup failed: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Gmail API is enabled in Google Cloud Console")
        print("2. Check that your OAuth2 credentials are correct")
        print("3. Try deleting gmail_token.pickle and re-authenticating")
        return False

def main():
    """Main test function"""
    print("🚀 Gmail OAuth2 Integration Test")
    print("=" * 50)
    
    success = test_gmail_oauth_setup()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Gmail OAuth2 setup is working correctly!")
        print("✅ You can now send real emails from your AI Assistant")
    else:
        print("⚠️  Gmail OAuth2 setup needs attention")
        print("📖 See GMAIL_OAUTH2_SETUP.md for detailed instructions")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 