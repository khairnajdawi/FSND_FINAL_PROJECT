from sqlalchemy import Column, String, create_engine
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import json
import os
import enum

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
Actors
Have name and is_available state
to check if this actor can be assigned to a movie
also age and gender
'''


class Actors(db.Model):
    __tablename__ = 'Actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
          'id': self.id,
          'name': self.name,
          'age': self.age,
          'gender': self.gender
          }

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

'''
Movie Class
'''


class Movies(db.Model):
    __tablename__ = 'Movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(String, nullable=False)
    release_date = db.Column(db.Date, nullable=False)
    movie_category = db.Column(db.Enum(MoviesCategory), nullable=False)
    movie_rating = db.Column(db.Enum(MoviesRating), nullable=False)
    actors = db.relationship(
        'Actors',
        secondary="MovieActors",
        backref=db.backref('movies', lazy=True)
        )

    def __init__(self, title, release_date, movie_category, movie_rating):
        self.title = title
        self.release_date = release_date
        self.movie_category = movie_category
        self.movie_rating = movie_rating

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
          'id': self.id,
          'title': self.title,
          'release_date': self.release_date,
          'movie_category': self.movie_category.value,
          'movie_rating': self.movie_rating.value
          }

'''
Movie Actor Relation
'''

MovieActors = db.Table(
    'MovieActors',
    db.Column(
        'movie_id',
        db.Integer,
        db.ForeignKey('Movies.id'),
        primary_key=True
        ),
    db.Column(
        'actor_id',
        db.Integer,
        db.ForeignKey('Actors.id'),
        primary_key=True
    )
)
