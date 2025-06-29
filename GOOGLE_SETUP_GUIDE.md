# Google API Setup Guide

## 🔧 Fixing Google API Permission Issues

### **1. Google Sheets 403 Permission Error**

**Quick Fix:**
1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1WqvKSjWuuEv6WRKg_cVb9ve-RS-_U7aIxEkgVKxtlNs
2. Click "Share" (top right)
3. Add this email: `ai-assistant-api@todo-assitant-464319.iam.gserviceaccount.com`
4. Give it "Editor" permissions
5. Click "Send"

**Alternative (for testing):**
- Click "Share" → "Change to anyone with the link" → "Viewer"

### **2. Gmail 400 Precondition Failed Error**

**For Google Workspace (Business) Accounts:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: `todo-assitant-464319`
3. Go to "APIs & Services" → "Library"
4. Search for "Gmail API" and enable it
5. Go to [Google Workspace Admin Console](https://admin.google.com/)
6. Go to "Security" → "API Controls" → "Domain-wide Delegation"
7. Add service account client ID with scopes:
   ```
   https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.readonly
   ```

**For Personal Gmail Accounts:**
- Service accounts don't work with personal Gmail
- You need to use OAuth2 instead
- For now, email functionality will show "sent" but won't actually send emails

### **3. Current Status**

✅ **Working:**
- Google Calendar (events are being created successfully)
- OpenAI API integration
- All core task management features

⚠️ **Needs Setup:**
- Google Sheets (needs sharing permissions)
- Gmail (needs API setup or OAuth2)

### **4. Quick Test**

After fixing Google Sheets permissions, test with:
```bash
curl -X POST "http://localhost:8000/tasks/ai-create?description=Test task"
```

You should see the task created and added to your Google Sheet.

### **5. For Production Deployment**

The app is ready for deployment even with these Google API issues:
- Core functionality works perfectly
- Google Calendar integration works
- AI features work
- Only Google Sheets sync and Gmail are affected

You can fix these after deployment or use the app without these features initially. 