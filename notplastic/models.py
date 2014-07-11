from sqlalchemy.orm import relationship, foreign
from sqlalchemy import func

from db import db

class DownloadCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text(), nullable=False)
    max_downloads = db.Column(db.Integer, nullable=False, default=5)
    is_download_card = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

class DownloadTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime(), default=func.now())

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    file = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(), default=func.now())

    download_codes = relationship(DownloadCode)
