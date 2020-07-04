from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,  DateTimeField,TextAreaField,TimeField,IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, AnyOf, URL
from models import MoviesCategory,MoviesRating,MovieStatus
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets


class AddActorForm(FlaskForm):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    is_available = SelectField(
        'is_available',
        validators=[DataRequired()],
        choices=[('True','Yes'),('False','No')]
    )
    age = h5fields.IntegerField(
        'age',
        widget=h5widgets.NumberInput(min=1, max=100, step=1),
        validators=[DataRequired()],
    )
    gender = SelectField(
        'gender',
        validators=[DataRequired()],
        choices=[('Male','Male'),('Female','Female')]
    )