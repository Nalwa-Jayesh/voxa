"""Task management for the voice assistant."""

import time
import threading
from datetime import datetime
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Callable

from ..utils.logging_config import logger
from ..utils.constants import TaskType

@dataclass
class Task:
    """Represents a task in the system."""
    id: str
    type: TaskType
    content: str
    scheduled_time: Optional[datetime] = None
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class TaskManager:
    """Advanced task management with scheduling and persistence."""
    
    def __init__(self, state_manager):
        """Initialize the task manager."""
        self.state_manager = state_manager
        self.active_timers: Dict[str, threading.Timer] = {}
        self.tasks: Dict[str, Task] = {}
        self.task_callbacks: List[Callable] = []
        self.load_tasks()
        
        # Start task scheduler
        self.scheduler_thread = threading.Thread(target=self._task_scheduler, daemon=True)
        self.scheduler_running = True
        self.scheduler_thread.start()
    
    def add_task_callback(self, callback: Callable):
        """Add callback for task completion."""
        self.task_callbacks.append(callback)
    
    def load_tasks(self):
        """Load tasks from state."""
        tasks_data = self.state_manager.get('tasks', {})
        for task_id, task_data in tasks_data.items():
            try:
                # Convert scheduled_time string back to datetime if needed
                if isinstance(task_data.get('scheduled_time'), str):
                    task_data['scheduled_time'] = datetime.fromisoformat(task_data['scheduled_time'])
                
                task = Task(**task_data)
                self.tasks[task_id] = task
                
                # Reschedule active tasks
                if not task.completed and task.scheduled_time:
                    if task.scheduled_time > datetime.now():
                        self._schedule_task(task)
            except Exception as e:
                logger.error(f"Failed to load task {task_id}: {e}")
    
    def save_tasks(self):
        """Save tasks to state."""
        tasks_data = {}
        for task_id, task in self.tasks.items():
            task_dict = asdict(task)
            # Convert datetime to string for JSON serialization
            if isinstance(task_dict['scheduled_time'], datetime):
                task_dict['scheduled_time'] = task_dict['scheduled_time'].isoformat()
            if isinstance(task_dict['created_at'], datetime):
                task_dict['created_at'] = task_dict['created_at'].isoformat()
            tasks_data[task_id] = task_dict
        
        self.state_manager.set('tasks', tasks_data)
    
    def create_task(self, task_type: TaskType, content: str, **kwargs) -> str:
        """Create a new task."""
        task_id = f"task_{int(time.time() * 1000)}"
        
        task = Task(
            id=task_id,
            type=task_type,
            content=content,
            **kwargs
        )
        
        self.tasks[task_id] = task
        
        if task.scheduled_time:
            self._schedule_task(task)
        
        self.save_tasks()
        return task_id
    
    def _schedule_task(self, task: Task):
        """Schedule a task for execution."""
        if task.scheduled_time <= datetime.now():
            return
            
        delay = (task.scheduled_time - datetime.now()).total_seconds()
        
        timer = threading.Timer(delay, self._execute_task, args=[task.id])
        self.active_timers[task.id] = timer
        timer.start()
        
        logger.info(f"Scheduled task {task.id} for {task.scheduled_time}")
    
    def _execute_task(self, task_id: str):
        """Execute a scheduled task."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.completed = True
            
            # Notify callbacks
            for callback in self.task_callbacks:
                try:
                    callback(task)
                except Exception as e:
                    logger.error(f"Task callback error: {e}")
            
            self.save_tasks()
            
        if task_id in self.active_timers:
            del self.active_timers[task_id]
    
    def _task_scheduler(self):
        """Background task scheduler."""
        while self.scheduler_running:
            try:
                current_time = datetime.now()
                
                # Check for overdue tasks
                for task_id, task in list(self.tasks.items()):
                    if (not task.completed and 
                        task.scheduled_time and 
                        task.scheduled_time <= current_time and
                        task_id not in self.active_timers):
                        
                        self._execute_task(task_id)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Task scheduler error: {e}")
                time.sleep(5)
    
    def stop_scheduler(self):
        """Stop the task scheduler."""
        self.scheduler_running = False
        for timer in self.active_timers.values():
            timer.cancel() 