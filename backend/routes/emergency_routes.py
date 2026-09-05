from flask import Blueprint, jsonify
from repositories.emergency_repository import EmergencyRepository

emergency_bp = Blueprint('emergency', __name__, url_prefix='/api/emergency')
emergency_repo = EmergencyRepository()

@emergency_bp.route('/contacts', methods=['GET'])
def get_emergency_contacts():
    contacts = emergency_repo.get_active_contacts()
    return jsonify({'success': True, 'contacts': [c.to_dict() for c in contacts]}), 200
