from repositories.base_repository import BaseRepository
from models.user import User
from models.rescue import RescueTeam
from models.role import Role

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_phone(self, phone):
        return User.query.filter_by(phone=phone).first()

    def get_role_by_name(self, name):
        return Role.query.filter_by(name=name).first()

    def get_rescue_team_by_user_id(self, user_id):
        return RescueTeam.query.filter_by(user_id=user_id).first()

    def get_rescue_team_by_id(self, team_id):
        return RescueTeam.query.get(team_id)

    def get_all_rescue_teams(self):
        return RescueTeam.query.all()
