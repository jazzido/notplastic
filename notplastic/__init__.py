import os, sys

from flask import Flask
from sqlalchemy import create_engine, MetaData
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.assets import Environment
from flask.ext.superadmin import Admin
from flask_limiter import Limiter
from flask_wtf.csrf import CsrfProtect

DEV_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///%s/notplastic.db' % os.path.abspath(os.path.dirname(__file__)),
    'SQLALCHEMY_ECHO': True,
    'SECRET_KEY': 'this is not secure, please set a real key when deploying',
    'SESSION_COOKIE_HTTPONLY': False,
    'MERCADOPAGO_USE_SANDBOX': True,
    'SERVER_NAME': 'dev.local.unabanda.cc:5000',
    'DEFAULT_MAIL_SENDER': 'testing@unabanda.cc',
    'DOWNLOAD_CODE_LENGTH': 6
}

db = SQLAlchemy()
limiter = Limiter()
mail = Mail()
csrf = CsrfProtect()
assets_env = Environment()

def create_app(**config):
    app = Flask(__name__, static_url_path='')
    app.config.update(config)

    db.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    assets_env.init_app(app)
    csrf.init_app(app)

    create_admin(app)

    from notplastic.mercadopago_ipn.views import mod as mp_views
    from notplastic.notplastic_site.views import mod as nps_views
    app.register_blueprint(mp_views)
    app.register_blueprint(nps_views)

    return app

def create_admin(app):
    admin = Admin(app, 'Not Plastic')
    from notplastic.notplastic_site import models as np_models
    admin.register(np_models.User, session=db.session)
    admin.register(np_models.Project, session=db.session)
