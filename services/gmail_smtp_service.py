import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class GmailSMTPService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.getenv('GMAIL_EMAIL')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not self.email or not self.app_password:
            raise ValueError(
                "Gmail SMTP credentials not configured. "
                "Please set GMAIL_EMAIL and GMAIL_APP_PASSWORD in your .env file"
            )

    def send_email(self, subject, body, to, from_email=None):
        """Send email via Gmail SMTP using App Password"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = from_email or self.email
            msg['To'] = to
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            
            # Login
            server.login(self.email, self.app_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email, to, text)
            server.quit()
            
            print(f"✅ Email sent successfully to {to}")
            print(f"   From: {self.email}")
            print(f"   Subject: {subject}")
            
            return {
                'id': f'smtp_{os.urandom(8).hex()}',
                'threadId': f'thread_{os.urandom(8).hex()}',
                'note': 'Email sent via SMTP'
            }
            
        except Exception as e:
            print(f"❌ Gmail SMTP Error: {str(e)}")
            raise Exception(f"Failed to send email: {str(e)}")

    def test_connection(self):
        """Test SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.app_password)
            server.quit()
            
            print(f"✅ Gmail SMTP connection successful")
            print(f"   Authenticated as: {self.email}")
            return True
            
        except Exception as e:
            print(f"❌ Gmail SMTP connection failed: {str(e)}")
            return False 