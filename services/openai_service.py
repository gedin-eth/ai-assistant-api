import openai
from datetime import datetime, timedelta
import json
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class OpenAIService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        
        self.client = openai.OpenAI(api_key=api_key)

    def generate_schedule(self, tasks: List[Dict], calendar_events: List[Dict], current_time: datetime):
        """Generate optimal schedule using GPT-4"""
        system_prompt = """
        You are an AI scheduling assistant. Given a list of tasks and existing calendar events,
        create an optimal schedule that maximizes productivity while respecting time constraints.
        
        Consider:
        - Task priorities and deadlines
        - Estimated durations
        - Existing calendar commitments
        - Optimal work patterns (avoid context switching)
        - Break times and energy levels
        - Time zones and working hours
        
        Return a JSON array of scheduled time blocks with start_time and end_time in ISO format.
        """
        
        user_prompt = f"""
        Current time: {current_time.isoformat()}
        
        Tasks to schedule:
        {json.dumps(tasks, indent=2, default=str)}
        
        Existing calendar events:
        {json.dumps(calendar_events, indent=2, default=str)}
        
        Please create an optimal schedule for the next 7 days, considering:
        1. High priority tasks should be scheduled first
        2. Respect existing calendar commitments
        3. Include breaks between tasks
        4. Group similar tasks together when possible
        5. Consider estimated durations
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=[{
                    "name": "create_schedule",
                    "description": "Create an optimal schedule",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "schedule": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "task_id": {"type": "integer"},
                                        "start_time": {"type": "string", "format": "date-time"},
                                        "end_time": {"type": "string", "format": "date-time"},
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "priority": {"type": "integer"}
                                    },
                                    "required": ["task_id", "start_time", "end_time", "title"]
                                }
                            }
                        },
                        "required": ["schedule"]
                    }
                }],
                function_call={"name": "create_schedule"}
            )
            
            schedule_data = json.loads(response.choices[0].message.function_call.arguments)
            return schedule_data['schedule']
        except Exception as e:
            raise Exception(f"Error generating schedule with OpenAI: {str(e)}")

    def process_task_input(self, task_data: Dict):
        """Process natural language task input"""
        system_prompt = """
        You are a task processing assistant. Convert natural language task descriptions
        into structured task data with appropriate priority, estimated duration, and due dates.
        
        Priority levels:
        1 - Low priority, can be done anytime
        2 - Normal priority
        3 - Important, should be done soon
        4 - High priority, urgent
        5 - Critical, must be done immediately
        
        Duration should be estimated in minutes.
        Due dates should be in ISO format if specified.
        """
        
        user_prompt = f"""
        Process this task input: {task_data.get('description', '')}
        
        Extract:
        - Title (concise and clear)
        - Description (detailed if provided)
        - Priority (1-5 based on urgency and importance)
        - Estimated duration in minutes
        - Due date if mentioned
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=[{
                    "name": "process_task",
                    "description": "Process task input",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {"type": "integer", "minimum": 1, "maximum": 5},
                            "estimated_duration": {"type": "integer", "minimum": 1},
                            "due_date": {"type": "string", "format": "date-time"}
                        },
                        "required": ["title", "priority"]
                    }
                }],
                function_call={"name": "process_task"}
            )
            
            return json.loads(response.choices[0].message.function_call.arguments)
        except Exception as e:
            raise Exception(f"Error processing task input with OpenAI: {str(e)}")

    def generate_reminder_email(self, task):
        """Generate reminder email content"""
        prompt = f"""
        Generate a friendly and motivating reminder email for this task:
        
        Title: {task.title}
        Description: {task.description or 'No description provided'}
        Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'No due date'}
        Priority: {task.priority}/5
        
        Make the email:
        - Friendly and encouraging
        - Include relevant context about the task
        - Mention the priority and due date if applicable
        - Keep it concise but motivating
        - Professional but not too formal
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating reminder email with OpenAI: {str(e)}")

    def analyze_productivity(self, completed_tasks: List[Dict], time_period: str = "week"):
        """Analyze productivity patterns and provide insights"""
        system_prompt = """
        You are a productivity analyst. Analyze completed tasks and provide insights about:
        - Productivity patterns
        - Time management effectiveness
        - Areas for improvement
        - Recommendations for better scheduling
        """
        
        user_prompt = f"""
        Analyze these completed tasks for the {time_period}:
        {json.dumps(completed_tasks, indent=2, default=str)}
        
        Provide insights on:
        1. Productivity patterns
        2. Time management effectiveness
        3. Areas for improvement
        4. Recommendations for better scheduling
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error analyzing productivity with OpenAI: {str(e)}")

    def suggest_task_improvements(self, task_description: str):
        """Suggest improvements for task execution"""
        prompt = f"""
        Analyze this task and suggest improvements for better execution:
        
        Task: {task_description}
        
        Provide suggestions for:
        1. Breaking down the task into smaller subtasks
        2. Time estimation improvements
        3. Priority assessment
        4. Potential blockers or dependencies
        5. Tools or resources that might help
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error suggesting task improvements with OpenAI: {str(e)}") 