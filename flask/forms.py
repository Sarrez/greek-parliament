from flask_wtf import FlaskForm
from wtforms import TextAreaField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class SearchForm(FlaskForm):
    query = StringField('Search something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Search')