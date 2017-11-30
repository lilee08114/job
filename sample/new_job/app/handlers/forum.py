import re
from app.model import Post, Comment
from flask import Blueprint, render_template, redirect, url_for, request, abort, current_app
from flask_login import current_user, login_required
import bleach
from app.forms.forum import Send_post, Send_comment

bp = Blueprint('forum', __name__)

@bp.route('/', methods=['GET','POST'])
@bp.route('/<int:page>/', methods=['GET','POST'])
def forum(page=1):
	form = Send_post()
	paginate = Post.query.order_by(Post.post_time).paginate(page=page, per_page=10)
	posts = paginate.items
	if form.validate_on_submit():
		post = form.text.data
		new_post = Post(title=form.title.data,
						post=int_to_link(post),
						author_id=current_user.id)
		new_post._save()
		

	return render_template('forum.html', posts=posts, 
							current_page=page, form=form, 
							has_prev=paginate.has_prev,
							has_next=paginate.has_next)

def int_to_link(post):
	'''transfer the job_id number in articles into link, make the job is easier to quote
	post:type:string, articles posted by users
	return article string in which job_id number was transferred into link
	'''
	post = bleach.clean(post, tags=['a'])
	for num in re.findall('#\d+', post):	
		num_int = num[1:]
		new_num = '<a href=%s>#%s</a>'%(url_for('front.detail', job_id=num_int), num_int)
		post = post.replace(num, new_num, 1)
	return post


@bp.route('/post/<int:post_id>/', methods=['GET', 'POST'])
@login_required
def post(post_id):
	form = Send_comment()
	post = Post.query.get_or_404(post_id)
	page = request.args.get('page', 1, type=int)
	if form.validate_on_submit():
		new_comment = Comment(comment=form.comment.data,
							author_id = current_user.id,
							post_id=post_id)
		new_comment._save()
		return redirect(url_for('.post', post_id=post_id))
	paginate = Comment.query.filter_by(post_id=post_id).\
					order_by(Comment.comment_time).paginate(page=page, per_page=10)
	return render_template('post_detail.html', post=post, form=form,
							comments=paginate.items, paginate=paginate)