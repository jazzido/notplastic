from sqlalchemy.orm import relationship, foreign
from sqlalchemy import func

from notplastic import db

class CollectionStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    status = db.Column(db.String(64), nullable=False)
    body = db.Column(db.Text(), nullable=False)

class Collection(db.Model):
    """ `collection` as in payment, not as an ordered set of things """
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(), default=func.now())
    statuses = relationship(CollectionStatus, backref='collection')
