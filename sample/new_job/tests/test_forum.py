
from .suite import BaseSuite
from flask_login import current_user

class TestForumPage(BaseSuite):

	def test_page_without_login(self):
		self.logout()
		res = self.client.get(self.url_for('forum.forum'))
		self.assertIn(b'Sorry, You should', res.data)
		self.assertNotIn(b'</form>', res.data)	
		self.assertNotIn(b'write down your thought', res.data)

		res = self.client.post(self.url_for('forum.forum'),
					data={'title':'testtesttest', 'post':'asdfasasfasfasfasf\
					fdsfdsfdsfdsfdsfsdgfhgf'})
		self.assertNotIn(b'testtesttest', res.data)

		res = self.client.post(self.url_for('forum.forum'),
					data={'title':'testtesttest', 'post':'asdfasasfasfasfasf\
					fdsfdsfdsfdsfdsfsdgfhgf', 'author_id':'10'}, follow_redirects=True)
		self.assertIn(b'Sorry, You should', res.data)

		#??????????

	def test_page_with_login(self):
		self.login()
		res = self.client.get(self.url_for('forum.forum'))
		self.assertIn(b'</form>', res.data)	
		self.assertIn(b'write down your thought', res.data)

		res = self.client.post(self.url_for('forum.forum'),
				data={'title':'shrt', 'post':'this is a test post'}, follow_redirects=True)
		self.assertIn(b'between 5 and 40 characters long', res.data)
		with self.client as c:
			res = self.client.post(self.url_for('forum.forum'),
				data={'title':'proper-length', 'post':'this is a test post'}, 
				follow_redirects=True)
			self.assertIn(b'proper-length', res.data)
			self.assertIn(current_user.name.encode(), res.data)

		res = self.client.post(self.url_for('forum.forum'),
				data={'title':'', 'post':'this is a test post'}, 
				follow_redirects=True)
		self.assertIn(b'This field is required', res.data)

		with self.client as c:
			res = c.post(self.url_for('forum.forum'),
				data={'title':'proper-title', 'post':''}, 
				follow_redirects=True)
			self.assertIn(b'proper-title', res.data)
			self.assertIn(current_user.name.encode(), res.data)
		#test the #32 ?

	def test_article(self):
		
		with self.client as c:
			self.prepare_post()
	
			res = c.get(self.url_for('forum.post', post_id=1))
			self.assertIn(b'this is post 1', res.data)
			self.assertIn(b'</a>', res.data)
			self.assertIn(b'</form>', res.data)		
			self.assertIn(b'your view over this article:', res.data)

			res = self.client.post(self.url_for('forum.post', post_id=1),
					data={'comment':'this is a comment!', 'post_id':1,
						'author_id':current_user.id}, follow_redirects=True)
			self.assertIn(b'this is post 1', res.data)
			self.assertIn(b'this is a comment!', res.data)
			self.assertIn(b'</form>', res.data)		
			self.assertIn(b'your view over this article:', res.data)


			for i in range(10):
				comment = 'Test Comment NO.{}'.format(i+1)
				self.client.post(self.url_for('forum.post', post_id=1),
					data={'comment':comment, 'post_id':1})

		res = self.client.get(self.url_for('forum.post', post_id=1))
		self.assertIn(b'Test Comment NO.1', res.data)
		self.assertNotIn(b'Test Comment NO.10', res.data)

		res = self.client.get(self.url_for('forum.post', post_id=1, page=2))
		self.assertNotIn(b'Test Comment NO.2', res.data)
		self.assertIn(b'Test Comment NO.10', res.data)