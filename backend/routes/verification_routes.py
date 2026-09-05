from flask import Blueprint, request, jsonify
from services.community_service import CommunityService
from middleware.auth_middleware import token_required

verification_bp = Blueprint('verifications', __name__, url_prefix='/api/community/posts/<int:post_id>/verify')
community_service = CommunityService()

@verification_bp.route('', methods=['POST'])
@token_required
def verify_post(post_id):
    data = request.get_json() or {}
    is_verified = data.get('is_verified') # boolean: True = upvote, False = downvote
    lat = data.get('latitude')
    lng = data.get('longitude')
    user_id = request.current_user.id

    if is_verified is None or lat is None or lng is None:
        return jsonify({'message': 'Vui lòng cung cấp đầy đủ ý kiến xác nhận và tọa độ GPS hiện tại.'}), 400

    result = community_service.verify_post(
        post_id=post_id,
        user_id=user_id,
        is_verified=bool(is_verified),
        user_lat=float(lat),
        user_lng=float(lng)
    )
    
    if not result['success']:
        return jsonify({'message': result['message']}), 400

    return jsonify(result), 200
