import os, sys

from flask import Flask
from sqlalchemy import create_engine, MetaData
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask_limiter import Limiter
from flask_wtf.csrf import CsrfProtect

db = SQLAlchemy()
limiter = Limiter()
mail = Mail()
csrf = CsrfProtect()

def create_app(**config):
    app = Flask(__name__, static_url_path='')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notplastic.db'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SECRET_KEY'] = 'this is not secure, please set a real key when deploying'
    app.config['SESSION_COOKIE_HTTPONLY'] = False

    app.config.update(config)

    db.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    from notplastic.mercadopago_ipn.views import mod as mp_views
    from notplastic.notplastic_site.views import mod as nps_views
    app.register_blueprint(mp_views)
    app.register_blueprint(nps_views)

    return app
