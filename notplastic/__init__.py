import os, sys

from flask import Flask
from sqlalchemy import create_engine, MetaData
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(**config):
    app = Flask(__name__, static_url_path='')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notplastic.db'
    app.config['SQLALCHEMY_ECHO'] = True

    app.config.update(config)

    db.init_app(app)

    from notplastic.mercadopago_ipn.views import mod as mp_views
    app.register_blueprint(mp_views)

    return app
