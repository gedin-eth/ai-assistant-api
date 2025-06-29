#!/usr/bin/env python3
"""
Environment Configuration Helper
This script helps you set up your .env file with the required credentials
"""

import os
import secrets
import string

def generate_secret_key():
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(50))

def setup_environment():
    """Interactive environment setup"""
    print("🔧 AI Personal Assistant API - Environment Setup")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("📋 Creating .env file from template...")
        os.system('cp env.example .env')
    
    # Read current .env content
    with open('.env', 'r') as f:
        content = f.read()
    
    print("\n📝 Please provide the following information:")
    print("(Press Enter to skip if you want to configure manually later)")
    
    # OpenAI API Key
    openai_key = input("\n🤖 OpenAI API Key: ").strip()
    if openai_key:
        content = content.replace('your_openai_api_key_here', openai_key)
    
    # Google Credentials Path
    creds_path = input("📁 Google Credentials Path (default: credentials.json): ").strip()
    if creds_path:
        content = content.replace('path/to/credentials.json', creds_path)
    else:
        content = content.replace('path/to/credentials.json', 'credentials.json')
    
    # Google Sheet ID
    sheet_id = input("📊 Google Sheet ID: ").strip()
    if sheet_id:
        content = content.replace('your_google_sheet_id_here', sheet_id)
    
    # Default Email
    email = input("📧 Default Email (for reminders): ").strip()
    if email:
        content = content.replace('your-email@gmail.com', email)
    
    # Generate Secret Key
    secret_key = generate_secret_key()
    content = content.replace('your_secret_key_here', secret_key)
    
    # Write updated content
    with open('.env', 'w') as f:
        f.write(content)
    
    print("\n✅ Environment configuration completed!")
    print("\n📋 Summary of what was configured:")
    print(f"   OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
    print(f"   Google Credentials: {'✅ Set' if creds_path else '✅ Default'}")
    print(f"   Google Sheet ID: {'✅ Set' if sheet_id else '❌ Not set'}")
    print(f"   Default Email: {'✅ Set' if email else '❌ Not set'}")
    print(f"   Secret Key: ✅ Generated")
    
    if not openai_key or not sheet_id or not email:
        print("\n⚠️  Some required values were not provided.")
        print("   You can edit the .env file manually to add them later.")
    
    print("\n📖 Next steps:")
    print("1. Make sure credentials.json is in the project root")
    print("2. Run: ./start.sh")
    print("3. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    setup_environment() 