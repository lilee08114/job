from suite import BaseSuite


class TestSignup(BaseSuite):

	def test_signup_page(self):
		res = self.client.get(self.url_for('user.regis'))
		self.assertIn('<form>', res.data)

	def test_name_require(self):
		#?????????
		res = self.client.post(self.url_for('user.regis'))
		self.assertIn('required', res.data)

	#here need more tests to test no passwd and email

	def test_invalid_name(self):
		res = self.client.post(self.url_for('user.regis'), 
					data={'name':'n', 'mail':'test@email.com',
							'passwd1':'1','passwd2':'1'})
		self.assertIn(??????)

	#here need more tests to test invalid passwd, and email

	