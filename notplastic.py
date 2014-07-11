from flask import Flask
from sqlalchemy import create_engine, MetaData
from db import db

app = Flask(__name__, static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notplastic.db'
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', 8081)
