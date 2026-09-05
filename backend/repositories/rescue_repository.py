from repositories.base_repository import BaseRepository
from models.rescue import RescueRequest, RescueTeam, RescueHistory
from database.db import db

class RescueRepository(BaseRepository):
    def __init__(self):
        super().__init__(RescueRequest)

    def get_all_active_requests(self):
        """Get requests that are not COMPLETED or CANCELLED."""
        return RescueRequest.query.filter(
            RescueRequest.status.in_(['WAITING', 'RECEIVED', 'MOVING'])
        ).order_by(RescueRequest.created_at.desc()).all()

    def get_requests_by_user_id(self, user_id):
        return RescueRequest.query.filter_by(user_id=user_id).order_by(RescueRequest.created_at.desc()).all()

    def get_requests_by_team_id(self, team_id):
        return RescueRequest.query.filter_by(assigned_team_id=team_id).order_by(RescueRequest.created_at.desc()).all()

    def get_history_by_request_id(self, request_id):
        return RescueHistory.query.filter_by(request_id=request_id).order_by(RescueHistory.created_at.asc()).all()

    def add_history_log(self, request_id, team_id, action, notes, performed_by):
        log = RescueHistory(
            request_id=request_id,
            team_id=team_id,
            action=action,
            notes=notes,
            performed_by=performed_by
        )
        db.session.add(log)
        return log
