from datetime import datetime
from src.models.user import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Task Properties
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    category = db.Column(db.String(50))
    estimated_duration = db.Column(db.Integer)  # in minutes
    actual_duration = db.Column(db.Integer)  # in minutes
    difficulty = db.Column(db.Integer, default=1)  # 1-5 scale
    
    # Status and Progress
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    
    # Gamification
    xp_reward = db.Column(db.Integer, default=10)
    bonus_xp = db.Column(db.Integer, default=0)
    
    # AI Features
    ai_suggested_priority = db.Column(db.String(20))
    ai_suggested_category = db.Column(db.String(50))
    ai_suggested_duration = db.Column(db.Integer)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    
    # Self-referential relationship for subtasks
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]), lazy=True)
    
    # Task dependencies
    dependencies = db.relationship('TaskDependency', 
                                 foreign_keys='TaskDependency.task_id',
                                 backref='task', lazy=True, cascade='all, delete-orphan')
    dependents = db.relationship('TaskDependency',
                               foreign_keys='TaskDependency.depends_on_id',
                               backref='depends_on_task', lazy=True, cascade='all, delete-orphan')

    def mark_completed(self):
        """Mark task as completed and update user stats"""
        if self.status != 'completed':
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
            self.progress = 100
            
            # Update user XP and streak
            if self.user:
                self.user.add_xp(self.xp_reward + self.bonus_xp)
                self.user.update_streak()
            
            return True
        return False

    def calculate_xp_reward(self):
        """Calculate XP reward based on task properties"""
        base_xp = 10
        
        # Priority multiplier
        priority_multipliers = {'low': 1, 'medium': 1.2, 'high': 1.5, 'urgent': 2}
        multiplier = priority_multipliers.get(self.priority, 1)
        
        # Difficulty bonus
        difficulty_bonus = (self.difficulty - 1) * 5
        
        # Duration bonus (longer tasks get more XP)
        duration_bonus = (self.estimated_duration or 30) // 30 * 2
        
        self.xp_reward = int(base_xp * multiplier + difficulty_bonus + duration_bonus)

    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status != 'completed':
            return datetime.utcnow() > self.due_date
        return False

    def get_completion_percentage(self):
        """Get overall completion percentage including subtasks"""
        if not self.subtasks:
            return self.progress
        
        total_progress = self.progress
        for subtask in self.subtasks:
            total_progress += subtask.get_completion_percentage()
        
        return total_progress // (len(self.subtasks) + 1)

    def __repr__(self):
        return f'<Task {self.title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'priority': self.priority,
            'category': self.category,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'difficulty': self.difficulty,
            'status': self.status,
            'progress': self.progress,
            'xp_reward': self.xp_reward,
            'bonus_xp': self.bonus_xp,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'parent_task_id': self.parent_task_id,
            'is_overdue': self.is_overdue(),
            'completion_percentage': self.get_completion_percentage()
        }


class TaskDependency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    depends_on_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TaskDependency {self.task_id} depends on {self.depends_on_id}>'

