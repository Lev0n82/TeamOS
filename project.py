from datetime import datetime
from src.models.user import db

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    
    # Project Properties
    status = db.Column(db.String(20), default='active')  # active, completed, archived, cancelled
    priority = db.Column(db.String(20), default='medium')
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color for UI
    
    # Team Collaboration
    is_team_project = db.Column(db.Boolean, default=False)
    visibility = db.Column(db.String(20), default='private')  # private, team, public
    
    # Progress Tracking
    progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    budget = db.Column(db.Float)
    spent_budget = db.Column(db.Float, default=0)
    
    # Relationships
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    members = db.relationship('ProjectMember', backref='project', lazy=True, cascade='all, delete-orphan')

    def calculate_progress(self):
        """Calculate project progress based on completed tasks"""
        if not self.tasks:
            return 0
        
        total_tasks = len(self.tasks)
        completed_tasks = len([task for task in self.tasks if task.status == 'completed'])
        
        self.progress = int((completed_tasks / total_tasks) * 100)
        return self.progress

    def get_task_stats(self):
        """Get comprehensive task statistics for the project"""
        total_tasks = len(self.tasks)
        completed_tasks = len([task for task in self.tasks if task.status == 'completed'])
        in_progress_tasks = len([task for task in self.tasks if task.status == 'in_progress'])
        overdue_tasks = len([task for task in self.tasks if task.is_overdue()])
        
        return {
            'total': total_tasks,
            'completed': completed_tasks,
            'in_progress': in_progress_tasks,
            'overdue': overdue_tasks,
            'pending': total_tasks - completed_tasks - in_progress_tasks
        }

    def is_overdue(self):
        """Check if project is overdue"""
        if self.end_date and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.end_date
        return False

    def add_member(self, user_id, role='member'):
        """Add a member to the project"""
        existing_member = ProjectMember.query.filter_by(
            project_id=self.id, user_id=user_id
        ).first()
        
        if not existing_member:
            member = ProjectMember(
                project_id=self.id,
                user_id=user_id,
                role=role
            )
            db.session.add(member)
            return member
        return existing_member

    def __repr__(self):
        return f'<Project {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'priority': self.priority,
            'color': self.color,
            'is_team_project': self.is_team_project,
            'visibility': self.visibility,
            'progress': self.progress,
            'budget': self.budget,
            'spent_budget': self.spent_budget,
            'owner_id': self.owner_id,
            'team_id': self.team_id,
            'is_overdue': self.is_overdue(),
            'task_stats': self.get_task_stats()
        }


class ProjectMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # owner, admin, member, viewer
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    permissions = db.Column(db.JSON, default={})

    def __repr__(self):
        return f'<ProjectMember {self.user_id} in {self.project_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'permissions': self.permissions
        }

