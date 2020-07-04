import os
from flask import Flask,render_template, request, Response, flash, redirect, url_for,jsonify,abort
from flask_cors import CORS
from models import db,setup_db,Actors,Movies
from flask_moment import Moment
from flask_wtf import FlaskForm
from forms import *
import logging

def create_app():

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
    

    @app.route('/actors/add')
    def add_actor_form():
        form = AddActorForm()
        return render_template('pages/actors/add.html',form=form)


    @app.route('/actors/add', methods=["POST"])
    def add_actor():
        form = AddActorForm(request.form)
        added=False
        try:
            new_actor = Actors(
                name=form.name.data,
                age = form.age.data,
                gender = form.gender.data,
                is_available = form.is_available.data=="True"
            )
            db.session.add(new_actor)
            db.session.commit()
            added=True
        except:
            db.session.rollback()
        finally:
            db.session.close()

        if(added):
            flash('New Actor added successfully','success')
            return redirect(url_for('actors'))
        else:
            flash('Could not add new Actor','danger')
            return render_template('pages/actors/add.html',form=form)


    @app.route('/actors/<int:actor_id>/edit')
    def edit_actor_form(actor_id):   
        # check if requested actor id does exist
        actor = Actors.query.get(actor_id)     
        if(actor==None):
            # if not exist, return to actors list and flash an error
            flash('Requested Actor could not be found !!','danger')
            return redirect(url_for('actors'))
        # if exist, prepare form with actor info
        form = AddActorForm()
        form.name.data = actor.name
        form.age.data = actor.age
        form.gender.data = actor.gender
        form.is_available.data = "True" if actor.is_available else "False"
        return render_template('pages/actors/edit.html',form=form)


    @app.route('/actors/<int:actor_id>/edit',methods=['POST'])
    def edit_actor(actor_id):           
        form = AddActorForm(request.form)
        updated=False
        try:
            actor = Actors.query.get(actor_id)            
            actor.name=form.name.data,
            actor.age = form.age.data,
            actor.gender = form.gender.data,
            actor.is_available = form.is_available.data=="True"            
            db.session.commit()
            updated=True
        except:
            db.session.rollback()
        finally:
            db.session.close()

        if(updated):
            flash('Actor\'s info updated successfully','success')
            return redirect(url_for('actors'))
        else:
            flash('Could not update Actor\'s info','danger')
            return render_template('pages/actors/edit.html',form=form)


    @app.route('/actors/<int:actor_id>/delete')
    def delete_actor_form(actor_id):   
        # check if requested actor id does exist
        actor = Actors.query.get(actor_id)     
        if(actor==None):
            # if not exist, return to actors list and flash an error
            flash('Requested Actor could not be found !!','danger')
            return redirect(url_for('actors'))
        # if exist, prepare form with actor info
        return render_template('pages/actors/delete.html',actor=actor)


    @app.route('/movies')
    def movies():
        movies = Movies.query.all()
        return render_template('pages/movies/list.html',movies=movies)

    return app

app = create_app()

if __name__ == '__main__':
    app.run()