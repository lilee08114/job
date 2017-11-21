from flask import Blueprint, render_template, Flask, request
from flask import redirect, url_for, flash, abort
from flask_login import login_user, current_user, logout_user, login_required
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from ..model import db, Jobbrief, Jobdetail, Company, Jobsite, User
from ..forms.user import LoginForm, Regis, Reset
from ..utils.send_mail import send_mail

bp = Blueprint('user', __name__)


@bp.route('/')
def user():
	form = LoginForm()
	return render_template('user.html', form=form, reg=1)


@bp.route('/login/', methods=['GET','POST'])
def login():
	form = LoginForm()
	if request.method == 'POST':
		user_name = request.form.get('name')
		passwd = request.form.get('password')
		user = User.query.filter_by(name=user_name).first()
		if user and user.verify_passwd(passwd):
			login_user(user)
			return redirect(request.args.get('next') or url_for('.user') )
		else:
			flash('Incorrect name or password!')
			return redirect(request.args.get('next') or url_for('.user'))
	return render_template('user.html', form=form, reg=1)


@bp.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(request.args.get('next') or url_for('front.home'))


@bp.route('/register/', methods=['GET', 'POST'])
def regis():
	form = Regis()
	if form.validate_on_submit():
		new_user = User(name=form.name.data, password=form.passwd2.data,
						mail=form.mail.data)
		db.session.add(new_user)
		try:
			db.session.commit()
			send_mail(new_user.mail, new_user.generate_token(), new_user.name)
			flash ('congrats, registraion succeed! A confirm letter \
				has been sent to your email, plz check out')
			return redirect(request.args.get('next') or url_for('.user'))
		except:
			print ('in except!!!!')
			db.session.rollback()
			abort(404)
	print ('run here')
	return render_template('user.html', form=form, reg=2)


@bp.route('/reset_code/')
@login_required
def reset():
	form = Reset()
	if form.validate_on_submit():
		user = current_user._get_current_object()
		user.password = form.new2.data
		db.session.add(user)
		try:
			db.session.commit()
			flash ('you code has been reseted')
			return render_template(request.args.get('next') or url_for('.user'))
		except:
			db.session.rollback()
			raise
	return render_template('user.html', form=form, reg=3)


@bp.route('/confirm/<token>')
@login_required
def confirm_mail(token):
	dic = current_user.decode_token(token)
	if current_user.id == dic.get('id'):
		user = current_user._get_current_object()
		user.confirm = True 
		db.session.add(user)
		db.session.commit()
		flash('You email address has been confirmed!')
		return redirect(request.args.get('next') or url_for('.user'))
	else:
		abort(404)


