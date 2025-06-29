from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class TaskInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: int = Field(1, ge=1, le=5)
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, gt=0)

class AIRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=1000)

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: int
    status: str
    due_date: Optional[datetime]
    estimated_duration: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = Field(None, pattern='^(pending|in_progress|completed|cancelled)$')
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = Field(None, gt=0)

class ScheduleResponse(BaseModel):
    id: int
    task_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    calendar_event_id: Optional[str]
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ScheduleCreate(BaseModel):
    task_id: int
    scheduled_start: datetime
    scheduled_end: datetime

class ScheduleUpdate(BaseModel):
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    is_completed: Optional[bool] = None

class TaskStatistics(BaseModel):
    total_tasks: int
    pending_tasks: int
    completed_tasks: int
    overdue_tasks: int
    completion_rate: float
    priority_distribution: dict

class EmailRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1)
    to: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

class ReminderRequest(BaseModel):
    task_id: int
    message: Optional[str] = None

class ProductivityAnalysis(BaseModel):
    time_period: str = Field(..., pattern='^(day|week|month)$')
    insights: str
    recommendations: List[str] 