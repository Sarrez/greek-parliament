from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, Length

class SearchForm(FlaskForm):
    query = StringField(' ', validators=[DataRequired(), Length(min=1, max=30)])
    submit = SubmitField('Search')