from flask_login import current_user
from suite import BaseSuite
from app.model import User


class TestSignup(BaseSuite):

	def test_signup_page(self):
		res = self.client.get(self.url_for('user.regis'))
		self.assertIn('<form>', res.data)
		self.assertIn('Register', res.data)

	def test_form_elements_required(self):
		'''name, email, passwd1, passwd2 all are needed!
		NEED CLOSE THE CSRF PROTECTION
		'''
		res = self.client.post(self.url_for('user.regis'), 
					data={'mail':'test@email.com', 'passwd1':'1',
							'passwd2':'1'})
		self.assertIn('This field is required', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'passwd1':'1',
							'passwd2':'1'})
		self.assertIn('This field is required', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd2':'1'})
		self.assertIn('This field is required', res.data)
		self.assertIn('password must match', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd1':'1'})
		self.assertIn('This field is required', res.data)

	def test_invalid_form_elements(slef):
		'''name: length 3-64, email: email format, passwd1 is same as passwd2
		'''
		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'n', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn('between 3 and 64 characters long', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn\
					nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn', 
							'mail':'test@email.com','passwd1':'1','passwd2':'1'})
		self.assertIn('between 3 and 64 characters long', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn('Invalid email address', res.data) 

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'12'})
		self.assertIn('password must match', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn(??????)

class TestSignin(BaseSuite):

	def test_signin_page(self):
		res = self.client.get(self.url_for('user.login'))
		self.assertIn(???)

	def test_sign_in(self):
		self.prepare_user()
		res = self.client.post(self.url_for('user.login'),
						data={'name':'', 'password':'1'})
		self.assertIn('This field is required', res.data)

		res = self.client.post(self.url_for('user.login'),
						data={'name':'foo', 'password':''})
		self.assertIn('This field is required', res.data)

		res = self.client.post(self.url_for('user.login'),
						data={'name':'foo1', 'password':'1'})
		self.assertIn('Incorrect name or password!', res.data)

		res = self.client.post(self.url_for('user.login'),
						data={'name':'foo', 'password':'11'})
		self.assertIn('Incorrect name or password!', res.data)

		res = self.client.post(self.url_for('user.login'),
						data={'name':'foo', 'password':'1'})
		self.assertIn('Welcome back', res.data)

		#more tests here look up the session id?
		#vist some login required pages
class TestUser(BaseSuite):

	def test_user_page(self):
		res = self.client.get('user.user')
		self.assertIn(????????)

class TestSignout(BaseSuite):

	def test_logout(self):
		res = self.client.get(self.url_for('use.logout'), follow_redirects=True)
		self.assertIn('Welcome to Stoya', res.data)

	#visit some login required pages

class TestResetCode(BaseSuite):

	def test_reset_page(self):
		#need to be improved
		res = self.client.get(self.url_for('use.reset'))
		self.assertIn('</form>', res.data)
	
	def test_invalid_reset_form(self):
		self.login()
		res = self.client.post(self.url_for('use.reset'),
				data={'origin':'', 'new1':'22', 'new2':'22'})
		self.assertIn(?????)

		res = self.client.post(self.url_for('use.reset'),
				data={'origin':'1', 'new1':'', 'new2':''})
		self.assertIn(?????)

		res = self.client.post(self.url_for('use.reset'),
				data={'origin':'1', 'new1':'22', 'new2':''})
		self.assertIn(?????)

		res = self.client.post(self.url_for('use.reset'),
				data={'origin':'1', 'new1':'22', 'new2':'21'})
		self.assertIn(?????)

		res = self.client.post(self.url_for('use.reset'),
				data={'origin':'11', 'new1':'22', 'new2':'22'})
		self.assertIn(?????)

		res = self.client.post(self.url_for('use.reset'),
				data={'origin':'1', 'new1':'1', 'new2':'1'})
		self.assertIn(?????)

		res = self.client.post(self.url_for('use.reset'),
				data={'origin':'1', 'new1':'22', 'new2':'22'})
		self.assertIn(?????)

class TestConfirmMail(BaseSuite):
	def test_confirm_mail(self):
		#login in 1st
		self.prepare_user()
		res = self.client.post(self.url_for('user.login'),
						data={'name':'foo', 'password':'1'})
		self.assertIn(?????????)
		token = current_user._get_current_object().generate_token()
		confirm_link = self.url_for('user.confirm_mail', token=token, _external=True)

		res = self.client.get(confirm_link, follow_redirects=True)
		self.assertIn('You email address has been confirmed', res.data)
		self.assertTrue(current_user.confirm)

		#here visist some email confirmed function