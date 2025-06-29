import os
import json
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from dotenv import load_dotenv

load_dotenv()

class GmailOAuthService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        self.credentials_path = os.getenv('GMAIL_OAUTH_CREDENTIALS_PATH', 'gmail_oauth_credentials.json')
        self.token_path = os.getenv('GMAIL_TOKEN_PATH', 'gmail_token.pickle')
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate using OAuth2 flow"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"❌ Token refresh failed: {str(e)}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"OAuth2 credentials file not found at {self.credentials_path}. "
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        print("✅ Gmail OAuth2 authentication successful")

    def send_email(self, subject, body, to, from_email=None):
        """Send email via Gmail API using OAuth2"""
        try:
            if not self.service:
                raise Exception("Gmail service not initialized")
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            if from_email:
                message['from'] = from_email
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"✅ Email sent successfully to {to}")
            print(f"   Message ID: {send_message.get('id')}")
            print(f"   Thread ID: {send_message.get('threadId')}")
            
            return send_message
            
        except Exception as e:
            print(f"❌ Gmail OAuth2 Error: {str(e)}")
            raise Exception(f"Failed to send email: {str(e)}")

    def test_connection(self):
        """Test the Gmail connection"""
        try:
            if not self.service:
                raise Exception("Gmail service not initialized")
            
            # Try to get user profile to test connection
            profile = self.service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress')
            print(f"✅ Gmail OAuth2 connection successful")
            print(f"   Authenticated as: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Gmail OAuth2 connection failed: {str(e)}")
            return False 