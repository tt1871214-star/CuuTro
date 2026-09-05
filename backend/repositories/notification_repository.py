from repositories.base_repository import BaseRepository
from models.notification import Notification
from database.db import db

class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)

    def get_by_user_id(self, user_id):
        return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).all()

    def get_unread_by_user_id(self, user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at.desc()).all()

    def create_notification(self, user_id, title, content, type):
        notif = Notification(
            user_id=user_id,
            title=title,
            content=content,
            type=type,
            is_read=False
        )
        db.session.add(notif)
        return notif

    def mark_all_read(self, user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({Notification.is_read: True})
        db.session.commit()
