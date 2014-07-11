from sqlalchemy.orm import relationship, foreign
from sqlalchemy import func

from db import db

class Collection(db.Model):
    """ a `collection` as in payment, not an ordered set of things """
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(), default=func.now())
    # url = db.Column(db.Text())
