import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import InputRequired, Length

class SearchForm(FlaskForm):

	key = StringField('', validators=[InputRequired(), Length(4,64)])
	submit = SubmitField('GO!')

	def validate_key(self, field):
		if not re.search('^[a-zA-Z\u4e00-\u9fa5]+$', field.data):
			raise ValidationError('must be Chinese or English letters only')