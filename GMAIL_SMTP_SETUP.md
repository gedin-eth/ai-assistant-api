# Gmail SMTP Setup Guide

## Overview
The API now uses Gmail SMTP with App Passwords instead of OAuth2 for better container compatibility.

## Setup Steps

### 1. Enable 2-Factor Authentication
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to "Security"
3. Enable "2-Step Verification" if not already enabled

### 2. Generate App Password
1. In Google Account Settings > Security
2. Find "App passwords" (under 2-Step Verification)
3. Click "App passwords"
4. Select "Mail" as the app and "Other" as the device
5. Click "Generate"
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### 3. Update Environment Variables
Add these lines to your `.env` file:

```env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password
```

**Important**: 
- Use your actual Gmail address
- Use the 16-character App Password (remove spaces)
- Do NOT use your regular Gmail password

### 4. Deploy Changes
After updating the `.env` file, redeploy the container:

```bash
ssh root@82.180.161.161 "cd ~/ai-assistant-api/ai-assistant-api && docker-compose down && docker-compose up -d"
```

### 5. Test the Setup
Test the email functionality:

```bash
curl https://your-ngrok-url/email/test
```

## Troubleshooting

### "Invalid credentials" error
- Make sure you're using the App Password, not your regular password
- Ensure 2-factor authentication is enabled
- Verify the email address is correct

### "Gmail service not initialized" error
- Check that both `GMAIL_EMAIL` and `GMAIL_APP_PASSWORD` are set in `.env`
- Restart the container after updating environment variables

### Security Notes
- App Passwords are more secure than OAuth2 for server applications
- Each App Password is specific to the application
- You can revoke App Passwords at any time from Google Account settings

### **File Structure After Setup**

```
~apiToDo/
├── .env                          # Updated with SMTP settings
├── main.py                      # Updated with SMTP service
├── services/
│   └── gmail_smtp_service.py    # New SMTP service
└── ...
```

### **Benefits of SMTP with App Passwords**

✅ **Works with personal Gmail accounts**  
✅ **No OAuth2 verification required**  
✅ **Simple setup process**  
✅ **Real email delivery**  
✅ **Secure authentication**  
✅ **Can be revoked anytime**  

Once set up, your AI Assistant will send actual emails instead of returning mock responses! 🎉

### **Example .env Configuration**

```bash
# Gmail SMTP Configuration
GMAIL_EMAIL=kahlil.gedin@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
DEFAULT_EMAIL=kahlil.gedin@gmail.com
```

**Note:** Replace `abcd efgh ijkl mnop` with your actual 16-character App Password. 