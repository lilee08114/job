from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from flask_login import LoginManager
from flask_mail import Message, Mail


db = SQLAlchemy()
ce = Celery('celery_app', backend='amqp', broker='amqp://localhost')
login_manager = LoginManager()
mail = Mail()