from flask import Blueprint, request, jsonify
from services.community_service import CommunityService
from middleware.auth_middleware import token_required

comment_bp = Blueprint('comments', __name__, url_prefix='/api/community/posts/<int:post_id>/comments')
community_service = CommunityService()

@comment_bp.route('', methods=['GET'])
def get_comments(post_id):
    comments = community_service.get_comments(post_id)
    return jsonify({'success': True, 'comments': comments}), 200

@comment_bp.route('', methods=['POST'])
@token_required
def add_comment(post_id):
    data = request.get_json() or {}
    content = data.get('content')
    parent_id = data.get('parent_id') # nullable, for nested replies
    user_id = request.current_user.id

    if not content:
        return jsonify({'message': 'Nội dung bình luận không được trống.'}), 400

    result = community_service.add_comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
        parent_id=parent_id
    )
    return jsonify(result), 201
