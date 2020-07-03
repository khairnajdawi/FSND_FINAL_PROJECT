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
    # db.create_all()


'''
Actors
Have name and is_available state 
to check if this actor can be assigned to a movie
also age and gender
'''


class Actors(db.Model):
    __tablename__ = 'Actors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String,nullable=False)
    is_available = db.Column(db.Boolean,nullable=False,default=True,server_default='True')
    age = db.Column(db.Integer,nullable=False)
    gender =db.Column(db.String,nullable=False)

    def __init__(self, name, age, gender, is_available=True):
        self.name = name
        self.is_available = is_available
        self.age = age
        self.gender = gender

    def format(self):
        return {
          'id': self.id,
          'name': self.name,
          'is_available': self.is_available,
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
    Adveture = 'Adventure'
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
Movie Casting Status
'''

class MovieStatus(enum.Enum):
    Recruting = 'Recruting'
    Filming = 'Filming'
    Directing = 'Directing'
    Review = 'Review'
    ReadyToPublish = 'Ready To Publish'
    Published = 'Published'


'''
Movie Class
'''


class Movies(db.Model):
    __tablename__ = 'Movies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(String,nullable=False)
    movie_status = db.Column(db.Enum(MovieStatus),nullable=False)
    movie_category = db.Column(db.Enum(MoviesCategory),nullable=False)
    movie_rating = db.Column(db.Enum(MoviesRating),nullable=False)
    actors = db.relationship('Actors',secondary="MovieActors",backref=db.backref('movies',lazy=True))


'''
Movie Actor Relation
'''

MovieActors = db.Table(
    'MovieActors',
    db.Column('movie_id',db.Integer,db.ForeignKey('Movies.id'),primary_key=True),
    db.Column('actor_id',db.Integer,db.ForeignKey('Actors.id'),primary_key=True)
)