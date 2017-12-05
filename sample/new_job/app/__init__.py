from flask import Flask
from flask_login import LoginManager
from app.model import User, Company
from flask_bootstrap import Bootstrap
from app.extensions import db, ce, login_manager, mail
from . import config
import pdb

def create_app(config=None):

	app = Flask(__name__)

	if config is None:
		app.config.from_pyfile('config.py') 
	else:
		app.config.update(config)

	bootstrap = Bootstrap(app)
	register_routes(app)
	register_mail(app)
	#pdb.set_trace()
	register_db(app)
	register_login_manager(app)
	register_jinja(app)
	return app


def register_routes(app):
	from .handlers import forum, subscribe, user, front

	app.register_blueprint(forum.bp, url_prefix='/forum')
	app.register_blueprint(front.bp, url_prefix='')
	app.register_blueprint(subscribe.bp, url_prefix='/subscribe')
	app.register_blueprint(user.bp, url_prefix='/user')
	return app

def register_mail(app):
	mail.init_app(app)
	return app


def register_db(app):
	db.app = app
	db.init_app(app)
	db.create_all()
	return app

def register_login_manager(app):
	login_manager.init_app(app)
	login_manager.session_protection = 'basic'
	login_manager.login_view = 'user.login'

	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(user_id)
	return app

def register_jinja(app):
	@app.context_processor
	def user_processor():
		def get_author_name(author_id):
			author_name = User.query.get(author_id).name
			return author_name
		return dict(get_author_name=get_author_name)

	@app.context_processor
	def company_processor():
		def get_company(company_id):
			company = Company.query.get(company_id)
			return company
		return dict(get_company=get_company)


def make_celery(app):
	#Integrate the Flask and Celery
	TaskBase = ce.Task
	class FlaskTask(TaskBase):
		abstract = True
		def __call__(self, *args, **kwargs):
			with app.app_context():
				return Task.__call__(self, *args, **kwargs)
	ce.Task = FlaskTask
	return ce

app = create_app()
ce = make_celery(app)

