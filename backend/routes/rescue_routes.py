from flask import Blueprint, request, jsonify
from services.rescue_service import RescueService
from middleware.auth_middleware import token_required, roles_accepted

rescue_bp = Blueprint('rescue', __name__, url_prefix='/api/rescue')
rescue_service = RescueService()

@rescue_bp.route('/requests', methods=['POST'])
@token_required
def create_request():
    data = request.get_json() or {}
    lat = data.get('latitude')
    lng = data.get('longitude')
    user_id = request.current_user.id

    if lat is None or lng is None:
        return jsonify({'message': 'Vui lòng cung cấp tọa độ GPS đầy đủ.'}), 400

    result = rescue_service.create_request(user_id, float(lat), float(lng))
    if not result['success']:
        return jsonify({'message': result['message']}), 400

    return jsonify(result), 201

@rescue_bp.route('/requests/my-status', methods=['GET'])
@token_required
def get_my_status():
    user_id = request.current_user.id
    req_status = rescue_service.get_citizen_request_status(user_id)
    if not req_status:
        return jsonify({'success': True, 'request': None}), 200
    return jsonify({'success': True, 'request': req_status}), 200

@rescue_bp.route('/requests/active', methods=['GET'])
@token_required
@roles_accepted('RescueTeam', 'Admin')
def get_active_requests():
    active_reqs = rescue_service.get_active_requests()
    return jsonify({'success': True, 'requests': active_reqs}), 200

@rescue_bp.route('/requests/<int:request_id>', methods=['GET'])
@token_required
def get_request_details(request_id):
    req_details = rescue_service.get_request_details(request_id)
    if not req_details:
        return jsonify({'message': 'Không tìm thấy yêu cầu cứu hộ.'}), 404
    return jsonify({'success': True, 'request': req_details}), 200

@rescue_bp.route('/requests/<int:request_id>/assign', methods=['POST'])
@token_required
@roles_accepted('RescueTeam', 'Admin')
def assign_request(request_id):
    user_id = request.current_user.id
    
    # Identify rescue team for the user (if role is RescueTeam)
    if request.current_user.role.name == 'RescueTeam':
        team = request.current_user.rescue_team
        if not team:
            return jsonify({'message': 'Bạn chưa được liên kết với đội cứu hộ nào.'}), 400
        team_id = team.id
    else:
        # For Admin, they can pass team_id in request body
        data = request.get_json() or {}
        team_id = data.get('team_id')
        if not team_id:
            return jsonify({'message': 'Vui lòng chọn đội cứu hộ để điều phối.'}), 400

    result = rescue_service.assign_request(request_id, team_id, user_id)
    if not result['success']:
        return jsonify({'message': result['message']}), 400

    return jsonify(result), 200

@rescue_bp.route('/requests/<int:request_id>/status', methods=['PUT'])
@token_required
@roles_accepted('RescueTeam', 'Admin')
def update_status(request_id):
    data = request.get_json() or {}
    status = data.get('status')
    notes = data.get('notes', '')
    user_id = request.current_user.id

    if not status or status not in ['RECEIVED', 'MOVING', 'COMPLETED', 'CANCELLED']:
        return jsonify({'message': 'Trạng thái cập nhật không hợp lệ.'}), 400

    result = rescue_service.update_request_status(request_id, status, notes, user_id)
    if not result['success']:
        return jsonify({'message': result['message']}), 400

    return jsonify(result), 200

@rescue_bp.route('/requests/<int:request_id>/citizen-cancel', methods=['POST'])
@token_required
def citizen_cancel(request_id):
    user_id = request.current_user.id
    result = rescue_service.citizen_cancel_request(request_id, user_id)
    if not result['success']:
        return jsonify({'message': result['message']}), 400
    return jsonify(result), 200

@rescue_bp.route('/teams/location', methods=['PUT'])
@token_required
@roles_accepted('RescueTeam')
def update_location():
    team = request.current_user.rescue_team
    if not team:
        return jsonify({'message': 'Tài khoản chưa được liên kết với đội cứu hộ.'}), 400

    data = request.get_json() or {}
    lat = data.get('latitude')
    lng = data.get('longitude')

    if lat is None or lng is None:
        return jsonify({'message': 'Vui lòng cung cấp tọa độ GPS đầy đủ.'}), 400

    result = rescue_service.update_team_location(team.id, float(lat), float(lng))
    if not result['success']:
        return jsonify({'message': result['message']}), 400

    return jsonify(result), 200

@rescue_bp.route('/requests/<int:request_id>/history', methods=['GET'])
@token_required
def get_history(request_id):
    history = rescue_service.rescue_repo.get_history_by_request_id(request_id)
    return jsonify({'success': True, 'history': [h.to_dict() for h in history]}), 200
