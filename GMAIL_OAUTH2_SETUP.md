# Gmail OAuth2 Setup Guide

## 🔧 Setting up Gmail OAuth2 for Personal Gmail Accounts

This guide will help you set up Gmail OAuth2 authentication so your AI Assistant can send actual emails instead of mock responses.

### **Step 1: Create OAuth2 Credentials**

1. **Go to Google Cloud Console:**
   ```
   https://console.cloud.google.com/
   ```

2. **Select your project:**
   - Choose project: `todo-assitant-464319`

3. **Enable Gmail API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. **Create OAuth2 Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Name: "AI Assistant Gmail OAuth2"
   - Click "Create"

5. **Download Credentials:**
   - Click the download button (⬇️) next to your new OAuth2 client
   - Save as `gmail_oauth_credentials.json` in your project root

### **Step 2: Configure Environment Variables**

1. **Update your `.env` file:**
   ```bash
   # Add these lines to your .env file
   GMAIL_OAUTH_CREDENTIALS_PATH=gmail_oauth_credentials.json
   GMAIL_TOKEN_PATH=gmail_token.pickle
   DEFAULT_EMAIL=kahlil.gedin@gmail.com
   ```

2. **Place the credentials file:**
   - Put `gmail_oauth_credentials.json` in your project root directory

### **Step 3: First-Time Authentication**

1. **Start your API server:**
   ```bash
   python3 main.py
   ```

2. **The first time you send an email, you'll see:**
   - A browser window will open
   - Google will ask you to sign in to your Gmail account
   - Grant permissions to send emails
   - The authentication token will be saved to `gmail_token.pickle`

### **Step 4: Test the Setup**

1. **Test the connection:**
   ```bash
   curl http://localhost:8000/email/test
   ```

2. **Send a test email:**
   ```bash
   curl -X POST "http://localhost:8000/email/send" \
     -H "Content-Type: application/json" \
     -d '{
       "to": "kahlil.gedin@gmail.com",
       "subject": "Test Email from AI Assistant",
       "body": "This is a test email to verify OAuth2 is working!"
     }'
   ```

### **Step 5: Verify Email Delivery**

- Check your Gmail inbox (and spam folder)
- You should receive the actual email
- The API response will include a real message ID

### **Troubleshooting**

**If you get "OAuth2 credentials file not found":**
- Make sure `gmail_oauth_credentials.json` is in your project root
- Check the file path in your `.env` file

**If authentication fails:**
- Delete `gmail_token.pickle` and try again
- Make sure you're using the correct Gmail account
- Check that Gmail API is enabled in Google Cloud Console

**If emails don't arrive:**
- Check your spam folder
- Verify the `DEFAULT_EMAIL` in your `.env` file
- Check the server logs for error messages

### **Security Notes**

- **Never commit credentials to git:**
  - Add `gmail_oauth_credentials.json` to `.gitignore`
  - Add `gmail_token.pickle` to `.gitignore`

- **Token storage:**
  - The OAuth2 token is stored locally in `gmail_token.pickle`
  - This token will auto-refresh when needed
  - Keep this file secure

### **File Structure After Setup**

```
~apiToDo/
├── .env                          # Updated with Gmail OAuth2 settings
├── gmail_oauth_credentials.json  # OAuth2 credentials (downloaded)
├── gmail_token.pickle           # OAuth2 token (auto-generated)
├── main.py                      # Updated with OAuth2 service
├── services/
│   └── gmail_oauth_service.py   # New OAuth2 service
└── ...
```

### **Benefits of OAuth2**

✅ **Works with personal Gmail accounts**  
✅ **Secure authentication**  
✅ **Automatic token refresh**  
✅ **Real email delivery**  
✅ **No mock responses**  

Once set up, your AI Assistant will send actual emails instead of returning mock responses! 🎉 