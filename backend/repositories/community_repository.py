from repositories.base_repository import BaseRepository
from models.community import CommunityPost, Comment, CommunityVerification
from database.db import db

class CommunityRepository(BaseRepository):
    def __init__(self):
        super().__init__(CommunityPost)

    def get_all_posts(self):
        return CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()

    def get_comments_by_post_id(self, post_id):
        # Return only top-level comments (parent_id is null)
        # Nested replies can be loaded through parent comment relationship or recursively
        return Comment.query.filter_by(post_id=post_id, parent_id=None).order_by(Comment.created_at.asc()).all()

    def get_verification(self, post_id, user_id):
        return CommunityVerification.query.filter_by(post_id=post_id, user_id=user_id).first()

    def add_verification(self, post_id, user_id, is_verified):
        verify = CommunityVerification(
            post_id=post_id,
            user_id=user_id,
            is_verified=is_verified
        )
        db.session.add(verify)
        return verify

    def add_comment(self, post_id, user_id, parent_id, content):
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            parent_id=parent_id,
            content=content
        )
        db.session.add(comment)
        return comment
