from datetime import timedelta, datetime
import string, random, json, uuid

from sqlalchemy.orm import relationship, foreign
from sqlalchemy import func
from sqlalchemy_sluggable import Sluggable

from flask import url_for, current_app

from notplastic import db, utils, mercadopago_ipn


class DownloadCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(12), nullable=False)
    max_downloads = db.Column(db.Integer, default=5)
    is_download_card = db.Column(db.Boolean, default=False)
    mercadopago_collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    download_tickets = relationship('DownloadTicket', lazy='dynamic', backref='download_code')

    __table_args__ = (db.Index('project_code_idx',
                               'project_id',
                               'code',
                               unique=True),)

    def times_downloaded(self):
        return self.download_tickets.filter(DownloadTicket.downloaded_at != None).count()

    def __unicode__(self):
        return self.code

    @classmethod
    def get_unique_code(cls, project, length=-1):
        if length == -1:
            length = current_app.config.get('DOWNLOAD_CODE_LENGTH', 6)
        rs = lambda: ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
        while True:
            code = rs()
            c = db.session.query(cls) \
                          .filter(cls.code==code) \
                          .filter(cls.project==project) \
                          .count()
            if c == 0:
                return code

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
    description = db.Column(db.Text())
    extended_description = db.Column(db.Text())
    amount = db.Column(db.Numeric(precision=2))
    max_amount = db.Column(db.Numeric(precision=2), nullable=True)
    suggested_amount = db.Column(db.Numeric(precision=2), nullable=True)
    max_downloads = db.Column(db.Integer, nullable=False, default=5)
    file = db.Column(db.String(255), nullable=False)
    background_image_url = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime(), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    download_codes = relationship(DownloadCode, lazy='dynamic', backref='project')
    mp_payment_preferences = relationship('MercadoPagoPaymentPreference', backref='project')

    __sluggable__ = slug_options = {
        'populate_from': 'name'
    }

    def __unicode__(self):
        return "%s" % self.name

    @property
    def is_variable_price(self):
        return self.max_amount is not None

class MercadoPagoPaymentPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    payment_preference_id = db.Column(db.String(50))
    amount = db.Column(db.Numeric(precision=2))
    definition = db.Column(db.Text())

    @classmethod
    def save_to_mercadopago(cls, payment_preference):
        if payment_preference.definition is not None:
            # refuse to save if not new
            return

        mp = utils.get_MP_client()
        response = mp.create_preference({
            'items': [
                {
                    'title': payment_preference.project.name,
                    'description': payment_preference.project.description,
                    'quantity': 1,
                    'currency_id': 'ARS',
                    'unit_price': payment_preference.amount,
                }
            ],
            'external_reference': payment_preference.project.id,
            'back_urls': {
                'success': url_for('notplastic_site.payment_confirmation', project=payment_preference.project.slug, status='success', _external=True),
                'failure': url_for('notplastic_site.payment_confirmation', project=payment_preference.project.slug, status='failure', _external=True),
                'pending': url_for('notplastic_site.payment_confirmation', project=payment_preference.project.slug, status='pending', _external=True),
            }
        })

        payment_preference.definition = json.dumps(response['response'])
        payment_preference.payment_preference_id = response['response']['id']

        return payment_preference


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), default=func.now())

    projects = relationship('Project', lazy='dynamic', backref='user')
