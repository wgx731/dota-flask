from flask import Flask
import flask_sqlalchemy
import os

default_db_path = os.path.join(os.path.dirname(__file__), '../db/local.sqlite')
default_db_uri = 'sqlite:///{}'.format(default_db_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', default_db_uri
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.gtag_tracking_id = os.environ.get(
    'GTAG_TRACKING_ID',
    'your-google-tracking-id'
)
app.secret_key = os.environ.get(
    'SESSION_SECRET_KEY',
    'default_secret_key'
)

db = flask_sqlalchemy.SQLAlchemy(app)

from app import models, views
