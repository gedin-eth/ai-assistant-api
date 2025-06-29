from sqlalchemy.orm import Session
from database.models import Task, Schedule
from database.database import SessionLocal
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class TaskService:
    def __init__(self):
        self.db = SessionLocal()

    def create_task(self, task_data: Dict) -> Task:
        """Create a new task"""
        try:
            # Convert due_date string to datetime if provided
            due_date = None
            if task_data.get('due_date'):
                if isinstance(task_data['due_date'], str):
                    due_date = datetime.fromisoformat(task_data['due_date'].replace('Z', '+00:00'))
                else:
                    due_date = task_data['due_date']

            task = Task(
                title=task_data['title'],
                description=task_data.get('description', ''),
                priority=task_data.get('priority', 1),
                status='pending',
                due_date=due_date,
                estimated_duration=task_data.get('estimated_duration')
            )
            
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            
            return task
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error creating task: {str(e)}")

    def get_task(self, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return self.db.query(Task).order_by(Task.priority.desc(), Task.due_date.asc()).all()

    def get_pending_tasks(self) -> List[Dict]:
        """Get pending tasks for scheduling"""
        tasks = self.db.query(Task).filter(
            Task.status.in_(['pending', 'in_progress'])
        ).order_by(Task.priority.desc(), Task.due_date.asc()).all()
        
        return [self._task_to_dict(task) for task in tasks]

    def get_tasks_by_status(self, status: str) -> List[Task]:
        """Get tasks by status"""
        return self.db.query(Task).filter(Task.status == status).all()

    def get_overdue_tasks(self) -> List[Task]:
        """Get overdue tasks"""
        now = datetime.now()
        return self.db.query(Task).filter(
            Task.due_date < now,
            Task.status.in_(['pending', 'in_progress'])
        ).all()

    def update_task(self, task_id: int, update_data: Dict) -> Optional[Task]:
        """Update a task"""
        try:
            task = self.get_task(task_id)
            if not task:
                return None
            
            # Update fields
            for key, value in update_data.items():
                if hasattr(task, key):
                    if key == 'due_date' and isinstance(value, str):
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    setattr(task, key, value)
            
            task.updated_at = datetime.now()
            self.db.commit()
            self.db.refresh(task)
            
            return task
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error updating task: {str(e)}")

    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        try:
            task = self.get_task(task_id)
            if not task:
                return False
            
            self.db.delete(task)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error deleting task: {str(e)}")

    def sync_tasks(self, sheet_data: List[List]) -> List[Task]:
        """Sync tasks from Google Sheet to database"""
        synced_tasks = []
        
        try:
            # Skip header row if it exists
            start_index = 1 if sheet_data and len(sheet_data) > 0 else 0
            
            for i, row in enumerate(sheet_data[start_index:], start=start_index + 1):
                if len(row) >= 4:  # Minimum required fields
                    # Check if task already exists by title and description
                    existing_task = self.db.query(Task).filter(
                        Task.title == row[0],
                        Task.description == (row[1] if len(row) > 1 else '')
                    ).first()
                    
                    if not existing_task:
                        # Create new task
                        task_data = {
                            'title': row[0],
                            'description': row[1] if len(row) > 1 else '',
                            'priority': int(row[2]) if len(row) > 2 and row[2].isdigit() else 1,
                            'status': row[3] if len(row) > 3 else 'pending',
                            'due_date': self._parse_date(row[4]) if len(row) > 4 and row[4] else None,
                            'estimated_duration': int(row[5]) if len(row) > 5 and row[5].isdigit() else None,
                            'sheet_row_id': i
                        }
                        
                        task = self.create_task(task_data)
                        synced_tasks.append(task)
            
            self.db.commit()
            return synced_tasks
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error syncing tasks: {str(e)}")

    def get_task_statistics(self) -> Dict:
        """Get task statistics"""
        total_tasks = self.db.query(Task).count()
        pending_tasks = self.db.query(Task).filter(Task.status == 'pending').count()
        completed_tasks = self.db.query(Task).filter(Task.status == 'completed').count()
        overdue_tasks = len(self.get_overdue_tasks())
        
        # Priority distribution
        priority_stats = {}
        for priority in range(1, 6):
            count = self.db.query(Task).filter(Task.priority == priority).count()
            priority_stats[f"priority_{priority}"] = count
        
        return {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'priority_distribution': priority_stats
        }

    def get_recent_tasks(self, days: int = 7) -> List[Task]:
        """Get tasks created in the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return self.db.query(Task).filter(
            Task.created_at >= cutoff_date
        ).order_by(Task.created_at.desc()).all()

    def _task_to_dict(self, task: Task) -> Dict:
        """Convert task object to dictionary"""
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'estimated_duration': task.estimated_duration,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.updated_at.isoformat() if task.updated_at else None
        }

    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_string:
            return None
        
        try:
            # Try different date formats
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            
            # If none of the formats work, try ISO format
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except Exception:
            return None

    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'db'):
            self.db.close() 