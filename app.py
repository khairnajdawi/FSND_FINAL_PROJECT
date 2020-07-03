import os
from flask import Flask,render_template, request, Response, flash, redirect, url_for,jsonify,abort
from flask_cors import CORS
from models import db,setup_db,Actors,Movies
from flask_moment import Moment
from flask_wtf import FlaskForm
from forms import *
import logging

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def index():
        return render_template('pages/home.html')

    @app.route('/actors')
    def actors():
        actors = Actors.query.all()
        return render_template('pages/actors/list.html',actors=actors)
    
    @app.route('/movies')
    def movies():
        movies = Movies.query.all()
        return render_template('pages/actors/list.html',movies=movies)

    return app

app = create_app()

if __name__ == '__main__':
    app.run()