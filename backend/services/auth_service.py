import jwt
from datetime import datetime, timedelta
from flask import current_app
from repositories.user_repository import UserRepository
from models.user import User
from models.rescue import RescueTeam
from database.db import db

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def generate_tokens(self, user):
        """Generate JWT Access and Refresh Tokens."""
        # Use secret keys from configuration
        secret = current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-key-relief-platform')
        access_expiry = datetime.utcnow() + current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=2))
        refresh_expiry = datetime.utcnow() + current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=7))

        access_payload = {
            'identity': user.id,
            'role_id': user.role_id,
            'role_name': user.role.name if user.role else None,
            'phone': user.phone,
            'exp': access_expiry,
            'type': 'access'
        }

        refresh_payload = {
            'identity': user.id,
            'exp': refresh_expiry,
            'type': 'refresh'
        }

        access_token = jwt.encode(access_payload, secret, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, secret, algorithm='HS256')

        # Decode to string if it is bytes (depending on PyJWT version)
        if isinstance(access_token, bytes):
            access_token = access_token.decode('utf-8')
        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode('utf-8')

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES').total_seconds())
        }

    def register(self, phone, password, full_name, role_name='Resident', team_details=None):
        """Register a new user."""
        existing_user = self.user_repo.get_by_phone(phone)
        if existing_user:
            return {'success': False, 'message': 'Số điện thoại này đã được đăng ký.'}

        role = self.user_repo.get_role_by_name(role_name)
        if not role:
            return {'success': False, 'message': f'Vai trò {role_name} không hợp lệ.'}

        user = User(
            phone=phone,
            full_name=full_name,
            role_id=role.id,
            is_active=True
        )
        user.set_password(password)
        self.user_repo.add(user)
        self.user_repo.save()

        # If role is RescueTeam, register the team profile
        if role_name == 'RescueTeam' and team_details:
            team = RescueTeam(
                user_id=user.id,
                team_name=team_details.get('team_name', f'Đội cứu hộ {full_name}'),
                leader_name=full_name,
                contact_phone=phone,
                status='ACTIVE',
                current_lat=team_details.get('latitude', 0.0),
                current_lng=team_details.get('longitude', 0.0)
            )
            db.session.add(team)
            db.session.commit()

        return {'success': True, 'user': user.to_dict()}

    def login(self, phone, password):
        """Login user and return tokens."""
        user = self.user_repo.get_by_phone(phone)
        if not user or not user.check_password(password):
            return {'success': False, 'message': 'Số điện thoại hoặc mật khẩu không chính xác.'}

        if not user.is_active:
            return {'success': False, 'message': 'Tài khoản của bạn đã bị khóa.'}

        tokens = self.generate_tokens(user)
        user_info = user.to_dict()
        
        # Add rescue team id if the user belongs to a rescue team
        if user.role.name == 'RescueTeam':
            team = self.user_repo.get_rescue_team_by_user_id(user.id)
            if team:
                user_info['rescue_team_id'] = team.id

        return {
            'success': True,
            'tokens': tokens,
            'user': user_info
        }

    def refresh(self, refresh_token):
        """Refresh access token using a valid refresh token."""
        secret = current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-key-relief-platform')
        try:
            payload = jwt.decode(refresh_token, secret, algorithms=['HS256'])
            if payload.get('type') != 'refresh':
                return {'success': False, 'message': 'Token không hợp lệ.'}

            user_id = payload.get('identity')
            user = self.user_repo.get_by_id(user_id)
            if not user or not user.is_active:
                return {'success': False, 'message': 'Người dùng không tồn tại hoặc đã bị khóa.'}

            tokens = self.generate_tokens(user)
            return {'success': True, 'tokens': tokens}
        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Refresh token đã hết hạn.'}
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'Token không hợp lệ.'}

    def change_password(self, user_id, old_password, new_password):
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.check_password(old_password):
            return {'success': False, 'message': 'Mật khẩu cũ không đúng.'}

        user.set_password(new_password)
        self.user_repo.save()
        return {'success': True, 'message': 'Thay đổi mật khẩu thành công.'}
        
    def forgot_password_mock(self, phone):
        """Simulate sending a reset code (mock implementation)."""
        user = self.user_repo.get_by_phone(phone)
        if not user:
            return {'success': False, 'message': 'Số điện thoại không tồn tại trong hệ thống.'}
        # In a real app, send OTP. Here we return a mock success message.
        return {'success': True, 'message': 'Mã khôi phục đã được gửi (Mock). Mật khẩu mặc định tạm thời sẽ là "relief123".'}
