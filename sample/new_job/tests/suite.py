
import os
import unittest
import tempfile
#here need some test configuration
from flask import url_for
from flask_login import current_user
from new_job.app import create_app
from new_job.app.model import User, Post, Comment
from new_job.app.extensions import db

#Again!!!!!! Module Import Error!!!!!WHAT THE HELL

class BaseSuite(unittest.TestCase):
	def setUp(self):
		app = create_app(some_config)
		app.debug = True
		self.db_fd, self.db_file = tempfile.mkstemp()
		app. config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(self.db_file)
		self.app = app
		self.client = app.test_client()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		os.close(self.db_fd)
		os.unlink(self.db_file)

	def prepare_user(self):
		foo = User(name='foo', password='1', mail='foo@email.com')
		bar = User(name='bar', password='1', mail='bar@email.com')
		baz = User(name='baz', password='1', mail='baz@email.com')
		with self.app.app_context():
			db.session.add(foo)
			db.session.add(bar)
			db.session.add(baz)
			db.commit()

	def login(self):
		self.prepare_user()
		res = self.client.post(self.url_for('user.login'), data={
				'name':'foo', 'password':'1'}, follow_redirects=True)
		self.assertIn('Welcome back', res.data)

	def logout(self):
		res = self.client.get('user.logout', follow_redirects=True)
		self.assertIn('Welcome to Stoya', res.data)
		#?????????how to test?

	def url_for(self, endpoint, **kwargs):
		with self.app.request_context():
			return url_for(endpoint, **kwargs)

	def prepare_post(self):

		post1 = Post(title='this is post 1',
					post='this is some text! #1 job link test', author_id=current_user.id)
		post1 = Post(title='this is post 2',
					post='this is some text too!', author_id=current_user.id)
		db.session.add(post1)
		db.session.add(post2)
		db.session.commit()



