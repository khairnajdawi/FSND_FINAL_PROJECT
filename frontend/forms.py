from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,TextAreaField,TimeField,IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, AnyOf, URL
from wtforms.fields import html5 as h5fields
from wtforms.widgets import html5 as h5widgets
from wtforms.fields.html5 import DateField

import enum


'''
Movies Category Enum
'''


class MoviesCategory(enum.Enum):
    Comedy = 'Comedy'
    Action = 'Action'
    Drama = 'Drama'
    Romance = 'Romance'
    Animation = 'Animation'
    History = 'History'
    Crime = 'Crime'
    SciFi = 'SciFi'
    Horror = 'Horror'
    Family = 'Family'
    Adventure = 'Adventure'
    Musical = 'Musical'
    Documentary = 'Documentary'

'''
Movies Rating Enum
'''


class MoviesRating(enum.Enum):
    G = 'G'
    PG = 'PG'
    PG13 = 'PG-13'
    R = 'R'

class AddActorForm(FlaskForm):
    name = StringField(
        'name',
        validators=[DataRequired()]
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

class MovieForm(FlaskForm):
    title = StringField(
        'title',
        validators=[DataRequired()]
    )
    movie_rating = SelectField(
        'movie_rating',
        validators=[DataRequired()]
    )
    movie_category = SelectField(
        'movie_category',
        validators=[DataRequired()]
    )
    release_date = DateField(
        'release_date',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )
        
    def __init__(self, *args, **kwargs): 
        super(MovieForm, self).__init__(*args, **kwargs)
        self.movie_rating.choices = [(name, member.value) for name,member in MoviesRating.__members__.items()]
        self.movie_category.choices = [(name, member.value) for name,member in MoviesCategory.__members__.items()]


class MovieActorsForm(FlaskForm):
    actor = SelectField(
        'actor',
        validators=[DataRequired()]
    )