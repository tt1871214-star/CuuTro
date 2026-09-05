from flask import Blueprint, jsonify, request
from repositories.notification_repository import NotificationRepository
from middleware.auth_middleware import token_required

notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')
notif_repo = NotificationRepository()

@notification_bp.route('', methods=['GET'])
@token_required
def get_my_notifications():
    user_id = request.current_user.id
    unread_only = request.args.get('unread_only', default='false').lower() == 'true'
    
    if unread_only:
        notifs = notif_repo.get_unread_by_user_id(user_id)
    else:
        notifs = notif_repo.get_by_user_id(user_id)
        
    return jsonify({'success': True, 'notifications': [n.to_dict() for n in notifs]}), 200

@notification_bp.route('/read-all', methods=['POST'])
@token_required
def mark_all_read():
    user_id = request.current_user.id
    notif_repo.mark_all_read(user_id)
    return jsonify({'success': True, 'message': 'Đã đánh dấu tất cả thông báo là đã đọc.'}), 200
