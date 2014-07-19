from datetime import timedelta, datetime
import string, random
import uuid

from sqlalchemy.orm import relationship, foreign
from sqlalchemy import func
from sqlalchemy_sluggable import Sluggable

from notplastic import db

class DownloadCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(12), nullable=False)
    max_downloads = db.Column(db.Integer, nullable=False, default=5)
    is_download_card = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    download_tickets = relationship('DownloadTicket', lazy='dynamic', backref='download_code')

    __table_args__ = (db.Index('project_code_idx',
                               'project_id',
                               'code',
                               unique=True),)

    def times_downloaded(self):
        return self.download_tickets.filter(DownloadTicket.downloaded_at != None).count()

class DownloadTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.String(40), nullable=False, unique=True)
    time_to_live = db.Column(db.Integer, nullable=False, default=24*60*60)
    created_at = db.Column(db.DateTime(), default=func.now())
    downloaded_at = db.Column(db.DateTime())
    download_code_id = db.Column(db.Integer, db.ForeignKey('download_code.id'))

    def has_expired(self, now=None):
        if now is None:
            now = datetime.now()

        return (now - self.created_at).total_seconds() >= self.time_to_live

    @classmethod
    def get_unique_ticket(cls):
        while True:
            t = uuid.uuid1().get_hex()
            c = db.session.query(cls) \
                          .filter(cls.ticket==t) \
                          .count()
            if c == 0:
                return t

class Project(db.Model, Sluggable):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    amount = db.Column(db.Numeric(precision=2))
    file = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    download_codes = relationship(DownloadCode, backref='project')

    __sluggable__ = slug_options = {
        'populate_from': 'name'
    }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), default=func.now())

    projects = relationship('Project', lazy='dynamic', backref='user')
