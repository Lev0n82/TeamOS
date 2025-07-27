from datetime import datetime
from src.models.user import db

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Team Settings
    is_public = db.Column(db.Boolean, default=False)
    invite_code = db.Column(db.String(20), unique=True)
    max_members = db.Column(db.Integer, default=50)
    
    # Team Customization
    avatar_url = db.Column(db.String(255))
    color_theme = db.Column(db.String(7), default='#3B82F6')
    
    # Relationships
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref='owned_teams')
    
    members = db.relationship('TeamMember', backref='team', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='team', lazy=True)

    def generate_invite_code(self):
        """Generate a unique invite code for the team"""
        import secrets
        import string
        
        while True:
            code = ''.join(secrets.choices(string.ascii_uppercase + string.digits, k=8))
            if not Team.query.filter_by(invite_code=code).first():
                self.invite_code = code
                break

    def get_member_count(self):
        """Get the current number of team members"""
        return len(self.members)

    def can_add_member(self):
        """Check if team can accept new members"""
        return self.get_member_count() < self.max_members

    def add_member(self, user_id, role='member'):
        """Add a new member to the team"""
        if not self.can_add_member():
            return None
            
        existing_member = TeamMember.query.filter_by(
            team_id=self.id, user_id=user_id
        ).first()
        
        if not existing_member:
            member = TeamMember(
                team_id=self.id,
                user_id=user_id,
                role=role
            )
            db.session.add(member)
            return member
        return existing_member

    def get_team_stats(self):
        """Get comprehensive team statistics"""
        total_projects = len(self.projects)
        active_projects = len([p for p in self.projects if p.status == 'active'])
        
        # Calculate total tasks across all team projects
        total_tasks = sum(len(project.tasks) for project in self.projects)
        completed_tasks = sum(
            len([task for task in project.tasks if task.status == 'completed'])
            for project in self.projects
        )
        
        return {
            'member_count': self.get_member_count(),
            'total_projects': total_projects,
            'active_projects': active_projects,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }

    def __repr__(self):
        return f'<Team {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_public': self.is_public,
            'invite_code': self.invite_code,
            'max_members': self.max_members,
            'avatar_url': self.avatar_url,
            'color_theme': self.color_theme,
            'owner_id': self.owner_id,
            'member_count': self.get_member_count(),
            'stats': self.get_team_stats()
        }


class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Member Details
    role = db.Column(db.String(20), default='member')  # owner, admin, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Permissions
    can_create_projects = db.Column(db.Boolean, default=True)
    can_invite_members = db.Column(db.Boolean, default=False)
    can_manage_team = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    notification_preferences = db.Column(db.JSON, default={})

    def update_activity(self):
        """Update the last active timestamp"""
        self.last_active = datetime.utcnow()

    def has_permission(self, permission):
        """Check if member has a specific permission"""
        permission_map = {
            'create_projects': self.can_create_projects,
            'invite_members': self.can_invite_members,
            'manage_team': self.can_manage_team
        }
        return permission_map.get(permission, False) or self.role in ['owner', 'admin']

    def __repr__(self):
        return f'<TeamMember {self.user_id} in team {self.team_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'user_id': self.user_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None,
            'can_create_projects': self.can_create_projects,
            'can_invite_members': self.can_invite_members,
            'can_manage_team': self.can_manage_team,
            'is_active': self.is_active,
            'notification_preferences': self.notification_preferences
        }


class TeamInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitee_email = db.Column(db.String(120), nullable=False)
    
    # Invitation Details
    token = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), default='member')
    message = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    responded_at = db.Column(db.DateTime)

    def generate_token(self):
        """Generate a unique invitation token"""
        import secrets
        self.token = secrets.token_urlsafe(32)

    def is_expired(self):
        """Check if invitation has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def accept(self, user_id):
        """Accept the invitation and add user to team"""
        if self.status == 'pending' and not self.is_expired():
            team = Team.query.get(self.team_id)
            if team and team.can_add_member():
                member = team.add_member(user_id, self.role)
                if member:
                    self.status = 'accepted'
                    self.responded_at = datetime.utcnow()
                    return member
        return None

    def decline(self):
        """Decline the invitation"""
        if self.status == 'pending':
            self.status = 'declined'
            self.responded_at = datetime.utcnow()
            return True
        return False

    def __repr__(self):
        return f'<TeamInvitation {self.invitee_email} to team {self.team_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'inviter_id': self.inviter_id,
            'invitee_email': self.invitee_email,
            'token': self.token,
            'role': self.role,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'is_expired': self.is_expired()
        }

