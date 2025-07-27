from datetime import datetime
from src.models.user import db

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Icon identifier
    category = db.Column(db.String(50))  # productivity, streak, social, etc.
    
    # Requirements
    requirement_type = db.Column(db.String(50))  # tasks_completed, streak_days, xp_earned, etc.
    requirement_value = db.Column(db.Integer)
    
    # Rewards
    xp_reward = db.Column(db.Integer, default=0)
    productivity_points_reward = db.Column(db.Integer, default=0)
    
    # Metadata
    is_hidden = db.Column(db.Boolean, default=False)  # Hidden until unlocked
    is_repeatable = db.Column(db.Boolean, default=False)
    rarity = db.Column(db.String(20), default='common')  # common, rare, epic, legendary
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Achievement {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'requirement_type': self.requirement_type,
            'requirement_value': self.requirement_value,
            'xp_reward': self.xp_reward,
            'productivity_points_reward': self.productivity_points_reward,
            'is_hidden': self.is_hidden,
            'is_repeatable': self.is_repeatable,
            'rarity': self.rarity
        }


class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Integer, default=0)  # For tracking progress towards achievement
    
    # Relationships
    achievement = db.relationship('Achievement', backref='user_achievements')

    def __repr__(self):
        return f'<UserAchievement {self.user_id}:{self.achievement_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'progress': self.progress,
            'achievement': self.achievement.to_dict() if self.achievement else None
        }


class CarrotPersonality(db.Model):
    """Stores CARROT's personality responses and mood states"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Response Categories
    category = db.Column(db.String(50), nullable=False)  # task_created, task_completed, task_overdue, etc.
    mood = db.Column(db.String(50), nullable=False)  # happy, sarcastic, angry, encouraging, etc.
    attitude_level = db.Column(db.Integer, nullable=False)  # 1-5 scale
    
    # Response Content
    text_response = db.Column(db.Text, nullable=False)
    animation_type = db.Column(db.String(50))  # bounce, shake, glow, etc.
    
    # Conditions
    min_personality_level = db.Column(db.Integer, default=1)
    max_personality_level = db.Column(db.Integer, default=10)
    
    # Metadata
    weight = db.Column(db.Integer, default=1)  # For random selection weighting
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CarrotPersonality {self.category}:{self.mood}>'

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'mood': self.mood,
            'attitude_level': self.attitude_level,
            'text_response': self.text_response,
            'animation_type': self.animation_type,
            'min_personality_level': self.min_personality_level,
            'max_personality_level': self.max_personality_level,
            'weight': self.weight
        }


class UserInteraction(db.Model):
    """Tracks user interactions for AI learning and mood adjustment"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Interaction Details
    interaction_type = db.Column(db.String(50), nullable=False)  # task_created, task_completed, etc.
    context_data = db.Column(db.JSON)  # Additional context about the interaction
    
    # AI Response
    carrot_response_id = db.Column(db.Integer, db.ForeignKey('carrot_personality.id'))
    user_reaction = db.Column(db.String(20))  # positive, negative, neutral
    
    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float)  # Time taken to respond in seconds

    def __repr__(self):
        return f'<UserInteraction {self.user_id}:{self.interaction_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'interaction_type': self.interaction_type,
            'context_data': self.context_data,
            'carrot_response_id': self.carrot_response_id,
            'user_reaction': self.user_reaction,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'response_time': self.response_time
        }


class ProductivityStreak(db.Model):
    """Tracks detailed streak information"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Streak Details
    streak_type = db.Column(db.String(50), nullable=False)  # daily, weekly, monthly
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)  # Null if streak is ongoing
    length = db.Column(db.Integer, default=1)
    
    # Streak Data
    tasks_completed = db.Column(db.Integer, default=0)
    total_xp_earned = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    broken_reason = db.Column(db.String(100))  # Why the streak was broken

    def __repr__(self):
        return f'<ProductivityStreak {self.user_id}:{self.streak_type}:{self.length}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'streak_type': self.streak_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'length': self.length,
            'tasks_completed': self.tasks_completed,
            'total_xp_earned': self.total_xp_earned,
            'is_active': self.is_active,
            'broken_reason': self.broken_reason
        }

