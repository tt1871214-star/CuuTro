from flask import Blueprint, request, jsonify
from database.db import db
from models.emergency import EmergencyContact
from models.disaster import Disaster, Alert
from models.user import User
from models.logs import AuditLog, AILog
from repositories.notification_repository import NotificationRepository
from middleware.auth_middleware import token_required, roles_accepted

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
notif_repo = NotificationRepository()

# 1. Emergency Contacts Management (CRUD)
@admin_bp.route('/emergency-contacts', methods=['POST'])
@token_required
@roles_accepted('Admin')
def create_emergency_contact():
    data = request.get_json() or {}
    name = data.get('name')
    phone = data.get('phone')
    icon_type = data.get('icon_type', 'phone')
    sort_order = data.get('sort_order', 0)

    if not name or not phone:
        return jsonify({'message': 'Tên và Số điện thoại là bắt buộc.'}), 400

    contact = EmergencyContact(
        name=name,
        phone=phone,
        icon_type=icon_type,
        sort_order=sort_order,
        is_active=True
    )
    db.session.add(contact)
    db.session.commit()
    return jsonify({'success': True, 'contact': contact.to_dict()}), 201

@admin_bp.route('/emergency-contacts/<int:contact_id>', methods=['PUT'])
@token_required
@roles_accepted('Admin')
def update_emergency_contact(contact_id):
    contact = EmergencyContact.query.get(contact_id)
    if not contact:
        return jsonify({'message': 'Không tìm thấy liên hệ khẩn cấp.'}), 404

    data = request.get_json() or {}
    contact.name = data.get('name', contact.name)
    contact.phone = data.get('phone', contact.phone)
    contact.icon_type = data.get('icon_type', contact.icon_type)
    contact.sort_order = data.get('sort_order', contact.sort_order)
    contact.is_active = data.get('is_active', contact.is_active)

    db.session.commit()
    return jsonify({'success': True, 'contact': contact.to_dict()}), 200

@admin_bp.route('/emergency-contacts/<int:contact_id>', methods=['DELETE'])
@token_required
@roles_accepted('Admin')
def delete_emergency_contact(contact_id):
    contact = EmergencyContact.query.get(contact_id)
    if not contact:
        return jsonify({'message': 'Không tìm thấy liên hệ khẩn cấp.'}), 404

    db.session.delete(contact)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Đã xóa liên hệ khẩn cấp.'}), 200


# 2. Disaster warnings creation
@admin_bp.route('/disasters', methods=['POST'])
@token_required
@roles_accepted('Admin')
def declare_disaster():
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    alert_level = data.get('alert_level') # YELLOW, ORANGE, RED
    lat = data.get('latitude')
    lng = data.get('longitude')
    radius = data.get('radius_km', 5.0)
    target_area = data.get('target_area', 'Toàn bộ khu vực lân cận')

    if not title or not description or not alert_level or lat is None or lng is None:
        return jsonify({'message': 'Vui lòng cung cấp đầy đủ thông tin thiên tai.'}), 400

    disaster = Disaster(
        title=title,
        description=description,
        alert_level=alert_level,
        latitude=float(lat),
        longitude=float(lng),
        radius_km=float(radius),
        status='ACTIVE'
    )
    db.session.add(disaster)
    db.session.commit()

    # Create associated Alert
    alert = Alert(
        disaster_id=disaster.id,
        title=f"CẢNH BÁO: {title}",
        message=description,
        target_area=target_area,
        alert_level=alert_level
    )
    db.session.add(alert)
    db.session.commit()

    # Broadcast notification to all active residents in database
    # In a production app, we would broadcast to users in target area. Here we broadcast to everyone.
    residents = User.query.filter_by(role_id=2).all() # Resident role
    for r in residents:
        notif_repo.create_notification(
            user_id=r.id,
            title=f"CẢNH BÁO THIÊN TAI KHẨN CẤP: {title}",
            content=description,
            type="DISASTER"
        )
    notif_repo.save()

    return jsonify({'success': True, 'disaster': disaster.to_dict(), 'alert': alert.to_dict()}), 201


# 3. System Logs auditing
@admin_bp.route('/audit-logs', methods=['GET'])
@token_required
@roles_accepted('Admin')
def get_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'logs': [l.to_dict() for l in logs]}), 200

@admin_bp.route('/ai-logs', methods=['GET'])
@token_required
@roles_accepted('Admin')
def get_ai_logs():
    logs = AILog.query.order_by(AILog.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'logs': [l.to_dict() for l in logs]}), 200
