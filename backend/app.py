import os
from flask import Flask, jsonify
from flask_cors import CORS
from config.config import active_config
from database.db import db, init_db

# Import blueprints
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.disaster_routes import disaster_bp
from routes.rescue_routes import rescue_bp
from routes.community_routes import community_bp
from routes.comment_routes import comment_bp
from routes.verification_routes import verification_bp
from routes.safe_routes import safe_bp
from routes.emergency_routes import emergency_bp
from routes.notification_routes import notification_bp
from routes.dashboard_routes import dashboard_bp
from routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(active_config)
    
    # Configure CORS for frontend access
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize Database
    init_db(app)
    
    # Register all 12 Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(disaster_bp)
    app.register_blueprint(rescue_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(safe_bp)
    app.register_blueprint(emergency_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    
    # Root status endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'project': 'Relief Warning and Rescue Platform',
            'api_version': '1.0'
        }), 200

    # Auto Seed Database if empty
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        import models
        
        # Create all tables if they don't exist
        db.create_all()
        
        # Check if Role is seeded. If not, run automated seeding
        from models.role import Role
        if Role.query.count() == 0:
            print("Database is empty. Running self-seeding process...")
            try:
                # 1. Seed Roles
                r_admin = Role(id=1, name='Admin')
                r_resident = Role(id=2, name='Resident')
                r_team = Role(id=3, name='RescueTeam')
                db.session.add_all([r_admin, r_resident, r_team])
                db.session.commit()
                
                # 2. Seed Default Users
                from models.user import User
                # admin123
                admin = User(id=1, phone='0901234567', full_name='Quản Trị Viên', role_id=1)
                admin.set_password('admin123')
                # citizen123
                resident = User(id=2, phone='0987654321', full_name='Nguyễn Văn Dân', role_id=2)
                resident.set_password('citizen123')
                # rescue123
                rescuer = User(id=3, phone='0912345678', full_name='Đội Trưởng Cứu Hộ A', role_id=3)
                rescuer.set_password('rescue123')
                
                db.session.add_all([admin, resident, rescuer])
                db.session.commit()
                
                # 3. Seed Rescue Team Profile
                from models.rescue import RescueTeam
                team = RescueTeam(
                    id=1,
                    user_id=3,
                    team_name='Đội Cứu Hộ Phản Ứng Nhanh Số 1',
                    leader_name='Đội Trưởng Cứu Hộ A',
                    contact_phone='0912345678',
                    status='ACTIVE',
                    current_lat=21.0285,
                    current_lng=105.8542
                )
                db.session.add(team)
                db.session.commit()
                
                # 4. Seed Emergency Contacts
                from models.emergency import EmergencyContact
                c1 = EmergencyContact(id=1, name='113 Công an', phone='113', icon_type='shield', sort_order=1)
                c2 = EmergencyContact(id=2, name='114 Cứu hỏa & Cứu nạn', phone='114', icon_type='flame', sort_order=2)
                c3 = EmergencyContact(id=3, name='115 Cấp cứu y tế', phone='115', icon_type='heart-pulse', sort_order=3)
                c4 = EmergencyContact(id=4, name='Hỗ Trợ Thiên Tai Quốc Gia', phone='18001022', icon_type='phone-call', sort_order=4)
                db.session.add_all([c1, c2, c3, c4])
                db.session.commit()
                
                # 5. Seed Disaster Warning
                from models.disaster import Disaster, Alert
                d = Disaster(
                    id=1,
                    title='Mưa lũ ngập úng đô thị',
                    description='Ảnh hưởng áp thấp nhiệt đới gây mưa cực lớn. Nguy cơ ngập cao tại ngã tư Cầu Giấy và các điểm trũng thấp.',
                    alert_level='ORANGE',
                    latitude=21.0350,
                    longitude=105.8000,
                    radius_km=10.0,
                    status='ACTIVE'
                )
                db.session.add(d)
                db.session.commit()
                
                a = Alert(
                    id=1,
                    disaster_id=1,
                    title='Cảnh Báo Ngập Lụt Đô Thị',
                    message='Khu vực Cầu Giấy, Hoàn Kiếm đề phòng ngập úng sâu. Tránh đi qua các vùng ngập tràn.',
                    target_area='Quận Cầu Giấy, Quận Hoàn Kiếm, TP. Hà Nội',
                    alert_level='ORANGE'
                )
                db.session.add(a)
                db.session.commit()
                
                # 6. Seed Community Post
                from models.community import CommunityPost
                p = CommunityPost(
                    id=1,
                    user_id=2,
                    title='Ngập ngụa nước tại ngã tư Xuân Thủy',
                    content='Nước dâng cao nửa mét, xe máy chết máy hàng loạt. Có người dân đang hỗ trợ đẩy xe.',
                    post_type='FLOOD',
                    latitude=21.0360,
                    longitude=105.7820,
                    verification_status='UNVERIFIED',
                    upvotes=0,
                    downvotes=0
                )
                db.session.add(p)
                db.session.commit()
                
                print("Self-seeding completed successfully!")
            except Exception as e:
                db.session.rollback()
                print(f"Error seeding database: {e}")
                
    return app

if __name__ == '__main__':
    app = create_app()
    # Read port from env or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
