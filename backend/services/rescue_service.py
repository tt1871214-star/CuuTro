from datetime import datetime
from repositories.rescue_repository import RescueRepository
from repositories.user_repository import UserRepository
from repositories.notification_repository import NotificationRepository
from models.rescue import RescueRequest, RescueTeam, RescueHistory
from database.db import db

class RescueService:
    def __init__(self):
        self.rescue_repo = RescueRepository()
        self.user_repo = UserRepository()
        self.notif_repo = NotificationRepository()

    def create_request(self, user_id, latitude, longitude):
        """Create a new rescue request from a resident."""
        # Check if there is already an active request for this user to prevent spam
        active_requests = RescueRequest.query.filter_by(user_id=user_id).filter(
            RescueRequest.status.in_(['WAITING', 'RECEIVED', 'MOVING'])
        ).first()
        
        if active_requests:
            return {'success': False, 'message': 'Bạn đã gửi một yêu cầu cứu hộ đang được xử lý.'}

        request = RescueRequest(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            status='WAITING',
            priority='YELLOW'
        )
        self.rescue_repo.add(request)
        self.rescue_repo.save()

        # Log history
        self.rescue_repo.add_history_log(
            request_id=request.id,
            team_id=0, # 0 indicates no team assigned yet
            action='CREATED',
            notes='Yêu cầu cứu hộ được gửi từ người dân.',
            performed_by=user_id
        )
        self.rescue_repo.save()

        # Send alert notification to all admins and active rescue teams (mock)
        # We can implement a notification broadcast here if needed.
        
        return {'success': True, 'request': request.to_dict()}

    def get_active_requests(self):
        """Retrieve all active requests and dynamically compute their priority and wait times."""
        requests = self.rescue_repo.get_all_active_requests()
        result = []
        for req in requests:
            # Dynamically recalculate priority based on wait time
            req.priority = req.calculate_priority()
            result.append(req.to_dict())
        return result

    def get_request_details(self, request_id):
        req = self.rescue_repo.get_by_id(request_id)
        if not req:
            return None
        req.priority = req.calculate_priority()
        return req.to_dict()

    def get_citizen_request_status(self, user_id):
        """Get the latest active or past request for a citizen."""
        requests = self.rescue_repo.get_requests_by_user_id(user_id)
        if not requests:
            return None
        req = requests[0]
        req.priority = req.calculate_priority()
        return req.to_dict()

    def update_team_location(self, team_id, latitude, longitude):
        team = self.user_repo.get_rescue_team_by_id(team_id)
        if not team:
            return {'success': False, 'message': 'Không tìm thấy thông tin đội cứu hộ.'}
        
        team.current_lat = latitude
        team.current_lng = longitude
        db.session.commit()
        return {'success': True, 'team': team.to_dict()}

    def assign_request(self, request_id, team_id, user_id):
        """Assign request to a rescue team (called by admin or grabbed by team)."""
        request = self.rescue_repo.get_by_id(request_id)
        if not request:
            return {'success': False, 'message': 'Không tìm thấy yêu cầu cứu hộ.'}
        
        if request.status not in ['WAITING']:
            return {'success': False, 'message': 'Yêu cầu cứu hộ này đã được tiếp nhận bởi đội khác.'}

        team = self.user_repo.get_rescue_team_by_id(team_id)
        if not team:
            return {'success': False, 'message': 'Đội cứu hộ không tồn tại.'}

        request.assigned_team_id = team.id
        request.status = 'RECEIVED'
        team.status = 'BUSY'
        
        # Log History
        self.rescue_repo.add_history_log(
            request_id=request.id,
            team_id=team.id,
            action='ASSIGNED',
            notes=f'Đội cứu hộ {team.team_name} đã tiếp nhận nhiệm vụ.',
            performed_by=user_id
        )
        self.rescue_repo.save()

        # Send Automatic SMS / Reassurance Notification
        sms_content = (
            f"Hệ thống Relief: Đội cứu hộ mã số {team.id} ({team.team_name}) "
            f"đã tiếp nhận yêu cầu của bạn. Liên hệ Đội trưởng: {team.leader_name} ({team.contact_phone}). "
            f"Thời gian dự kiến đến: 15-20 phút. Xin hãy giữ bình tĩnh và giữ liên lạc!"
        )
        self.notif_repo.create_notification(
            user_id=request.user_id,
            title="Đội cứu hộ đã tiếp nhận yêu cầu",
            content=sms_content,
            type="RESCUE"
        )
        self.notif_repo.save()

        return {'success': True, 'request': request.to_dict()}

    def update_request_status(self, request_id, status, notes, performed_by_user_id):
        """Update request status (MOVING, COMPLETED, CANCELLED)."""
        request = self.rescue_repo.get_by_id(request_id)
        if not request:
            return {'success': False, 'message': 'Không tìm thấy yêu cầu cứu hộ.'}

        old_status = request.status
        
        if status == 'CANCELLED':
            # SPECIAL BUSINESS RULE: Revert request back to WAITING status if cancelled,
            # allowing other teams to pick it up, unless it's cancelled by the citizen.
            # We fetch performer role: if they are rescue team, we revert to WAITING.
            performer = self.user_repo.get_by_id(performed_by_user_id)
            
            # Log history before modifying request details
            team_id = request.assigned_team_id or 0
            self.rescue_repo.add_history_log(
                request_id=request.id,
                team_id=team_id,
                action='CANCELLED_BY_TEAM',
                notes=f'Đội cứu hộ hủy nhiệm vụ: {notes}. Yêu cầu chuyển về trạng thái Đang Chờ.',
                performed_by=performed_by_user_id
            )
            
            # Revert to waiting state so other teams can view and assign
            request.status = 'WAITING'
            request.assigned_team_id = None
            
            if team_id > 0:
                team = self.user_repo.get_rescue_team_by_id(team_id)
                if team:
                    team.status = 'ACTIVE'
            
            self.rescue_repo.save()

            # Notify the citizen that the team had to cancel but their request is back in queue
            self.notif_repo.create_notification(
                user_id=request.user_id,
                title="Đội cứu hộ đã hủy bỏ, yêu cầu của bạn đang chờ đội khác",
                content="Do sự cố khách quan, đội cứu hộ tiếp nhận trước đó đã phải hủy nhiệm vụ. Yêu cầu cứu hộ của bạn đã được đưa lại danh sách Đang chờ. Chúng tôi sẽ điều phối đội khác ngay lập tức.",
                type="RESCUE"
            )
            self.notif_repo.save()
            
            return {'success': True, 'request': request.to_dict(), 'reverted': True}

        else:
            # Update normally (MOVING, COMPLETED)
            request.status = status
            team = self.user_repo.get_rescue_team_by_id(request.assigned_team_id)
            
            if status == 'COMPLETED':
                if team:
                    team.status = 'ACTIVE' # Set team back to active
                # Notify citizen
                self.notif_repo.create_notification(
                    user_id=request.user_id,
                    title="Nhiệm vụ cứu hộ hoàn thành",
                    content="Đội cứu hộ đã hoàn thành hỗ trợ. Chúc bạn và gia đình luôn an toàn!",
                    type="RESCUE"
                )
                self.notif_repo.save()
            
            self.rescue_repo.add_history_log(
                request_id=request.id,
                team_id=request.assigned_team_id or 0,
                action=status,
                notes=notes,
                performed_by=performed_by_user_id
            )
            self.rescue_repo.save()
            
            return {'success': True, 'request': request.to_dict(), 'reverted': False}
            
    def citizen_cancel_request(self, request_id, user_id):
        """Allow a citizen to cancel their own request (terminal state)."""
        request = self.rescue_repo.get_by_id(request_id)
        if not request:
            return {'success': False, 'message': 'Không tìm thấy yêu cầu cứu hộ.'}
        
        if request.user_id != user_id:
            return {'success': False, 'message': 'Bạn không thể hủy yêu cầu của người khác.'}
            
        request.status = 'CANCELLED'
        team_id = request.assigned_team_id
        if team_id:
            team = self.user_repo.get_rescue_team_by_id(team_id)
            if team:
                team.status = 'ACTIVE'
                
        self.rescue_repo.add_history_log(
            request_id=request.id,
            team_id=team_id or 0,
            action='CANCELLED_BY_USER',
            notes='Người dân tự hủy yêu cầu cứu hộ.',
            performed_by=user_id
        )
        self.rescue_repo.save()
        return {'success': True, 'request': request.to_dict()}
