from flask import Flask


def create_app(config=None):

	app = Flask(__name__)

	if config is None:
		app.config.from_pyfile('config.py') 
	else:
		app.config.update(config)

	return app


def register_routes(app):
	pass

def register_mail(app):
	pass

def register_db(app):
	pass

def register_celery(app):
	pass

def register_login_manager(app):
	pass