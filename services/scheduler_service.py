from sqlalchemy.orm import Session
from database.models import Task, Schedule
from database.database import SessionLocal
from services.google_service import GoogleService
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import schedule
import time
import json
import os

class SchedulerService:
    def __init__(self, google_service=None):
        self.db = SessionLocal()
        self.google_service = google_service
        self.running = False

    async def run_scheduler(self):
        """Run the background scheduler"""
        self.running = True
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(60)

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False

    async def create_calendar_events(self, schedule_data: List[Dict]):
        """Create calendar events for scheduled tasks"""
        created_events = []
        
        try:
            for item in schedule_data:
                task_id = item.get('task_id')
                start_time = item.get('start_time')
                end_time = item.get('end_time')
                title = item.get('title', 'Scheduled Task')
                
                if not all([task_id, start_time, end_time]):
                    continue
                
                # Parse datetime strings
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                
                # Create calendar event
                event_data = {
                    'summary': title,
                    'description': f'Task ID: {task_id}',
                    'start': {
                        'dateTime': start_dt.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'dateTime': end_dt.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 15},
                            {'method': 'popup', 'minutes': 10},
                        ],
                    },
                }
                
                # Create event in Google Calendar if available
                calendar_event_id = None
                if self.google_service:
                    try:
                        calendar_event = self.google_service.create_calendar_event(event_data)
                        calendar_event_id = calendar_event.get('id')
                    except Exception as e:
                        print(f"Warning: Could not create calendar event: {str(e)}")
                
                # Save to database
                schedule_entry = Schedule(
                    task_id=task_id,
                    scheduled_start=start_dt,
                    scheduled_end=end_dt,
                    calendar_event_id=calendar_event_id
                )
                
                self.db.add(schedule_entry)
                created_events.append({
                    'task_id': task_id,
                    'calendar_event_id': calendar_event_id,
                    'start_time': start_dt.isoformat(),
                    'end_time': end_dt.isoformat()
                })
            
            self.db.commit()
            return created_events
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error creating calendar events: {str(e)}")

    def get_schedule(self, days_ahead: int = 7) -> List[Dict]:
        """Get scheduled tasks for the next N days"""
        end_date = datetime.now() + timedelta(days=days_ahead)
        
        schedules = self.db.query(Schedule).filter(
            Schedule.scheduled_start >= datetime.now(),
            Schedule.scheduled_start <= end_date
        ).order_by(Schedule.scheduled_start.asc()).all()
        
        return [self._schedule_to_dict(schedule) for schedule in schedules]

    def update_schedule(self, schedule_id: int, update_data: Dict) -> Optional[Schedule]:
        """Update a schedule entry"""
        try:
            schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
            if not schedule:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(schedule, key):
                    if key in ['scheduled_start', 'scheduled_end'] and isinstance(value, str):
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    setattr(schedule, key, value)
            
            # Update calendar event if times changed
            if 'scheduled_start' in update_data or 'scheduled_end' in update_data:
                self._update_calendar_event(schedule)
            
            self.db.commit()
            self.db.refresh(schedule)
            
            return schedule
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error updating schedule: {str(e)}")

    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a schedule entry"""
        try:
            schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
            if not schedule:
                return False
            
            # Delete from Google Calendar if exists
            if schedule.calendar_event_id:
                self._delete_calendar_event(schedule.calendar_event_id)
            
            self.db.delete(schedule)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting schedule: {str(e)}")

    def mark_schedule_completed(self, schedule_id: int) -> bool:
        """Mark a scheduled task as completed"""
        try:
            schedule = self.db.query(Schedule).filter(Schedule.id == schedule_id).first()
            if not schedule:
                return False
            
            schedule.is_completed = True
            
            # Update task status
            task = self.db.query(Task).filter(Task.id == schedule.task_id).first()
            if task:
                task.status = 'completed'
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error marking schedule completed: {str(e)}")

    def get_conflicts(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Check for scheduling conflicts"""
        conflicts = self.db.query(Schedule).filter(
            Schedule.scheduled_start < end_time,
            Schedule.scheduled_end > start_time
        ).all()
        
        return [self._schedule_to_dict(conflict) for conflict in conflicts]

    def _daily_schedule_check(self):
        """Daily schedule check - runs at 9 AM"""
        try:
            # Get today's schedule
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            today_schedules = self.db.query(Schedule).filter(
                Schedule.scheduled_start >= today_start,
                Schedule.scheduled_start < today_end
            ).all()
            
            # Send summary email
            if today_schedules:
                self._send_daily_summary(today_schedules)
        except Exception as e:
            print(f"Error in daily schedule check: {str(e)}")

    def _evening_review(self):
        """Evening review - runs at 6 PM"""
        try:
            # Get completed tasks for today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            completed_schedules = self.db.query(Schedule).filter(
                Schedule.scheduled_start >= today_start,
                Schedule.scheduled_start < today_end,
                Schedule.is_completed == True
            ).all()
            
            # Send evening review
            self._send_evening_review(completed_schedules)
        except Exception as e:
            print(f"Error in evening review: {str(e)}")

    def _check_overdue_tasks(self):
        """Check for overdue tasks every 30 minutes"""
        try:
            overdue_tasks = self.db.query(Task).filter(
                Task.due_date < datetime.now(),
                Task.status.in_(['pending', 'in_progress'])
            ).all()
            
            if overdue_tasks:
                self._send_overdue_notification(overdue_tasks)
        except Exception as e:
            print(f"Error checking overdue tasks: {str(e)}")

    def _send_daily_summary(self, schedules: List[Schedule]):
        """Send daily schedule summary"""
        try:
            if not self.google_service:
                print("Google service not available - skipping daily summary email")
                return
                
            summary = "Today's Schedule:\n\n"
            for schedule in schedules:
                task = self.db.query(Task).filter(Task.id == schedule.task_id).first()
                if task:
                    summary += f"• {schedule.scheduled_start.strftime('%H:%M')} - {task.title} (Priority: {task.priority})\n"
            
            self.google_service.send_email(
                subject="Daily Schedule Summary",
                body=summary,
                to=os.getenv('DEFAULT_EMAIL', 'your-email@gmail.com')
            )
        except Exception as e:
            print(f"Error sending daily summary: {str(e)}")

    def _send_evening_review(self, completed_schedules: List[Schedule]):
        """Send evening review"""
        try:
            if not completed_schedules:
                return
            
            if not self.google_service:
                print("Google service not available - skipping evening review email")
                return
                
            review = "Evening Review - Completed Tasks:\n\n"
            for schedule in completed_schedules:
                task = self.db.query(Task).filter(Task.id == schedule.task_id).first()
                if task:
                    review += f"✅ {task.title}\n"
            
            self.google_service.send_email(
                subject="Evening Review",
                body=review,
                to=os.getenv('DEFAULT_EMAIL', 'your-email@gmail.com')
            )
        except Exception as e:
            print(f"Error sending evening review: {str(e)}")

    def _send_overdue_notification(self, overdue_tasks: List[Task]):
        """Send overdue task notification"""
        try:
            if not self.google_service:
                print("Google service not available - skipping overdue notification email")
                return
                
            notification = "Overdue Tasks Alert:\n\n"
            for task in overdue_tasks:
                notification += f"⚠️ {task.title} (Due: {task.due_date.strftime('%Y-%m-%d %H:%M')})\n"
            
            self.google_service.send_email(
                subject="Overdue Tasks Alert",
                body=notification,
                to=os.getenv('DEFAULT_EMAIL', 'your-email@gmail.com')
            )
        except Exception as e:
            print(f"Error sending overdue notification: {str(e)}")

    def _update_calendar_event(self, schedule: Schedule):
        """Update calendar event in Google Calendar"""
        try:
            if not schedule.calendar_event_id or not self.google_service:
                return
            
            event_data = {
                'start': {
                    'dateTime': schedule.scheduled_start.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': schedule.scheduled_end.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            self.google_service.calendar_service.events().update(
                calendarId='primary',
                eventId=schedule.calendar_event_id,
                body=event_data
            ).execute()
        except Exception as e:
            print(f"Error updating calendar event: {str(e)}")

    def _delete_calendar_event(self, event_id: str):
        """Delete calendar event from Google Calendar"""
        try:
            if not self.google_service:
                return
                
            self.google_service.calendar_service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
        except Exception as e:
            print(f"Error deleting calendar event: {str(e)}")

    def _schedule_to_dict(self, schedule: Schedule) -> Dict:
        """Convert schedule object to dictionary"""
        return {
            'id': schedule.id,
            'task_id': schedule.task_id,
            'scheduled_start': schedule.scheduled_start.isoformat() if schedule.scheduled_start else None,
            'scheduled_end': schedule.scheduled_end.isoformat() if schedule.scheduled_end else None,
            'calendar_event_id': schedule.calendar_event_id,
            'is_completed': schedule.is_completed,
            'created_at': schedule.created_at.isoformat() if schedule.created_at else None
        }

    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'db'):
            self.db.close() 