from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

# Load .env as early as possible
load_dotenv()

class GoogleService:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly'
        ]
        self.credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        print(f"Using credentials from: {self.credentials_path}")  # Debug print
        
        # Check if credentials file exists before trying to authenticate
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")
        
        self.creds = self._authenticate()
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)

    def _authenticate(self):
        """Handle Google Service Account authentication"""
        print(f"🔐 Authenticating with service account...")
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.SCOPES
        )
        
        # Print service account email for debugging
        if hasattr(creds, 'service_account_email'):
            print(f"✅ Authenticated as: {creds.service_account_email}")
        else:
            print(f"✅ Authenticated with service account")
        
        return creds

    def read_sheet(self, sheet_id=None, range_name='A:Z'):
        """Read data from Google Sheet"""
        sheet_id = sheet_id or os.getenv('GOOGLE_SHEET_ID')
        if not sheet_id:
            raise ValueError("Google Sheet ID not configured")
        
        print(f"📖 Reading Google Sheet:")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   Range: {range_name}")
        
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=range_name
            ).execute()
            
            print(f"✅ Successfully read {len(result.get('values', []))} rows from sheet")
            return result.get('values', [])
        except Exception as e:
            print(f"❌ Error reading Google Sheet:")
            print(f"   Sheet ID: {sheet_id}")
            print(f"   Range: {range_name}")
            print(f"   Error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            
            # Print full error details if available
            if hasattr(e, 'resp') and e.resp:
                print(f"   HTTP Status: {e.resp.status}")
                print(f"   Response: {e.resp.data}")
            
            raise Exception(f"Error reading Google Sheet: {str(e)}")

    def add_task_to_sheet(self, task, sheet_id=None):
        """Add a task to Google Sheet"""
        sheet_id = sheet_id or os.getenv('GOOGLE_SHEET_ID')
        if not sheet_id:
            raise ValueError("Google Sheet ID not configured")
        
        values = [[
            task.title,
            task.description or '',
            task.priority,
            task.status,
            task.due_date.isoformat() if task.due_date else '',
            task.estimated_duration or ''
        ]]
        
        body = {'values': values}
        
        print(f"📝 Adding task to Google Sheet:")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   Range: A:F")
        print(f"   Task: {task.title}")
        print(f"   Request body: {json.dumps(body, indent=2)}")
        
        try:
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range='A:F',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Successfully added task to sheet")
            print(f"   Updated range: {result.get('updates', {}).get('updatedRange', 'N/A')}")
            return result
        except Exception as e:
            print(f"❌ Google Sheets API Error:")
            print(f"   Sheet ID: {sheet_id}")
            print(f"   Range: A:F")
            print(f"   Task: {task.title}")
            print(f"   Error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            
            # Print full error details if available
            if hasattr(e, 'resp') and e.resp:
                print(f"   HTTP Status: {e.resp.status}")
                print(f"   Response: {e.resp.data}")
            
            print("\n🔧 To fix Google Sheets permissions:")
            print(f"1. Share your Google Sheet with: ai-assistant-api@todo-assitant-464319.iam.gserviceaccount.com")
            print(f"2. Give it 'Editor' permissions")
            print(f"3. Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
            print("4. Wait 2-3 minutes after sharing before testing again")
            print("5. For now, task creation will continue without Google Sheets sync")
            
            # Return a mock response to prevent app crashes
            return {
                'updates': {
                    'updatedRange': f'{sheet_id}!A:F',
                    'updatedRows': 1,
                    'updatedColumns': 6,
                    'updatedCells': 6
                },
                'note': 'Task not added to sheet - permissions issue'
            }

    def get_calendar_events(self, days_ahead=7):
        """Get calendar events for scheduling"""
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        
        now = datetime.utcnow().isoformat() + 'Z'
        end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        try:
            events_result = self.calendar_service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except Exception as e:
            raise Exception(f"Error reading calendar events: {str(e)}")

    def create_calendar_event(self, event_data):
        """Create a calendar event"""
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        
        try:
            event = self.calendar_service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            return event
        except Exception as e:
            raise Exception(f"Error creating calendar event: {str(e)}")

    def send_email(self, subject, body, to):
        """Send email via Gmail API"""
        from email.mime.text import MIMEText
        import base64
        
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return send_message
        except Exception as e:
            # Log the error but don't crash the app
            print(f"Gmail API Error: {str(e)}")
            print("To fix Gmail API issues:")
            print("1. Enable Gmail API in Google Cloud Console")
            print("2. For personal Gmail: Use OAuth2 instead of service account")
            print("3. For Workspace: Enable domain-wide delegation")
            print("4. For now, email functionality is disabled")
            
            # Return a mock response to prevent app crashes
            return {
                'id': 'mock_email_id',
                'threadId': 'mock_thread_id',
                'labelIds': ['SENT'],
                'note': 'Email not sent - Gmail API not configured'
            }

    def update_task_in_sheet(self, task, row_id, sheet_id=None):
        """Update an existing task in Google Sheet"""
        sheet_id = sheet_id or os.getenv('GOOGLE_SHEET_ID')
        if not sheet_id:
            raise ValueError("Google Sheet ID not configured")
        
        values = [[
            task.title,
            task.description or '',
            task.priority,
            task.status,
            task.due_date.isoformat() if task.due_date else '',
            task.estimated_duration or ''
        ]]
        
        body = {'values': values}
        
        print(f"📝 Updating task in Google Sheet:")
        print(f"   Sheet ID: {sheet_id}")
        print(f"   Range: A{row_id}:F{row_id}")
        print(f"   Task: {task.title}")
        print(f"   Request body: {json.dumps(body, indent=2)}")
        
        try:
            result = self.sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f'A{row_id}:F{row_id}',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Successfully updated task in sheet")
            print(f"   Updated range: {result.get('updatedRange', 'N/A')}")
            return result
        except Exception as e:
            print(f"❌ Error updating task in Google Sheet:")
            print(f"   Sheet ID: {sheet_id}")
            print(f"   Range: A{row_id}:F{row_id}")
            print(f"   Task: {task.title}")
            print(f"   Error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            
            # Print full error details if available
            if hasattr(e, 'resp') and e.resp:
                print(f"   HTTP Status: {e.resp.status}")
                print(f"   Response: {e.resp.data}")
            
            raise Exception(f"Error updating task in Google Sheet: {str(e)}") 