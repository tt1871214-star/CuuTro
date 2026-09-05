from flask import Blueprint, request, jsonify
from services.community_service import CommunityService
from middleware.auth_middleware import token_required

community_bp = Blueprint('community', __name__, url_prefix='/api/community/posts')
community_service = CommunityService()

@community_bp.route('', methods=['POST'])
@token_required
def create_post():
    data = request.get_json() or {}
    title = data.get('title')
    content = data.get('content')
    post_type = data.get('post_type') # FLOOD, LANDSLIDE, ROAD_DAMAGE, BRIDGE_DAMAGE, RELIEF_POINT, DANGER_ZONE
    lat = data.get('latitude')
    lng = data.get('longitude')
    image_url = data.get('image_url')
    user_id = request.current_user.id

    if not title or not content or not post_type or lat is None or lng is None:
        return jsonify({'message': 'Vui lòng điền đầy đủ tiêu đề, nội dung, loại báo cáo và vị trí.'}), 400

    result = community_service.create_post(
        user_id=user_id,
        title=title,
        content=content,
        post_type=post_type,
        latitude=float(lat),
        longitude=float(lng),
        image_url=image_url
    )
    return jsonify(result), 201

@community_bp.route('', methods=['GET'])
def get_posts():
    posts = community_service.get_all_posts()
    return jsonify({'success': True, 'posts': posts}), 200

@community_bp.route('/<int:post_id>', methods=['GET'])
def get_post_details(post_id):
    post = community_service.get_post_details(post_id)
    if not post:
        return jsonify({'message': 'Không tìm thấy bài đăng.'}), 404
    return jsonify({'success': True, 'post': post}), 200
