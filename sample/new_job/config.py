class BaseConfig():
	SUBJECT_PREFIX = '主题前缀'
	MAIL_DEFAULT_SENDER = '发送者<422758783@qq.com>'
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PASSWORD = 'krzarygxvvhzcafb'
	MAIL_USERNAME = '422758783@qq.com'
	MAIL_USE_SSL = False
	MAIL_USE_TLS = True
	MAIL_PORT = 587
	ADMIN_MAIL='422758783@qq.com'

class Production(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:a123@localhost:3306/stoya'
	SQLALCHEMY_ECHO = False
	SECRET_KEY = 'I AM VERY STRONG'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	DEBIUG = False
	TESTING = False

class Development(BaseConfig):

	#SQLALCHEMY_DATABASE_URI = 'C:\\works\\new\sample\\new_job'
	SERVER_NAME = 'www.127.0.01.com'
	SQLALCHEMY_ECHO = False
	SECRET_KEY = 'I AM VERY STRONG'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	WTF_CSRF_ENABLED = False
	DEBIUG = True
	TESTING = True