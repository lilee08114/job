from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin, AnonymousUserMixin, current_user
from flask import Flask, current_app
from app.extensions import db
from app.helper import CRUD_Model


class User(UserMixin, db.Model):
	__tablename__ = 'user'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	name = db.Column(db.String(30), unique=True, nullable=False)
	passwd_hash = db.Column(db.String(512), nullable=False)
	mail = db.Column(db.String(30), unique=True, nullable=False)
	focus = db.Column(db.String(100))
	time = db.Column(db.DateTime(), default=datetime.now())
	confirm = db.Column(db.Boolean(), default=False)

	posts = db.relationship('Post', back_populates='author', lazy='dynamic')
	comments = db.relationship('Comment', back_populates='author', lazy='dynamic')
	sub_info = db.relationship('Subscribe', back_populates='user', lazy='dynamic')
	profile = db.relationship('Profile', back_populates='user', lazy='dynamic')

	@property
	def password(self):
		return ('You can not access it!')

	@password.setter
	def password(self, num):
		self.passwd_hash = generate_password_hash(num)

	def verify_passwd(self, num):
		return check_password_hash(self.passwd_hash, num)

	def generate_token(self):
		s = Serializer(current_app.config['SECRET_KEY'], 600)
		return s.dumps({'id':self.id})

	def decode_token(self, token):
		s = Serializer(current_app.config['SECRET_KEY'], 600)
		return s.loads(token)
		


class Post(db.Model):
	__tablename__ = 'post'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	post = db.Column(db.Text(), nullable=False)
	post_time = db.Column(db.DateTime(), default=datetime.now())
	labels = db.Column(db.Text())

	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	author = db.relationship('User', back_populates='posts', lazy=True)
	comment = db.relationship('Comment', back_populates='post', lazy='dynamic')
	

class Comment(db.Model):
	__tablename__ = 'comments'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	comment = db.Column(db.Text(), nullable=False)
	comment_time = db.Column(db.DateTime(), default=datetime.now())

	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	author = db.relationship('User', back_populates='comments', lazy=True) 
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
	post = db.relationship('Post', back_populates='comment', lazy=True)


class Jobbrief(db.Model):
	__tablename__ = 'brief'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	key_word = db.Column(db.String(50))
	job_name = db.Column(db.String(50))
	job_location = db.Column(db.String(20))
	job_salary_low = db.Column(db.Integer)
	job_salary_high= db.Column(db.Integer)
	job_exp = db.Column(db.Integer)
	job_edu = db.Column(db.String(20))
	job_quantity = db.Column(db.String(20))
	job_time = db.Column(db.DateTime())
	job_other_require = db.Column(db.String(50))
	job_labels = db.Column(db.Text())

	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	#下面这一个，在实际存储中，应当注意，在订阅中需要，非订阅中不需要, 每次对结果的存贮都需要判断
	subscribe_id = db.Column(db.Integer, db.ForeignKey('subInfo.id')) 
	
	job_link = db.relationship('Jobsite', back_populates='brief', lazy='dynamic')
	company = db.relationship('Company', back_populates='job', lazy=True)
	detail = db.relationship('Jobdetail', back_populates='abstract', lazy='dynamic')
	sub_info = db.relationship('Subscribe', back_populates='brief')


class Profile(db.Model):
	__tablename__ = 'profile'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	salary = db.Column(db.Integer)
	exp = db.Column(db.Integer)
	edu = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)

	user = db.relationship('User', back_populates='profile')


class Assessment(db.Model):
	__tablename__ = 'assess'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	key_word = db.Column(db.String(50))
	count = db.Column(db.Integer)
	average_salary = db.Column(db.Integer)
	updated_time = db.Column(db.DateTime())

class Jobsite(db.Model):
	__tablename__ = 'site'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	site = db.Column(db.String(100))
	brief_id = db.Column(db.Integer, db.ForeignKey('brief.id'))
	
	brief = db.relationship('Jobbrief', back_populates='job_link')


class Jobdetail(db.Model):
	__tablename__ = 'requirement'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	requirement = db.Column(db.Text())
	brief_id = db.Column(db.Integer, db.ForeignKey('brief.id'))

	abstract = db.relationship('Jobbrief', back_populates='detail')


class Company(db.Model):
	__tablename__ = 'company'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	company_name = db.Column(db.String(50))
	company_site = db.Column(db.String(100))

	job = db.relationship('Jobbrief', back_populates='company', lazy='dynamic')

class Subscribe(db.Model):
	__tablename__ = 'subInfo'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True) 	#before
	sub_key = db.Column(db.String(50), nullable=False)					#before
	sub_start = db.Column(db.DateTime(), default=datetime.now())		#before
	sub_end = db.Column(db.DateTime())									#after
	subscriber_id = db.Column(db.Integer, db.ForeignKey('user.id'))		#before
	
	brief = db.relationship('Jobbrief', back_populates='sub_info', lazy='dynamic')
	user = db.relationship('User', back_populates='sub_info')

class Ip_pool(db.Model):
	__tablename__ = 'ips'

	id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	ip = db.Column(db.String(20), nullable=False, unique=True)
	port = db.Column(db.String(10), nullable=False)	
	scheme = db.Column(db.String(10), nullable=False)
	qc_status = db.Column(db.Boolean, default=True)
	lg_status = db.Column(db.Boolean, default=True)
	lp_status = db.Column(db.Boolean, default=True)
	security = db.Column(db.String(20), nullable=False)
	store_time = db.Column(db.DateTime(), default=datetime.now())
	qc_expire_time = db.Column(db.DateTime())
	lg_expire_time = db.Column(db.DateTime())
	lp_expire_time = db.Column(db.DateTime())