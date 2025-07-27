from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # CARROT Personality Settings
    carrot_attitude_level = db.Column(db.Integer, default=3)  # 1-5 scale
    carrot_personality_level = db.Column(db.Integer, default=1)
    carrot_mood = db.Column(db.String(50), default='neutral')
    
    # Gamification Stats
    total_xp = db.Column(db.Integer, default=0)
    productivity_points = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_task_completion = db.Column(db.DateTime)
    
    # User Preferences
    timezone = db.Column(db.String(50), default='UTC')
    notification_preferences = db.Column(db.JSON, default={})
    theme_preferences = db.Column(db.JSON, default={})
    
    # Relationships
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy=True, cascade='all, delete-orphan')
    team_memberships = db.relationship('TeamMember', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_streak(self):
        """Update user's task completion streak"""
        now = datetime.utcnow()
        if self.last_task_completion:
            days_diff = (now.date() - self.last_task_completion.date()).days
            if days_diff == 1:
                self.current_streak += 1
            elif days_diff > 1:
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_task_completion = now

    def add_xp(self, amount):
        """Add XP and check for personality level ups"""
        self.total_xp += amount
        new_level = min(10, (self.total_xp // 1000) + 1)
        if new_level > self.carrot_personality_level:
            self.carrot_personality_level = new_level
            return True  # Level up occurred
        return False

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'carrot_attitude_level': self.carrot_attitude_level,
            'carrot_personality_level': self.carrot_personality_level,
            'carrot_mood': self.carrot_mood,
            'total_xp': self.total_xp,
            'productivity_points': self.productivity_points,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'timezone': self.timezone
        }
