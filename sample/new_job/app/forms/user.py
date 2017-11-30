from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError


class LoginForm(FlaskForm):

	name = StringField('Name', validators=[DataRequired(), Length(3,64)])
	password = PasswordField('PassWD', validators=[DataRequired()])
	submit = SubmitField('Submit')

class Regis(FlaskForm):

	name = StringField('Name', validators=[DataRequired(), Length(3,64)])
	mail = StringField('Email', validators=[Email(), DataRequired()])
	passwd1 = PasswordField('Password', validators=[DataRequired()])
	passwd2 = PasswordField('confirm password', 
				validators=[DataRequired(), EqualTo('passwd1', message='password must match')])
	submit = SubmitField('Submit')

	def validate_name(self, field):
		if User.query.filter_by(name=field.data).first():
			raise ValidationError('name already exsits!')

	def validate_mail(self, field):
		if User.query.filter_by(mail=field.data).first():
			raise ValidationError('Email has been registered!')

class Reset(FlaskForm):

	origin = PasswordField('origin password', validators=[DataRequired()])
	new1 = PasswordField('new password', validators=[DataRequired()])
	new2 = PasswordField('confirm password', 
			validators=[DataRequired(), EqualTo('new1', message='check your password')])
	submit = SubmitField('Submit')

	def validate_origin(self, field):
		if current_user.verify_passwd(field.data):
			raise ValidationError('Origin password is incorrect!')