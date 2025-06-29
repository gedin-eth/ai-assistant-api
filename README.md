# AI Personal Assistant API

An intelligent personal assistant that manages tasks, schedules, and productivity using AI. This API integrates with Google services (Sheets, Calendar, Gmail) and OpenAI to provide a comprehensive productivity management solution.

## 🚀 Features

- **AI-Powered Task Management**: Process natural language task descriptions
- **Intelligent Scheduling**: Generate optimal schedules using AI
- **Google Integration**: Sync with Google Sheets, Calendar, and Gmail
- **Email Reminders**: Automated reminder system with AI-generated content
- **Productivity Analytics**: AI-powered insights and recommendations
- **RESTful API**: Full CRUD operations for tasks and schedules
- **Background Processing**: Automated scheduling and monitoring

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Your VPS      │    │   Google APIs   │    │   OpenAI API    │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ • Sheets API    │    │ • GPT-4/4o      │
│ │   FastAPI   │◄┼────┤ • Calendar API  │    │ • Function      │
│ │   Server    │ │    │ • Gmail API     │    │   Calling       │
│ └─────────────┘ │    │ • Drive API     │    │                 │
│                 │    └─────────────────┘    └─────────────────┘
│ ┌─────────────┐ │    
│ │  Database   │ │    
│ │ (SQLite/PG) │ │    
│ └─────────────┘ │    
└─────────────────┘    
```

## 📋 Prerequisites

- Python 3.8+
- Google Cloud Console account
- OpenAI API key
- VPS or local server
- Domain name (optional, for production)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ai-personal-assistant-api
```

### 2. Set Up Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the following APIs:
   - Google Sheets API
   - Google Calendar API
   - Gmail API
   - Google Drive API (optional)
4. Create service account credentials
5. Download the credentials JSON file
6. Set up OAuth 2.0 for user consent (if needed)

### 3. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your credentials
nano .env
```

### 4. Configure Environment Variables

Edit the `.env` file with your actual credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google API Configuration
GOOGLE_CREDENTIALS_PATH=path/to/credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_CALENDAR_ID=primary

# Database Configuration
DATABASE_URL=sqlite:///./assistant.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Email Configuration
DEFAULT_EMAIL=your-email@gmail.com

# Security
SECRET_KEY=your_secret_key_here
```

### 5. Set Up Google Sheet

Create a Google Sheet with the following columns:
- A: Title
- B: Description
- C: Priority (1-5)
- D: Status
- E: Due Date
- F: Estimated Duration (minutes)

Copy the Sheet ID from the URL and add it to your `.env` file.

## 🚀 Quick Start

### Local Development

```bash
# Start the API server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Deployment

Use the provided deployment script:

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🔧 API Endpoints

### Task Management

```bash
# Create a task
POST /tasks
{
  "title": "Complete project report",
  "description": "Finish the quarterly report",
  "priority": 3,
  "due_date": "2024-01-15T17:00:00",
  "estimated_duration": 120
}

# Get all tasks
GET /tasks

# Get task by ID
GET /tasks/{task_id}

# Update task
PUT /tasks/{task_id}

# Delete task
DELETE /tasks/{task_id}

# Get task statistics
GET /tasks/statistics

# Get overdue tasks
GET /tasks/overdue
```

### AI-Powered Features

```bash
# Process natural language task
POST /tasks/ai-process?description="Finish the quarterly report by Friday, should take about 3 hours"

# Create task with AI processing
POST /tasks/ai-create?description="Prepare presentation for client meeting next week"

# Get AI suggestions for task improvements
GET /tasks/{task_id}/improvements
```

### Scheduling

```bash
# Generate optimal schedule
POST /schedule/generate

# Get scheduled tasks
GET /schedule?days_ahead=7

# Create manual schedule
POST /schedule

# Update schedule
PUT /schedule/{schedule_id}

# Mark schedule as completed
POST /schedule/{schedule_id}/complete
```

### Google Integration

```bash
# Sync tasks from Google Sheet
POST /sync/sheets

# Get calendar events
GET /calendar/events?days_ahead=7
```

### Communication

```bash
# Send email
POST /email/send
{
  "subject": "Task Reminder",
  "body": "Don't forget to complete the report",
  "to": "user@example.com"
}

# Send AI-generated reminder
POST /reminders/send
{
  "task_id": 1,
  "message": "Custom reminder message"
}
```

### Analytics

```bash
# Analyze productivity
GET /productivity/analyze?time_period=week
```

## 🧪 Testing

Run the test script to verify functionality:

```bash
# Install test dependencies
pip install requests

# Run tests
python scripts/test_api.py
```

## 📊 Usage Examples

### 1. Adding a Task via AI

```bash
curl -X POST "http://localhost:8000/tasks/ai-create" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Finish the quarterly report by Friday, should take about 3 hours"
  }'
```

### 2. Generate Schedule

```bash
curl -X POST "http://localhost:8000/schedule/generate"
```

### 3. Sync from Google Sheet

```bash
curl -X POST "http://localhost:8000/sync/sheets"
```

### 4. Send Reminder

```bash
curl -X POST "http://localhost:8000/reminders/send" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": 1,
    "message": "This is urgent!"
  }'
```

## 🔒 Security Considerations

- Store API keys securely in environment variables
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Regular security updates
- Monitor API usage and logs

## 🚀 Production Deployment

### VPS Setup

1. **Update system**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install dependencies**:
   ```bash
   sudo apt install python3 python3-pip python3-venv nginx git curl -y
   ```

3. **Run deployment script**:
   ```bash
   ./scripts/deploy.sh
   ```

### SSL Certificate

For production, set up SSL with Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Service Management

```bash
# Start service
sudo systemctl start ai-assistant

# Stop service
sudo systemctl stop ai-assistant

# Restart service
sudo systemctl restart ai-assistant

# Check status
sudo systemctl status ai-assistant

# View logs
sudo journalctl -u ai-assistant -f
```

## 🔧 Configuration

### Database

The default configuration uses SQLite. For production, consider PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost/assistant_db
```

### Rate Limiting

Add rate limiting to your endpoints:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/tasks")
@limiter.limit("10/minute")
async def create_task(request: Request, task_data: TaskInput):
    # Implementation
    pass
```

## 📈 Monitoring

### Health Checks

```bash
curl http://localhost:8000/health
```

### Logs

```bash
# Application logs
sudo journalctl -u ai-assistant -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when running
- **Issues**: Create an issue on GitHub
- **Email**: Contact the maintainer

## 🔄 Updates

To update the application:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart ai-assistant
```

---

**Happy Productivity! 🚀** 