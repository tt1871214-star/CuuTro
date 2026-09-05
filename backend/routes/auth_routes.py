from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from middleware.auth_middleware import token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_service = AuthService()

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    phone = data.get('phone')
    password = data.get('password')
    full_name = data.get('full_name')
    role_name = data.get('role_name', 'Resident')
    team_details = data.get('team_details') # optional dict containing team name, etc.

    if not phone or not password or not full_name:
        return jsonify({'message': 'Vui lòng cung cấp đầy đủ số điện thoại, mật khẩu và họ tên.'}), 400

    result = auth_service.register(phone, password, full_name, role_name, team_details)
    if not result['success']:
        return jsonify({'message': result['message']}), 400

    return jsonify(result), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    phone = data.get('phone')
    password = data.get('password')

    if not phone or not password:
        return jsonify({'message': 'Vui lòng nhập đầy đủ số điện thoại và mật khẩu.'}), 400

    result = auth_service.login(phone, password)
    if not result['success']:
        return jsonify({'message': result['message']}), 401

    return jsonify(result), 200

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    data = request.get_json() or {}
    refresh_token = data.get('refresh_token')

    if not refresh_token:
        return jsonify({'message': 'Vui lòng cung cấp refresh token.'}), 400

    result = auth_service.refresh(refresh_token)
    if not result['success']:
        return jsonify({'message': result['message']}), 401

    return jsonify(result), 200

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    data = request.get_json() or {}
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    user_id = request.current_user.id

    if not old_password or not new_password:
        return jsonify({'message': 'Vui lòng nhập đầy đủ mật khẩu cũ và mật khẩu mới.'}), 400

    result = auth_service.change_password(user_id, old_password, new_password)
    if not result['success']:
        return jsonify({'message': result['message']}), 400

    return jsonify({'message': result['message']}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    phone = data.get('phone')

    if not phone:
        return jsonify({'message': 'Vui lòng cung cấp số điện thoại.'}), 400

    result = auth_service.forgot_password_mock(phone)
    if not result['success']:
        return jsonify({'message': result['message']}), 400

    return jsonify(result), 200
