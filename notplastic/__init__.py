import os, sys

from flask import Flask
from sqlalchemy import create_engine, MetaData
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.assets import Environment
from flask.ext.superadmin import Admin, model as admin_model
from flask.ext.superadmin.contrib.fileadmin import FileAdmin
from flask_limiter import Limiter
from flask_wtf.csrf import CsrfProtect
from flask.ext.collect import Collect
from flaskext.markdown import Markdown

DEV_SERVER_NAME = 'dev.local.unabanda.cc:5000'

DEV_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///%s/notplastic.db' % os.path.abspath(os.path.dirname(__file__)),
    'SQLALCHEMY_ECHO': True,
    'SECRET_KEY': 'this is not secure, please set a real key when deploying',
    'SESSION_COOKIE_HTTPONLY': False,
    'MERCADOPAGO_USE_SANDBOX': True,
    'SERVER_NAME': DEV_SERVER_NAME,
    'DEFAULT_MAIL_SENDER': 'testing@unabanda.cc',
    'DOWNLOAD_CODE_LENGTH': 6,
    'DEV': True,
    'PROJECT_FILES_PATH': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'project_files'),
    'GOOGLE_ANALYTICS_ID': 'UA-99999-99'
}

db = SQLAlchemy()
limiter = Limiter()
mail = Mail()
csrf = CsrfProtect()
assets_env = Environment()
collect = Collect()

def create_app(**config):
    app = Flask(__name__, static_url_path='')
    app.config.update(config)

    db.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    assets_env.init_app(app)
    csrf.init_app(app)
    collect.init_app(app)

    Markdown(app)

    if not app.config.get('TESTING'):
        create_admin(app)

    from notplastic.mercadopago_ipn.views import mod as mp_views
    from notplastic.notplastic_site.views import mod as nps_views
    app.register_blueprint(mp_views)
    app.register_blueprint(nps_views)


    return app

class AdminProject(admin_model.ModelAdmin):
    session = db.session
    list_display = ('name',)
    fields = ('name', 'description', 'extended_description', 'amount', 'max_amount', 'suggested_amount', 'max_downloads', 'background_image_url', 'extra_head_html', 'file')


def create_admin(app):
    admin = Admin(app, 'Not Plastic', '/admin')
    from notplastic.notplastic_site import models as np_models
    admin.register(np_models.User, session=db.session)
    admin.register(np_models.Project, AdminProject)
    admin.add_view(FileAdmin(app.config['PROJECT_FILES_PATH'], 'project_files', name='Project Files'))
