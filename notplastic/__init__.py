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
from flask.ext.cdn import CDN
from flask_bootstrap import Bootstrap

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
    'CDN_DOMAIN': DEV_SERVER_NAME,
    'CDN_DEBUG': True,
    'AUTH0_CLIENT_ID': 'HJl2RIXuBq1022WWqZzJobGZDhw1ciW8',
    'AUTH0_CLIENT_SECRET': 'MMuSbWVL3_PqrDGS-Uamu6_K-G-_Y3osqMrztdtXw_rVxOTR9vlolyjEtJsGigS1',
    'AUTH0_DOMAIN': 'unabanda.auth0.com',
    'AUTH0_CALLBACK_URL': 'http://%s/auth0/callback' % DEV_SERVER_NAME,
    'BOOTSTRAP_SERVE_LOCAL': True
}

db = SQLAlchemy()
limiter = Limiter()
mail = Mail()
csrf = CsrfProtect()
assets_env = Environment()
collect = Collect()
cdn = CDN()
bootstrap = Bootstrap()

def create_app(**config):
    app = Flask(__name__, static_url_path='')
    app.config.update(config)

    db.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    assets_env.init_app(app)
    csrf.init_app(app)
#    collect.init_app(app)
    #cdn.init_app(app)
    bootstrap.init_app(app)

    Markdown(app)

    if not app.config.get('TESTING'):
        create_admin(app)

    from notplastic.mercadopago_ipn.views import mod as mp_views
    from notplastic.user_dashboard.views import mod as ud_views
    from notplastic.notplastic_site.views import mod as nps_views
    from notplastic.auth0.views import mod as auth0_views

    app.register_blueprint(mp_views)
    app.register_blueprint(ud_views)
    app.register_blueprint(nps_views)
    app.register_blueprint(auth0_views)

    return app

class AdminProject(admin_model.ModelAdmin):
    session = db.session
    list_display = ('name',)
    fields = ('name', 'description', 'extended_description', 'amount', 'max_amount', 'suggested_amount', 'max_downloads', 'background_image_url', 'file')


def create_admin(app):
    admin = Admin(app, 'Not Plastic', '/saracatungacatunga')
    from notplastic.notplastic_site import models as np_models
    admin.register(np_models.User, session=db.session)
    admin.register(np_models.Project, AdminProject)
    admin.add_view(FileAdmin(app.config['PROJECT_FILES_PATH'], 'project_files', name='Project Files'))
