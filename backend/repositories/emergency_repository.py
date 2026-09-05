from repositories.base_repository import BaseRepository
from models.emergency import EmergencyContact
from database.db import db

class EmergencyRepository(BaseRepository):
    def __init__(self):
        super().__init__(EmergencyContact)

    def get_active_contacts(self):
        return EmergencyContact.query.filter_by(is_active=True).order_by(EmergencyContact.sort_order.asc()).all()
