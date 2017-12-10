
import os
import unittest
import tempfile
import time
#here need some test configuration
from flask import url_for
from flask_login import current_user
from app import create_app
from app.model import User, Post, Comment
from app.extensions import db
from config import Development

#Again!!!!!! Module Import Error!!!!!WHAT THE HELL

class BaseSuite(unittest.TestCase):
	def setUp(self):
		#self.db_fd, self.db_file = tempfile.mkstemp()

		DATABASE_URI = 'sqlite:///C:\\works\\new\sample\\new_job\\for_test.db'
		setattr(Development, 'SQLALCHEMY_DATABASE_URI', DATABASE_URI)
		app = create_app(Development)
		self.app = app
		self.client = app.test_client()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		#db.session.close()
		
		#os.close(self.db_fd)
		#os.close(self.db_fd)
		#os.unlink(self.db_file)
		#try:
		#	f = open(self.db_fd, 'w')

			#os.unlink(self.db_file)
		#finally:
		#	os.unlink(self.db_file)

	def prepare_user(self):
		foo = User(name='foo', password='1', mail='foo@email.com')
		bar = User(name='bar', password='1', mail='bar@email.com')
		baz = User(name='baz', password='1', mail='baz@email.com')

		db.session.add(foo)
		db.session.add(bar)
		db.session.add(baz)
		try:
			db.session.commit()
		except:
			db.session.rollback()

	def login(self):
		self.prepare_user()
		res = self.client.post(self.url_for('user.login'), data={
			'name':'foo', 'password':'1'}, follow_redirects=True)
		self.assertIn(b'Welcome back', res.data)

	def logout(self):
		res = self.client.get(self.url_for('user.logout'), follow_redirects=True)
		#self.assertIn(b'Welcome to Stoya', res.data)
		#?????????how to test?

	def url_for(self, endpoint, **kwargs):
		with self.app.app_context():
			return url_for(endpoint, **kwargs)

	def prepare_post(self):
		
		#with self.client:
			self.login()
			post1 = Post(title='this is post 1',
					post='this is some text! #1 job link test', author_id=current_user.id)
			post2 = Post(title='this is post 2',
					post='this is some text too!', author_id=current_user.id)
			db.session.add(post1)
			db.session.add(post2)
			db.session.commit()



