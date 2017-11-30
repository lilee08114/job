from suite import BaseSuite


class TestSignup(BaseSuite):

	def test_signup_page(self):
		res = self.client.get(self.url_for('user.regis'))
		self.assertIn('<form>', res.data)

	def test_form_elements_required(self):
		'''name, email, passwd1, passwd2 all are needed!
		'''
		res = self.client.post(self.url_for('user.regis'), 
					data={'mail':'test@email.com', 'passwd1':'1',
							'passwd2':'1'})
		self.assertIn(??????)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'passwd1':'1',
							'passwd2':'1'})
		self.assertIn(??????)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd2':'1'})
		self.assertIn(??????)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd1':'1'})
		self.assertIn(??????)

	def test_invalid_form_elements(slef):
		'''name: length 3-64, email: email format, passwd1 is same as passwd2
		'''
		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'n', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn(??????)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn', 
							'mail':'test@email.com','passwd1':'1','passwd2':'1'})
		self.assertIn(??????)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn(??????) 

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'n', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'12'})
		self.assertIn(??????)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn(??????)

class TestSignin(BaseSuite):

	def test_signin_page(self):
		res = self.client.get(self.url_for())

	def test_sign_in(self):
		self.prepare_user()

	