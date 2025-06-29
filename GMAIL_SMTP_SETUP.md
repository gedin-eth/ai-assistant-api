# Gmail SMTP Setup Guide

## 🔧 Setting up Gmail SMTP with App Passwords

This guide will help you set up Gmail SMTP authentication using App Passwords, which is much simpler than OAuth2 for personal Gmail accounts.

### **Step 1: Enable 2-Factor Authentication**

1. **Go to your Google Account settings:**
   ```
   https://myaccount.google.com/
   ```

2. **Enable 2-Step Verification:**
   - Go to "Security" → "2-Step Verification"
   - Follow the setup process
   - This is required to use App Passwords

### **Step 2: Generate an App Password**

1. **Go to App Passwords:**
   ```
   https://myaccount.google.com/apppasswords
   ```

2. **Create a new App Password:**
   - Select "Mail" as the app
   - Select "Other (Custom name)" as device
   - Name it "AI Assistant"
   - Click "Generate"

3. **Copy the App Password:**
   - You'll get a 16-character password like: `abcd efgh ijkl mnop`
   - Copy this password (remove spaces)

### **Step 3: Configure Environment Variables**

1. **Update your `.env` file:**
   ```bash
   # Add these lines to your .env file
   GMAIL_EMAIL=kahlil.gedin@gmail.com
   GMAIL_APP_PASSWORD=your_16_character_app_password
   DEFAULT_EMAIL=kahlil.gedin@gmail.com
   ```

2. **Replace the values:**
   - `GMAIL_EMAIL`: Your Gmail address
   - `GMAIL_APP_PASSWORD`: The 16-character app password you generated
   - `DEFAULT_EMAIL`: Where to send reminder emails

### **Step 4: Test the Setup**

1. **Restart your API server:**
   ```bash
   python3 main.py
   ```

2. **Test the connection:**
   ```bash
   curl http://localhost:8000/email/test
   ```

3. **Send a test email:**
   ```bash
   curl -X POST "http://localhost:8000/email/send" \
     -H "Content-Type: application/json" \
     -d '{
       "to": "kahlil.gedin@gmail.com",
       "subject": "Test Email from AI Assistant",
       "body": "This is a test email to verify SMTP is working!"
     }'
   ```

### **Step 5: Verify Email Delivery**

- Check your Gmail inbox
- You should receive the actual email
- The API response will include a message ID

### **Troubleshooting**

**If you get "App Password not configured":**
- Make sure you've generated an App Password
- Check that 2-Step Verification is enabled
- Verify the password in your `.env` file

**If authentication fails:**
- Double-check your App Password (16 characters, no spaces)
- Make sure you're using the correct Gmail address
- Try generating a new App Password

**If emails don't arrive:**
- Check your spam folder
- Verify the email addresses in your `.env` file
- Check the server logs for error messages

### **Security Notes**

- **Keep your App Password secure:**
  - Never share your App Password
  - Add `.env` to `.gitignore` to keep it out of version control
  - You can revoke App Passwords anytime from Google Account settings

- **App Password vs OAuth2:**
  - App Passwords are simpler for personal use
  - No browser authentication required
  - Works immediately after setup
  - Can be revoked anytime

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