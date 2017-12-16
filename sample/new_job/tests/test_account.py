from flask_login import current_user
from .suite import BaseSuite
from app.model import User


class TestSignup(BaseSuite):

	def test_signup_page(self):
		res = self.client.get(self.url_for('user.regis'))
		self.assertIn(b'</form>', res.data)
		self.assertIn(b'Register', res.data)

	def test_form_elements_required(self):
		'''name, email, passwd1, passwd2 all are needed!
		NEED CLOSE THE CSRF PROTECTION
		'''
		res = self.client.post(self.url_for('user.regis'), 
					data={'mail':'test@email.com', 'passwd1':'1',
							'passwd2':'1'})
		self.assertIn(b'This field is required', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'passwd1':'1',
							'passwd2':'1'})
		self.assertIn(b'This field is required', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd2':'1'})
		self.assertIn(b'This field is required', res.data)
		self.assertIn(b'password must match', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd1':'1'})
		self.assertIn(b'This field is required', res.data)

	def test_invalid_form_elements(self):
		'''name: length 3-64, email: email format, passwd1 is same as passwd2
		'''
		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'n', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn(b'between 3 and 64 characters long', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn\
					nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn', 
							'mail':'test@email.com','passwd1':'1','passwd2':'1'})
		self.assertIn(b'between 3 and 64 characters long', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn(b'Invalid email address', res.data) 

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'12'})
		self.assertIn(b'password must match', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn3', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'1'}, follow_redirects=True)
		self.assertIn(b'registraion succeed!', res.data)

	def test_duplicate_account(self):
		'''test duplicate name or email
		'''
		self.prepare_user()
		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'foo', 'mail':'test11@email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn(b'name already exsits!', res.data)

		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'nnn34', 'mail':'foo@email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn(b'Email has been registered!', res.data)


class TestSignin(BaseSuite):

	def test_signin_page(self):
		res = self.client.get(self.url_for('user.login'))
		self.assertIn(b'Login', res.data)
		self.assertIn(b'</form>', res.data)

	def test_sign_in(self):
		self.prepare_user()
		res = self.client.post(self.url_for('user.login'),
						data={'name':'', 'password':'1'})
		self.assertIn(b'This field is required', res.data)

		res = self.client.post(self.url_for('user.login'),
						data={'name':'foo', 'password':''})
		self.assertIn(b'This field is required', res.data)

		res = self.client.post(self.url_for('user.login'),
						data={'name':'foo1', 'password':'1'}, follow_redirects=True)
		self.assertIn(b'Incorrect name or password!', res.data)

		res = self.client.post(self.url_for('user.login'),
						data={'name':'foo', 'password':'11'}, follow_redirects=True)
		self.assertIn(b'Incorrect name or password!', res.data)

		res = self.client.post(self.url_for('user.login'),
						data={'name':'foo', 'password':'1'}, follow_redirects=True)
		self.assertIn(b'Welcome back', res.data)

		#more tests here look up the session id?
		#vist some login required pages
class TestUser(BaseSuite):

	def test_user_page(self):
		self.logout()
		res = self.client.get(self.url_for('user.user'))
		self.assertIn(b'Login', res.data)
		self.assertIn(b'</form>', res.data)
		self.login()
		res = self.client.get(self.url_for('user.user'))
		self.assertIn(b'Welcome back, foo', res.data)

class TestSignout(BaseSuite):

	def test_logout(self):
		self.login()
		res = self.client.get(self.url_for('user.logout'), follow_redirects=True)
		self.assertIn(b'Welcome to Stoya', res.data)

	#visit some login required pages

class TestResetCode(BaseSuite):

	def test_reset_page(self):
		#need to be improved
		self.logout()
		res = self.client.get(self.url_for('user.reset'), follow_redirects=True)
		self.assertIn(b'Login', res.data)
		self.assertIn(b'</form>', res.data)
		self.login()
		res = self.client.get(self.url_for('user.reset'))
		self.assertIn(b'</form>', res.data)
		self.assertIn(b'Reset Code', res.data)	
	
	def test_invalid_reset_form(self):
		self.login()
		res = self.client.post(self.url_for('user.reset'),
				data={'origin':'', 'new1':'22', 'new2':'22'}, follow_redirects=True)
		self.assertIn(b'This field is required', res.data)

		res = self.client.post(self.url_for('user.reset'),
				data={'origin':'1', 'new1':'', 'new2':''}, follow_redirects=True)
		self.assertIn(b'This field is required', res.data)

		res = self.client.post(self.url_for('user.reset'),
				data={'origin':'1', 'new1':'22', 'new2':''}, follow_redirects=True)
		self.assertIn(b'This field is required', res.data)

		res = self.client.post(self.url_for('user.reset'),
				data={'origin':'1', 'new1':'22', 'new2':'21'}, follow_redirects=True)
		self.assertIn(b'check your password', res.data)

		res = self.client.post(self.url_for('user.reset'),
				data={'origin':'11', 'new1':'22', 'new2':'22'}, follow_redirects=True)
		self.assertIn(b'Origin password is incorrect!', res.data)

		res = self.client.post(self.url_for('user.reset'),
				data={'origin':'1', 'new1':'1', 'new2':'1'}, follow_redirects=True)
		self.assertIn(b'new password must be different from origin', res.data)

		res = self.client.post(self.url_for('user.reset'),
				data={'origin':'1', 'new1':'22', 'new2':'22'}, follow_redirects=True)
		
		self.assertIn(b'you code has been reseted', res.data)

class TestConfirmMail(BaseSuite):
	def test_confirm_mail(self):
		#login in 1st
		self.prepare_user()
		self.login()
		self.assertFalse(current_user.confirm)
		token = current_user._get_current_object().generate_token()
		confirm_link = self.url_for('user.confirm_mail', token=token, _external=True)

		res = self.client.get(confirm_link, follow_redirects=True)
		self.assertIn(b'You email address has been confirmed', res.data)
		self.assertTrue(current_user.confirm)

		#here visist some email confirmed function