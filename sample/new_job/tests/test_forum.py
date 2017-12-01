
from .suite import BaseSuite
from flask_login import current_user

class TestForumPage(BaseSuite):

	def test_page_without_login(self):
		self.logout()
		res = self.client.get(self.url_for('forum.forum'))
		self.assertIn('Sorry, You should', res.data)
		self.assertNotIn('</form>', res.data)

		res = self.client.post(self.url_for('forum.forum'),
					data={'title':'testtesttest', 'post':'asdfasasfasfasfasf\
					fdsfdsfdsfdsfdsfsdgfhgf', 'author_id':'10'})
		?????????????statuscode=401

		res = self.client.post(self.url_for('forum.forum'),
					data={'title':'testtesttest', 'post':'asdfasasfasfasfasf\
					fdsfdsfdsfdsfdsfsdgfhgf', 'author_id':'10'}, follow_redirects=True)
		self.assertIn('<form>', res.data)
		#??????????

	def test_page_with_login(self):
		self.login()
		res = self.client.get(self.url_for('forum.forum'))
		self.assertIn('</form>', res.data)	
		self.assertIn('write down your thought', res.data)

		res = self.client.post(self.url_for('forum.forum'),
				data={'title':'short', 'post':'this is a test post, \
				length is enough'}, follow_redirects=True)
		self.assertIn('title too short', res.data)？？？？？？？？

		res = self.client.post(self.url_for('forum.forum'),
				data={'title':'proper-length', 'post':'this is a test post, \
				length is enough'}, follow_redirects=True)
		self.assertIn('Sorry, You should', res.data)

