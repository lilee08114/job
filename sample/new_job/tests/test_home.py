from .suite import BaseSuite
from urllib import parse

class TestHomePage(BaseSuite):

	def test_home_page(self):
		res = self.client.get(self.url_for('front.home'))
		self.assertIn(b'Welcome to Stoya', res.data)
		self.assertIn(b'</form>', res.data)

	def test_invalid_keyword(self):
		test_keys = ['#1', '@#$', '高级%&', ',,,', '113']
		for key in test_keys:
			url = self.url_for('front.home', key_word=key)
			res = self.client.get(url)
			self.assertIn(b'must be Chinese or English letters', res.data)

		res = self.client.get(self.url_for('front.home', key_word=' '))
		self.assertIn(b'A key word is needed!', res.data)

	def test_new_key(self):
		res = self.client.get(self.url_for('front.home', key_word='totalnew'))
		self.assertIn(b'Sorry! This is a new word', res.data)

	def test_job_list(self):
		#there should be some job with particular keyword already in the database
		pass