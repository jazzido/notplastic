import json

from sqlalchemy.orm import relationship, foreign
from sqlalchemy import func

from notplastic import db

class CollectionStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    status = db.Column(db.String(64), nullable=False)
    body = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(), default=func.now())

    @property
    def payer_email(self):
        if self.body is None:
            return None
        j = json.loads(self.body)
        return j['response']['collection']['payer']['email']


class Collection(db.Model):
    """ `collection` as in payment, not as an ordered set of things """
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Text(), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    created_at = db.Column(db.DateTime(), default=func.now())
    email_sent_at = db.Column(db.DateTime())
    statuses = relationship(CollectionStatus, backref='collection')
