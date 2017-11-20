from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..model import Jobbrief, Jobdetail, Company, Jobsite, User

class Send_post(FlaskForm):

	title = StringField('title', validators=[DataRequired(), Length(min=10, max=50)])
	text = TextAreaField('write down your thought')
	submit = SubmitField('submit')

class Send_comment(FlaskForm):

	comment = TextAreaField('your view over this article:', 
							validators=[DataRequired(), Length(10,200)])
	submit = SubmitField('Submit')