
from .suite import BaseSuite
from flask_login import current_user

class TestForumPage(BaseSuite):

	def test_page_without_login(self):
		self.logout()
		res = self.client.get(self.url_for('forum.forum'))
		self.assertIn('Sorry, You should', res.data)
		self.assertNotIn('</form>', res.data)	
		self.assertNotIn('write down your thought', res.data)

		res = self.client.post(self.url_for('forum.forum'),
					data={'title':'testtesttest', 'post':'asdfasasfasfasfasf\
					fdsfdsfdsfdsfdsfsdgfhgf', 'author_id':'10'})
		self.assertEqual(res.status_code, 401)

		res = self.client.post(self.url_for('forum.forum'),
					data={'title':'testtesttest', 'post':'asdfasasfasfasfasf\
					fdsfdsfdsfdsfdsfsdgfhgf', 'author_id':'10'}, follow_redirects=True)
		self.assertIn('<form>', res.data)
		self.assertIn('Login', res.data)
		#??????????

	def test_page_with_login(self):
		self.login()
		res = self.client.get(self.url_for('forum.forum'))
		self.assertIn('</form>', res.data)	
		self.assertIn('write down your thought', res.data)

		res = self.client.post(self.url_for('forum.forum'),
				data={'title':'shrt', 'post':'this is a test post'}, follow_redirects=True)
		self.assertIn('between 5 and 40 characters long', res.data)

		res = self.client.post(self.url_for('forum.forum'),
				data={'title':'proper-length', 'post':'this is a test post'}, 
				follow_redirects=True)
		self.assertIn('proper-length', res.data)
		self.assertIn(current_user.name, res.data)

		res = self.client.post(self.url_for('forum.forum'),
				data={'title':'', 'post':'this is a test post'}, 
				follow_redirects=True)
		self.assertIn('This field is required', res.data)

		res = self.client.post(self.url_for('forum.forum'),
				data={'title':'proper-title', 'post':''}, 
				follow_redirects=True)
		self.assertIn('proper-title', res.data)
		self.assertIn(current_user.name, res.data)
		#test the #32 ?

	def test_article(slef):
		self.prepare_post()
		self.login()
		res = self.client.get(self.url_for('forum.post', post_id=1))
		self.assertIn('this is post 1', res.data)
		self.assertIn('</a>', res.data)
		self.assertIn('</form>', res.data)		
		self.assertIn('your view over this article:', res.data)

		res = self.client.post(self.url_for('forum.post', post_id=1),
					data={'comment':'this is a comment!', 'post_id':1,
						'author_id':current_user.id}, follow_redirects=True)
		self.assertIn('this is post 1', res.data)
		self.assertIn('this is a comment!', res.data)
		self.assertIn('</form>', res.data)		
		self.assertIn('your view over this article:', res.data)


		for i in range(10):
			comment = 'Test Comment NO.{}'.format(i+1)
			self.client.post(self.url_for('forum.post', post_id=1),
					data={'comment':comment, 'post_id':1,
						'author_id':current_user.id})

		res = self.client.get(self.url_for('forum.post', post_id=1))
		self.assertIn('Test Comment NO.1', res.data)
		self.assertNotIn('Test Comment NO.10', res.data)

		res = self.client.get(self.url_for('forum.post', post_id=1, page=2))
		self.assertNotIn('Test Comment NO.1', res.data)
		self.assertIn('Test Comment NO.10', res.data)