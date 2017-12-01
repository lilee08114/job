
import os
import unittest
import tempfile
#here need some test configuration
from flask import url_for
from app import create_app
from app.model import User

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
				name='foo', password='1'}, follow_redirects=True)
		self.assertIn('welcome', res.data)

	def logout(self):
		res = self.client.get('user.logout')
		#?????????how to test?

	def url_for(self, endpoint, **kwargs):
		with self.app.request_context():
			return url_for(endpoint, **kwargs)



