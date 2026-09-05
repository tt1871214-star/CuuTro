from database.db import db

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, id):
        return self.model.query.get(id)

    def get_all(self):
        return self.model.query.all()

    def add(self, entity):
        db.session.add(entity)
        return entity

    def update(self, entity):
        # SQLAlchemy tracks changes on session-attached objects automatically,
        # but this method clarifies the pattern.
        return entity

    def delete(self, entity):
        db.session.delete(entity)

    def save(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()
