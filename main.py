from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from services.google_service import GoogleService
from services.openai_service import OpenAIService
from services.task_service import TaskService
from services.scheduler_service import SchedulerService
from services.gmail_oauth_service import GmailOAuthService
from services.gmail_smtp_service import GmailSMTPService
from database.models import Task, Schedule
from database.database import engine, get_db
from models import (
    TaskInput, TaskResponse, TaskUpdate, ScheduleResponse, 
    ScheduleCreate, ScheduleUpdate, TaskStatistics, EmailRequest,
    ReminderRequest, ProductivityAnalysis, AIRequest
)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI Personal Assistant API",
    description="An intelligent personal assistant that manages tasks, schedules, and productivity using AI",
    version="1.0.0",
    servers=[
        {
            "url": "https://421b-2a02-4780-10-ec0d-00-1.ngrok-free.app",
            "description": "Production server via ngrok tunnel"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
)

# Add CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services as None - will be set in startup
google_service = None
openai_service = None
task_service = None
scheduler_service = None
gmail_service = None

def get_services():
    """Dependency to ensure services are available"""
    if not all([task_service, scheduler_service]):
        raise HTTPException(status_code=503, detail="Core services not initialized")
    return google_service, openai_service, task_service, scheduler_service

def get_gmail_service():
    """Dependency to get Gmail service (SMTP or OAuth2)"""
    if not gmail_service:
        raise HTTPException(status_code=503, detail="Gmail service not initialized")
    return gmail_service

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks"""
    global google_service, openai_service, task_service, scheduler_service, gmail_service
    
    # Initialize services after environment variables are loaded
    # Initialize Google Service (optional - won't crash if not configured)
    try:
        google_service = GoogleService()
        print("✅ Google service initialized")
    except Exception as e:
        print(f"⚠️  Google service not initialized: {str(e)}")
        google_service = None
    
    # Initialize OpenAI Service (optional - won't crash if not configured)
    try:
        openai_service = OpenAIService()
        print("✅ OpenAI service initialized")
    except Exception as e:
        print(f"⚠️  OpenAI service not initialized: {str(e)}")
        openai_service = None
    
    task_service = TaskService()
    scheduler_service = SchedulerService(google_service)
    
    # Initialize Gmail service - try SMTP first, then OAuth2
    try:
        # Try SMTP first (better for containers)
        gmail_service = GmailSMTPService()
        print("✅ Gmail SMTP service initialized")
    except Exception as e:
        print(f"⚠️  Gmail SMTP service not initialized: {str(e)}")
        try:
            # Fall back to OAuth2
            gmail_service = GmailOAuthService()
            print("✅ Gmail OAuth2 service initialized")
        except Exception as e2:
            print(f"⚠️  Gmail OAuth2 service not initialized: {str(e2)}")
            gmail_service = None
    
    # Create database tables
    Task.metadata.create_all(bind=engine)
    Schedule.metadata.create_all(bind=engine)
    
    # Start background scheduler
    asyncio.create_task(scheduler_service.run_scheduler())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global scheduler_service
    if scheduler_service:
        scheduler_service.stop_scheduler()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Personal Assistant API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Task Management Endpoints

@app.post("/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskInput, services=Depends(get_services)):
    """Create a new task"""
    try:
        _, _, task_service, _ = services
        task = task_service.create_task(task_data.dict())
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks", response_model=list[TaskResponse])
async def get_tasks(status: str = None, priority: int = None, services=Depends(get_services)):
    """Get all tasks with optional filtering"""
    try:
        _, _, task_service, _ = services
        tasks = task_service.get_all_tasks()
        
        # Apply filters
        if status:
            tasks = [task for task in tasks if task.status == status]
        if priority:
            tasks = [task for task in tasks if task.priority == priority]
        
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/statistics", response_model=TaskStatistics)
async def get_task_statistics(services=Depends(get_services)):
    """Get task statistics"""
    try:
        _, _, task_service, _ = services
        stats = task_service.get_task_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/overdue", response_model=list[TaskResponse])
async def get_overdue_tasks(services=Depends(get_services)):
    """Get overdue tasks"""
    try:
        _, _, task_service, _ = services
        tasks = task_service.get_overdue_tasks()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, services=Depends(get_services)):
    """Get a specific task by ID"""
    try:
        _, _, task_service, _ = services
        task = task_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, services=Depends(get_services)):
    """Update a task"""
    try:
        _, _, task_service, _ = services
        # Filter out None values
        update_data = {k: v for k, v in task_update.dict().items() if v is not None}
        
        task = task_service.update_task(task_id, update_data)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, services=Depends(get_services)):
    """Delete a task"""
    try:
        _, _, task_service, _ = services
        success = task_service.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI-Powered Task Management

@app.post("/tasks/ai-process")
async def process_task_with_ai(request: AIRequest, services=Depends(get_services)):
    """Process natural language task description with AI"""
    try:
        _, openai_service, _, _ = services
        if not openai_service:
            raise HTTPException(status_code=503, detail="OpenAI service not configured")
        
        processed_task = openai_service.process_task_input({"description": request.description})
        return processed_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks/ai-create")
async def create_task_with_ai(request: AIRequest, services=Depends(get_services)):
    """Create a task from natural language description using AI"""
    try:
        google_service, openai_service, task_service, _ = services
        if not openai_service:
            raise HTTPException(status_code=503, detail="OpenAI service not configured")
        
        # Process with AI
        processed_task = openai_service.process_task_input({"description": request.description})
        
        # Create task
        task = task_service.create_task(processed_task)
        
        # Add to Google Sheet if available
        if google_service:
            try:
                google_service.add_task_to_sheet(task)
                return {"task": task, "message": "Task created successfully with AI processing and Google Sheets sync"}
            except Exception as e:
                print(f"Warning: Could not sync to Google Sheets: {str(e)}")
                return {"task": task, "message": "Task created successfully with AI processing (Google Sheets sync failed)"}
        else:
            return {"task": task, "message": "Task created successfully with AI processing (Google Sheets not configured)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}/improvements")
async def get_task_improvements(task_id: int, services=Depends(get_services)):
    """Get AI suggestions for task improvements"""
    try:
        _, openai_service, task_service, _ = services
        if not openai_service:
            raise HTTPException(status_code=503, detail="OpenAI service not configured")
        
        task = task_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        improvements = openai_service.suggest_task_improvements(
            f"{task.title}: {task.description or 'No description'}"
        )
        
        return {"task_id": task_id, "improvements": improvements}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Scheduling Endpoints

@app.post("/schedule/generate")
async def generate_schedule(background_tasks: BackgroundTasks, services=Depends(get_services)):
    """Generate optimal schedule using AI"""
    try:
        google_service, openai_service, task_service, scheduler_service = services
        if not openai_service:
            raise HTTPException(status_code=503, detail="OpenAI service not configured")
        
        # Get pending tasks and filter to prevent message size issues
        pending_tasks = task_service.get_pending_tasks()
        
        if not pending_tasks:
            return {"message": "No pending tasks to schedule"}
        
        # Filter and limit tasks to prevent AI message size errors
        # Sort by priority (descending) and due_date (ascending), then limit to top 10
        filtered_tasks = []
        for task in pending_tasks:
            # Convert task to dict if it's an object
            if hasattr(task, '__dict__'):
                task_dict = {
                    'id': getattr(task, 'id', None),
                    'title': getattr(task, 'title', ''),
                    'description': getattr(task, 'description', ''),
                    'priority': getattr(task, 'priority', 0),
                    'status': getattr(task, 'status', 'pending'),
                    'due_date': getattr(task, 'due_date', None),
                    'estimated_duration': getattr(task, 'estimated_duration', 60)
                }
            else:
                task_dict = task
            
            # Only include tasks that are pending or in progress
            if task_dict.get('status') in ['pending', 'in_progress']:
                filtered_tasks.append(task_dict)
        
        # Sort by priority (descending) and due_date (ascending)
        filtered_tasks.sort(
            key=lambda t: (
                -t.get('priority', 0),  # Higher priority first
                t.get('due_date', '9999-12-31') if t.get('due_date') else '9999-12-31'  # Earlier due date first
            )
        )
        
        # Limit to top 5 tasks to prevent message size issues (reduced from 10)
        filtered_tasks = filtered_tasks[:5]
        
        if not filtered_tasks:
            return {"message": "No suitable tasks to schedule"}
        
        # Get calendar availability if Google service is available
        calendar_events = []
        if google_service:
            try:
                calendar_events = google_service.get_calendar_events()
                # Limit calendar events to prevent message size issues (reduced from 20)
                calendar_events = calendar_events[:10] if calendar_events else []
            except Exception as e:
                print(f"Warning: Could not fetch calendar events: {str(e)}")
        
        # Generate schedule with AI using filtered data
        schedule = openai_service.generate_schedule(
            tasks=filtered_tasks,
            calendar_events=calendar_events,
            current_time=datetime.now()
        )
        
        # Create calendar events in background if Google service is available
        if google_service:
            background_tasks.add_task(
                scheduler_service.create_calendar_events, 
                schedule
            )
        
        return {"schedule": schedule, "message": "Schedule generated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schedule", response_model=list[ScheduleResponse])
async def get_schedule(days_ahead: int = 7, services=Depends(get_services)):
    """Get scheduled tasks"""
    try:
        _, _, _, scheduler_service = services
        schedules = scheduler_service.get_schedule(days_ahead)
        return schedules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule", response_model=ScheduleResponse)
async def create_schedule(schedule_data: ScheduleCreate, services=Depends(get_services)):
    """Create a manual schedule entry"""
    try:
        google_service, _, task_service, scheduler_service = services
        # Check for conflicts
        conflicts = scheduler_service.get_conflicts(
            schedule_data.scheduled_start, 
            schedule_data.scheduled_end
        )
        
        if conflicts:
            return JSONResponse(
                status_code=409,
                content={"message": "Schedule conflict detected", "conflicts": conflicts}
            )
        
        # Create calendar event if Google service is available
        calendar_event_id = None
        if google_service:
            try:
                event_data = {
                    'summary': f'Task {schedule_data.task_id}',
                    'start': {
                        'dateTime': schedule_data.scheduled_start.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'dateTime': schedule_data.scheduled_end.isoformat(),
                        'timeZone': 'UTC',
                    },
                }
                
                calendar_event = google_service.create_calendar_event(event_data)
                calendar_event_id = calendar_event.get('id')
            except Exception as e:
                print(f"Warning: Could not create calendar event: {str(e)}")
        
        # Save to database
        schedule_entry = Schedule(
            task_id=schedule_data.task_id,
            scheduled_start=schedule_data.scheduled_start,
            scheduled_end=schedule_data.scheduled_end,
            calendar_event_id=calendar_event_id
        )
        
        task_service.db.add(schedule_entry)
        task_service.db.commit()
        task_service.db.refresh(schedule_entry)
        
        return schedule_entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/schedule/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(schedule_id: int, schedule_update: ScheduleUpdate, services=Depends(get_services)):
    """Update a schedule entry"""
    try:
        _, _, _, scheduler_service = services
        update_data = {k: v for k, v in schedule_update.dict().items() if v is not None}
        schedule = scheduler_service.update_schedule(schedule_id, update_data)
        
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        
        return schedule
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/schedule/{schedule_id}")
async def delete_schedule(schedule_id: int, services=Depends(get_services)):
    """Delete a schedule entry"""
    try:
        _, _, _, scheduler_service = services
        success = scheduler_service.delete_schedule(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return {"message": "Schedule deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule/{schedule_id}/complete")
async def complete_schedule(schedule_id: int, services=Depends(get_services)):
    """Mark a scheduled task as completed"""
    try:
        _, _, _, scheduler_service = services
        success = scheduler_service.mark_schedule_completed(schedule_id)
        if not success:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return {"message": "Schedule marked as completed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Google Integration Endpoints

@app.post("/sync/sheets")
async def sync_tasks_from_sheet(services=Depends(get_services)):
    """Sync tasks from Google Sheet to database"""
    try:
        google_service, _, task_service, _ = services
        if not google_service:
            raise HTTPException(status_code=503, detail="Google Sheets service not configured")
        
        sheet_data = google_service.read_sheet()
        synced_tasks = task_service.sync_tasks(sheet_data)
        return {"message": f"Synced {len(synced_tasks)} tasks from Google Sheet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/events")
async def get_calendar_events(days_ahead: int = 7, services=Depends(get_services)):
    """Get calendar events"""
    try:
        google_service, _, _, _ = services
        if not google_service:
            raise HTTPException(status_code=503, detail="Google Calendar service not configured")
        
        events = google_service.get_calendar_events(days_ahead)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Email and Communication Endpoints

@app.post("/email/send")
async def send_email(email_request: EmailRequest, gmail_service=Depends(get_gmail_service)):
    """Send an email using Gmail service"""
    try:
        result = gmail_service.send_email(
            subject=email_request.subject,
            body=email_request.body,
            to=email_request.to
        )
        return {"message": "Email sent successfully", "message_id": result.get('id')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reminders/send")
async def send_reminder(reminder_request: ReminderRequest, services=Depends(get_services), gmail_service=Depends(get_gmail_service)):
    """Send a reminder email for a task using Gmail service"""
    try:
        _, openai_service, task_service, _ = services
        if not openai_service:
            raise HTTPException(status_code=503, detail="OpenAI service not configured")
        
        task = task_service.get_task(reminder_request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Generate reminder email with AI
        email_content = openai_service.generate_reminder_email(task)
        
        # Add custom message if provided
        if reminder_request.message:
            email_content = f"{reminder_request.message}\n\n{email_content}"
        
        # Send email using Gmail service
        result = gmail_service.send_email(
            subject=f"Reminder: {task.title}",
            body=email_content,
            to=os.getenv('DEFAULT_EMAIL', 'your-email@gmail.com')
        )
        
        return {"message": "Reminder sent successfully", "message_id": result.get('id')}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/email/test")
async def test_email_connection(gmail_service=Depends(get_gmail_service)):
    """Test Gmail connection"""
    try:
        success = gmail_service.test_connection()
        if success:
            return {"message": "Gmail connection successful"}
        else:
            raise HTTPException(status_code=500, detail="Gmail connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Productivity Analysis

@app.get("/productivity/analyze")
async def analyze_productivity(time_period: str = "week", services=Depends(get_services)):
    """Analyze productivity patterns"""
    try:
        _, openai_service, task_service, _ = services
        if not openai_service:
            raise HTTPException(status_code=503, detail="OpenAI service not configured")
        
        # Get completed tasks for the period
        if time_period == "day":
            days = 1
        elif time_period == "week":
            days = 7
        elif time_period == "month":
            days = 30
        else:
            raise HTTPException(status_code=400, detail="Invalid time period")
        
        cutoff_date = datetime.now() - timedelta(days=days)
        completed_tasks = task_service.db.query(Task).filter(
            Task.status == 'completed',
            Task.updated_at >= cutoff_date
        ).all()
        
        # Convert to dict for analysis
        tasks_data = [task_service._task_to_dict(task) for task in completed_tasks]
        
        # Analyze with AI
        analysis = openai_service.analyze_productivity(tasks_data, time_period)
        
        return {
            "time_period": time_period,
            "completed_tasks_count": len(completed_tasks),
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(app, host=host, port=port) 