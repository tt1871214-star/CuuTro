from datetime import datetime
from database.db import db

class Disaster(db.Model):
    __tablename__ = 'disasters'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    alert_level = db.Column(db.String(20), nullable=False)  # YELLOW, ORANGE, RED
    latitude = db.Column(db.Double, nullable=False)
    longitude = db.Column(db.Double, nullable=False)
    radius_km = db.Column(db.Double, default=5.0)
    status = db.Column(db.String(20), default='ACTIVE')  # ACTIVE, RESOLVED
    occurred_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    alerts = db.relationship('Alert', backref='disaster', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'alert_level': self.alert_level,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius_km': self.radius_km,
            'status': self.status,
            'occurred_at': self.occurred_at.isoformat() if self.occurred_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disaster_id = db.Column(db.Integer, db.ForeignKey('disasters.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    target_area = db.Column(db.String(100), nullable=False)
    alert_level = db.Column(db.String(20), nullable=False)  # YELLOW, ORANGE, RED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'disaster_id': self.disaster_id,
            'title': self.title,
            'message': self.message,
            'target_area': self.target_area,
            'alert_level': self.alert_level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
