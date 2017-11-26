import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request
from flask import redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from celery import group, chain
from ..crawler.store import fetch_Store
from ..forms.sub import SubSearch, SubSub
from ..model import db, Jobbrief, Jobdetail, Company, Jobsite, User, Subscribe
from ..decorator import check_confirm_state
from crawler.store import Crawler


bp = Blueprint('subscribe', __name__)

#需要登陆
@bp.route('/', methods=['GET','POST'])
#@check_confirm_state
@login_required
def subscribe():
	form_search = SubSearch()
	form_sub = SubSub()
	if form_search.validate_on_submit():
		key_word = form_search.key.data
		ins = Crawler(key_word)
		ins.Start()
		#这里也不能直接传输实例，因为不能序列化，所以传输类本身，这样才能序列话，将实例作为参数传输
		#ins = fetch_Store(key)					
		#instance.workStart()

		flash('is searching the internet, please wait...')
		return redirect(request.args.get('next') or url_for('.subscribe')) 

	if form_sub.validate_on_submit():
		#应该增加一个订阅列表，包含订阅人，订阅相关时间，以及相应的结果！	
		#由客户端输入时间限制，有3天，7天选项，如果后面有其他的调整，可以在这调整
		key_word = form_sub.subkey.data
		ins = Crawler(key_word)
		ins.Start(subscribe=True)


		#在开始时写订阅相关信息入数据库，此时还缺少结束数据
		new_sub = Subscribe(sub_key=key_word, subscriber_id=current_user.id)
		new_sub._save()
		flash('we will keep searching the relative job')
		
		return redirect(request.args.get('next') or url_for('.subscribe')) 

	return render_template('subscribe.html', form_search=form_search, form_sub=form_sub)

def period_format(days):
	now = datetime.now()
	countdown = 5*60*60
	period_list = []
	if days==3:
		#------------------------
		start = now + timedelta(seconds=countdown)
		end = now + timedelta(days=3)
		while start<end:
			period_list.append(countdown)
			start += timedelta(seconds=countdown)
		print (period_list)
		return period_list
		#------------------------

	elif days==7:
		start = now + timedelta(seconds=countdown)
		end = now + timedelta(days=7)
		while start<end:
			period_list.append(countdown)
			start += timedelta(seconds=countdown)
		print (period_list)
		return period_list

	else:
		return period_list