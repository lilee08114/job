from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, PasswordField, TextField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..model import Jobbrief, Jobdetail, Company, Jobsite, User, Subscribe

class SubSearch(FlaskForm):

	key = StringField('', validators=[DataRequired(), Length(1, 40)])
	submit = SubmitField('Search Now')

	def validate_key(self, field):
		obj = Jobbrief.query.filter_by(key_word=field.data).order_by(Jobbrief.job_time.desc()).first()
		if obj is not None:
			if datetime.now()-obj.job_time < timedelta(hours=7):
				raise ValidationError('this key is already in our database, you can \
					check it throgh the homepage or refresh it below this page')

class SubSub(FlaskForm):

	subkey = StringField('', validators=[DataRequired(), Length(1, 40)])
	#这里应该还有时间选项， 1为3天，2为7天
	time_limit = SelectField('days', choices=[(3,'3days'), (7,'7days')], coerce=int)
	submit = SubmitField('Subscribe')
	
	def validate_subkey(self, field):
		s = Subscribe.query.filter_by(sub_key=field.data).order_by(Subscribe.sub_start).first()
		if s is not None and (datetime.now()-s.sub_start < timedelta(hours=5)):
			raise ValidationError('Sorry, this word just has been searching recently,\
				check it throgh the home page')
	