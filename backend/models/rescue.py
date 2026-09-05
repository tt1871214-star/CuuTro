from datetime import datetime
from database.db import db

class RescueTeam(db.Model):
    __tablename__ = 'rescue_teams'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    team_name = db.Column(db.String(100), nullable=False)
    leader_name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, BUSY, INACTIVE
    current_lat = db.Column(db.Double, nullable=False, default=0.0)
    current_lng = db.Column(db.Double, nullable=False, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assigned_requests = db.relationship('RescueRequest', backref='assigned_team', lazy=True)
    histories = db.relationship('RescueHistory', backref='rescue_team', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'team_name': self.team_name,
            'leader_name': self.leader_name,
            'contact_phone': self.contact_phone,
            'status': self.status,
            'current_lat': self.current_lat,
            'current_lng': self.current_lng,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RescueRequest(db.Model):
    __tablename__ = 'rescue_requests'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    latitude = db.Column(db.Double, nullable=False)
    longitude = db.Column(db.Double, nullable=False)
    status = db.Column(db.String(20), default='WAITING')  # WAITING, RECEIVED, MOVING, COMPLETED, CANCELLED
    priority = db.Column(db.String(20), default='YELLOW')  # YELLOW, ORANGE, RED
    assigned_team_id = db.Column(db.Integer, db.ForeignKey('rescue_teams.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    histories = db.relationship('RescueHistory', backref='rescue_request', lazy=True, cascade="all, delete-orphan")

    def get_wait_time_minutes(self):
        """Calculate wait time in minutes since request creation."""
        delta = datetime.utcnow() - self.created_at
        return int(delta.total_seconds() / 60)

    def calculate_priority(self):
        """
        Recalculates the priority based on elapsed waiting time:
        - YELLOW = 0-20 mins
        - ORANGE = 20-30 mins
        - RED = > 30 mins
        """
        if self.status != 'WAITING':
            # Priority might lock once assigned, or keep recalculating. We keep it or update.
            return self.priority
            
        wait_mins = self.get_wait_time_minutes()
        if wait_mins > 30:
            return 'RED'
        elif wait_mins > 20:
            return 'ORANGE'
        else:
            return 'YELLOW'

    def to_dict(self):
        wait_mins = self.get_wait_time_minutes()
        # Ensure priority is dynamically checked
        dyn_priority = self.calculate_priority()
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'citizen_name': self.user.full_name if self.user else None,
            'citizen_phone': self.user.phone if self.user else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'priority': dyn_priority,
            'assigned_team_id': self.assigned_team_id,
            'assigned_team_name': self.assigned_team.team_name if self.assigned_team else None,
            'wait_time_minutes': wait_mins,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class RescueHistory(db.Model):
    __tablename__ = 'rescue_histories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey('rescue_requests.id', ondelete='CASCADE'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('rescue_teams.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # Status updates, notes added
    notes = db.Column(db.Text, nullable=True)
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'team_id': self.team_id,
            'action': self.action,
            'notes': self.notes,
            'performed_by': self.performed_by,
            'performer_name': db.session.query(User.full_name).filter_by(id=self.performed_by).scalar() if hasattr(self, 'performed_by') else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
