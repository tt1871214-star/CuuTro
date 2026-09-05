from datetime import datetime
from database.db import db
from models.safe import SafeStatus, Follower
from models.user import User
from repositories.user_repository import UserRepository
from repositories.notification_repository import NotificationRepository

class SafeService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.notif_repo = NotificationRepository()

    def mark_safe(self, user_id, latitude, longitude):
        """Mark user as safe and notify all their followers."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {'success': False, 'message': 'Người dùng không tồn tại.'}

        status = SafeStatus(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            logged_at=datetime.utcnow()
        )
        db.session.add(status)
        db.session.commit()

        # Get all followers whose status is ACCEPTED
        accepted_followers = Follower.query.filter_by(user_id=user_id, status='ACCEPTED').all()
        
        # Broadcast safe notification to all of them
        for f in accepted_followers:
            self.notif_repo.create_notification(
                user_id=f.follower_id,
                title="Người thân báo an toàn",
                content=f"Người thân {user.full_name} của bạn đã báo cáo AN TOÀN vào lúc {status.logged_at.strftime('%H:%M:%S %d/%m/%Y')}.",
                type="SAFE"
            )
        self.notif_repo.save()

        return {'success': True, 'safe_status': status.to_dict()}

    def add_follower_by_phone(self, follower_id, target_phone):
        """
        Request to follow another user (relative) by phone number.
        follower_id is the user wanting to follow.
        target_phone is the phone of the relative they want to follow.
        """
        relative = self.user_repo.get_by_phone(target_phone)
        if not relative:
            return {'success': False, 'message': 'Không tìm thấy người dùng với số điện thoại này.'}
        
        if relative.id == follower_id:
            return {'success': False, 'message': 'Bạn không thể theo dõi chính mình.'}

        # Check if already following
        existing = Follower.query.filter_by(user_id=relative.id, follower_id=follower_id).first()
        if existing:
            return {'success': False, 'message': 'Bạn đã gửi yêu cầu theo dõi người này rồi.'}

        # For quick emergency coordination, we auto-accept or set to ACCEPTED, 
        # but let's default to PENDING so users can approve. To make testing easy, we can also support auto-accept.
        # Let's set to ACCEPTED for instant connection in emergency, but can be updated.
        # Let's write PENDING, but create a method to approve it.
        follower_rel = Follower(
            user_id=relative.id,      # the relative
            follower_id=follower_id,  # the current user
            status='ACCEPTED'         # Instant connection for easier emergency coordination
        )
        db.session.add(follower_rel)
        db.session.commit()

        # Notify the relative that someone is now following their safety updates
        follower_user = self.user_repo.get_by_id(follower_id)
        self.notif_repo.create_notification(
            user_id=relative.id,
            title="Thành viên mới theo dõi bạn",
            content=f"{follower_user.full_name} ({follower_user.phone}) đã kết nối để theo dõi trạng thái an toàn của bạn.",
            type="SAFE"
        )
        self.notif_repo.save()

        return {'success': True, 'follower': follower_rel.to_dict()}

    def remove_follower(self, follower_id, target_user_id):
        """Remove following relationship."""
        rel = Follower.query.filter_by(user_id=target_user_id, follower_id=follower_id).first()
        if not rel:
            return {'success': False, 'message': 'Mối quan hệ kết nối không tồn tại.'}
        
        db.session.delete(rel)
        db.session.commit()
        return {'success': True, 'message': 'Đã hủy kết nối thành công.'}

    def get_family_statuses(self, user_id):
        """Get safety statuses of all people the user is following."""
        # Find who the user is following (user is follower_id)
        following_relations = Follower.query.filter_by(follower_id=user_id, status='ACCEPTED').all()
        
        results = []
        for rel in following_relations:
            followed_user = rel.followed_user
            if followed_user:
                # Get their latest safety status
                latest_status = SafeStatus.query.filter_by(user_id=followed_user.id).order_by(SafeStatus.logged_at.desc()).first()
                results.append({
                    'user_id': followed_user.id,
                    'full_name': followed_user.full_name,
                    'phone': followed_user.phone,
                    'is_safe': latest_status is not None,
                    'last_seen_lat': latest_status.latitude if latest_status else None,
                    'last_seen_lng': latest_status.longitude if latest_status else None,
                    'last_seen_time': latest_status.logged_at.isoformat() if latest_status else None
                })
        return results

    def get_my_followers(self, user_id):
        """Get people who are following the user (user is user_id)."""
        relations = Follower.query.filter_by(user_id=user_id).all()
        return [r.to_dict() for r in relations]
