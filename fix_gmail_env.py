#!/usr/bin/env python3
"""
Script to fix Gmail OAuth2 environment variables in .env file
"""

import os
import re

def fix_env_file():
    """Fix the Gmail OAuth2 paths in .env file"""
    
    # Read current .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Fix the Gmail OAuth2 paths
    content = re.sub(
        r'GMAIL_OAUTH_CREDENTIALS_PATH=gmail_oauth_credentials\.json',
        'GMAIL_OAUTH_CREDENTIALS_PATH=credentials/gmail_oauth_credentials.json',
        content
    )
    
    content = re.sub(
        r'GMAIL_TOKEN_PATH=gmail_token\.pickle',
        'GMAIL_TOKEN_PATH=credentials/gmail_token.pickle',
        content
    )
    
    # Also fix Google credentials path if needed
    content = re.sub(
        r'GOOGLE_CREDENTIALS_PATH=todo-assitant-464319-5d1327fc302a\.json',
        'GOOGLE_CREDENTIALS_PATH=credentials/todo-assitant-464319-5d1327fc302a.json',
        content
    )
    
    # Write back to .env file
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Fixed Gmail OAuth2 environment variables in .env file")
    print("   - GMAIL_OAUTH_CREDENTIALS_PATH now points to credentials/gmail_oauth_credentials.json")
    print("   - GMAIL_TOKEN_PATH now points to credentials/gmail_token.pickle")
    print("   - GOOGLE_CREDENTIALS_PATH now points to credentials/todo-assitant-464319-5d1327fc302a.json")

if __name__ == "__main__":
    fix_env_file() 