from flask import Blueprint, jsonify, request
from middleware.auth_middleware import token_required
from database.db import db
from services.ai_service import AIService

user_bp = Blueprint('user', __name__, url_prefix='/api/users')
ai_service = AIService()

@user_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    user = request.current_user
    user_data = user.to_dict()
    
    # Include rescue team information if applicable
    if user.role.name == 'RescueTeam' and user.rescue_team:
        user_data['rescue_team'] = user.rescue_team.to_dict()
        
    return jsonify({'success': True, 'user': user_data}), 200

@user_bp.route('/me', methods=['PUT'])
@token_required
def update_profile():
    user = request.current_user
    data = request.get_json() or {}
    
    full_name = data.get('full_name')
    if full_name:
        user.full_name = full_name
        
    db.session.commit()
    return jsonify({'success': True, 'user': user.to_dict()}), 200

@user_bp.route('/ai-chat', methods=['POST'])
@token_required
def ai_chat():
    data = request.get_json() or {}
    query = data.get('query')
    if not query:
        return jsonify({'message': 'Nội dung câu hỏi không được trống.'}), 400
        
    result = ai_service.query(request.current_user.id, query)
    return jsonify({'success': True, 'data': result}), 200

