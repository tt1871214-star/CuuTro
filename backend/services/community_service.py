from repositories.community_repository import CommunityRepository
from repositories.notification_repository import NotificationRepository
from models.community import CommunityPost, Comment, CommunityVerification
from utils.gps import haversine_distance
from database.db import db

class CommunityService:
    def __init__(self):
        self.post_repo = CommunityRepository()
        self.notif_repo = NotificationRepository()

    def create_post(self, user_id, title, content, post_type, latitude, longitude, image_url=None):
        post = CommunityPost(
            user_id=user_id,
            title=title,
            content=content,
            post_type=post_type,
            latitude=latitude,
            longitude=longitude,
            image_url=image_url,
            verification_status='UNVERIFIED',
            upvotes=0,
            downvotes=0
        )
        self.post_repo.add(post)
        self.post_repo.save()
        return {'success': True, 'post': post.to_dict()}

    def get_all_posts(self):
        posts = self.post_repo.get_all_posts()
        return [post.to_dict() for post in posts]

    def get_post_details(self, post_id):
        post = self.post_repo.get_by_id(post_id)
        if not post:
            return None
        return post.to_dict()

    def get_comments(self, post_id):
        comments = self.post_repo.get_comments_by_post_id(post_id)
        # Serialize nested structure
        return [self._serialize_comment(c) for c in comments]

    def _serialize_comment(self, comment):
        res = comment.to_dict()
        res['replies'] = [self._serialize_comment(reply) for reply in comment.replies]
        return res

    def add_comment(self, post_id, user_id, content, parent_id=None):
        comment = self.post_repo.add_comment(
            post_id=post_id,
            user_id=user_id,
            parent_id=parent_id,
            content=content
        )
        self.post_repo.save()
        return {'success': True, 'comment': comment.to_dict()}

    def verify_post(self, post_id, user_id, is_verified, user_lat, user_lng):
        """
        Verify post (Upvote/Downvote).
        Enforce distance check: verifier must be within 5km of the post coordinates.
        """
        post = self.post_repo.get_by_id(post_id)
        if not post:
            return {'success': False, 'message': 'Không tìm thấy bài viết.'}

        # Calculate distance
        dist = haversine_distance(user_lat, user_lng, post.latitude, post.longitude)
        if dist > 5.0:
            return {
                'success': False, 
                'message': f'Bạn ở cách địa điểm này {dist:.2f} km. Bạn cần ở trong bán kính 5km để xác thực thông tin này.'
            }

        # Check if already voted
        existing_vote = self.post_repo.get_verification(post_id, user_id)
        
        if existing_vote:
            # If voting same, do nothing
            if existing_vote.is_verified == is_verified:
                return {'success': False, 'message': 'Bạn đã xác thực bài đăng này rồi.'}
            
            # If changing vote, adjust counters
            existing_vote.is_verified = is_verified
            if is_verified:
                post.upvotes += 1
                post.downvotes = max(0, post.downvotes - 1)
            else:
                post.downvotes += 1
                post.upvotes = max(0, post.upvotes - 1)
        else:
            # New vote
            self.post_repo.add_verification(post_id, user_id, is_verified)
            if is_verified:
                post.upvotes += 1
            else:
                post.downvotes += 1

        db.session.commit()

        # Run Verification Status Transition Logic
        # Threshold: 3 confirmations -> VERIFIED; 3 denials -> REJECTED
        status_changed = False
        new_status = post.verification_status
        
        if post.upvotes >= 3 and post.upvotes > post.downvotes:
            if post.verification_status != 'VERIFIED':
                post.verification_status = 'VERIFIED'
                new_status = 'VERIFIED'
                status_changed = True
                # Notify author and community
                self.notif_repo.create_notification(
                    user_id=post.user_id,
                    title="Bài đăng của bạn đã được xác thực",
                    content=f"Tin cảnh báo '{post.title}' của bạn đã nhận đủ lượt xác thực từ người dân lân cận.",
                    type="VERIFIED"
                )
                self.notif_repo.save()
        elif post.downvotes >= 3 and post.downvotes >= post.upvotes:
            if post.verification_status != 'REJECTED':
                post.verification_status = 'REJECTED'
                new_status = 'REJECTED'
                status_changed = True
                self.notif_repo.create_notification(
                    user_id=post.user_id,
                    title="Bài đăng bị báo cáo sai lệch",
                    content=f"Tin cảnh báo '{post.title}' của bạn bị cộng đồng báo cáo là không chính xác hoặc đã được xử lý.",
                    type="VERIFIED"
                )
                self.notif_repo.save()

        db.session.commit()

        return {
            'success': True, 
            'upvotes': post.upvotes, 
            'downvotes': post.downvotes,
            'status': new_status,
            'status_changed': status_changed
        }
