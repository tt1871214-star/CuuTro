from flask import Blueprint, request, jsonify
from services.safe_service import SafeService
from middleware.auth_middleware import token_required

safe_bp = Blueprint('safe', __name__, url_prefix='/api/safe')
safe_service = SafeService()

@safe_bp.route('/mark', methods=['POST'])
@token_required
def mark_safe():
    data = request.get_json() or {}
    lat = data.get('latitude')
    lng = data.get('longitude')
    user_id = request.current_user.id

    if lat is None or lng is None:
        return jsonify({'message': 'Vui lòng cung cấp tọa độ GPS hiện tại.'}), 400

    result = safe_service.mark_safe(user_id, float(lat), float(lng))
    return jsonify(result), 200

@safe_bp.route('/family', methods=['GET'])
@token_required
def get_family():
    user_id = request.current_user.id
    family_statuses = safe_service.get_family_statuses(user_id)
    return jsonify({'success': True, 'family': family_statuses}), 200

@safe_bp.route('/family/follow', methods=['POST'])
@token_required
def follow_relative():
    data = request.get_json() or {}
    phone = data.get('phone')
    user_id = request.current_user.id

    if not phone:
        return jsonify({'message': 'Vui lòng cung cấp số điện thoại người thân cần theo dõi.'}), 400

    result = safe_service.add_follower_by_phone(user_id, phone)
    if not result['success']:
        return jsonify({'message': result['message']}), 400

    return jsonify(result), 200

@safe_bp.route('/family/follow/<int:target_user_id>', methods=['DELETE'])
@token_required
def unfollow_relative(target_user_id):
    user_id = request.current_user.id
    result = safe_service.remove_follower(user_id, target_user_id)
    if not result['success']:
        return jsonify({'message': result['message']}), 400
    return jsonify(result), 200

@safe_bp.route('/followers', methods=['GET'])
@token_required
def get_my_followers():
    user_id = request.current_user.id
    followers = safe_service.get_my_followers(user_id)
    return jsonify({'success': True, 'followers': followers}), 200
