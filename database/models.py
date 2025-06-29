from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=1)  # 1-5 scale
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    due_date = Column(DateTime)
    estimated_duration = Column(Integer)  # minutes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    sheet_row_id = Column(Integer)  # Reference to Google Sheet row
    
    # Relationship
    schedules = relationship("Schedule", back_populates="task")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    calendar_event_id = Column(String(255))  # Google Calendar event ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_completed = Column(Boolean, default=False)
    
    # Relationship
    task = relationship("Task", back_populates="schedules") 