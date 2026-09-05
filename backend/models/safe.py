from datetime import datetime
from database.db import db

class SafeStatus(db.Model):
    __tablename__ = 'safe_status'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    latitude = db.Column(db.Double, nullable=False)
    longitude = db.Column(db.Double, nullable=False)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.user.full_name if self.user else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'logged_at': self.logged_at.isoformat() if self.logged_at else None
        }

class Follower(db.Model):
    __tablename__ = 'followers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # Followed relative
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # User who is following
    status = db.Column(db.String(20), default='PENDING')  # PENDING, ACCEPTED
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent duplicate following relations
    __table_args__ = (
        db.UniqueConstraint('user_id', 'follower_id', name='unique_user_follower'),
    )

    # Relationships
    followed_user = db.relationship('User', foreign_keys=[user_id], backref='followed_by')
    follower_user = db.relationship('User', foreign_keys=[follower_id], backref='following_to')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'followed_name': self.followed_user.full_name if self.followed_user else None,
            'followed_phone': self.followed_user.phone if self.followed_user else None,
            'follower_id': self.follower_id,
            'follower_name': self.follower_user.full_name if self.follower_user else None,
            'follower_phone': self.follower_user.phone if self.follower_user else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
