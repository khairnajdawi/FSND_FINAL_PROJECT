import os
from flask import Flask, request, Response, jsonify, abort
from flask_cors import CORS
from backend.models import db, setup_db, Actors, Movies
import logging
from backend.auth.auth import AuthError, requires_auth


def create_app():
    #
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true'
            )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,POST,DELETE,PATCH,INFO'
            )
        return response

    # Endpoints

    '''
    Get /actors
        requires get:actors permission
        returns success boolean and an array of actors
        or appropriate status code indicating reason for failure
    '''

    @app.route('/actors')
    @requires_auth('get:actors')
    def actors(payload):
        actors_list = Actors.query.all()
        actors_formatted = [actor.format() for actor in actors_list]
        return jsonify({
            'success': True,
            'actors': actors_formatted
        })

    '''
    POST /actors
        creates a new actor
        requires create:actor permission
        paramter : a json object containts actor's attribue :
                  string name, int age, string gender, and boolean is_available
        returns success boolean and new actor's id
        or appropriate status code indicating reason for failure
    '''

    @app.route('/actors', methods=['POST'])
    @requires_auth('create:actor')
    def add_actor(payload):
        # read form data from post request
        body = request.get_json()
        if(not body):
            abort(400)
        # read post data
        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        # check if all required data is available,
        # if so, then add the actor
        added = False
        new_actor_id = 0
        if(name and age and gender):
            # create Actor instance using form data
            new_actor = Actors(
                name=name,
                age=age,
                gender=gender
                )
            # add new actor to db
            added = False
            try:
                new_actor.insert()
                new_actor_id = new_actor.id
                added = True
            except:
                db.session.rollback()
            finally:
                db.session.close()
        else:
            # in case one or more of required fields are missing,
            # return 422  error
            abort(422)
        # return json response for success
        return jsonify(
            {
                'success': added,
                'inserted': new_actor_id,
            }
        )

    '''
    GET /actors/<int : actor_id>
        get actor's info
        requires get:actor-info permission
        paramter : no parameter
        returns success boolean and actor's info whose Id = actor_id
        or appropriate status code indicating reason for failure
    '''

    @app.route('/actors/<int:actor_id>', methods=['GET'])
    @requires_auth('get:actor-info')
    def get_actor_info(payload, actor_id):
        # get list of actor identified by actor_id
        actor = Actors.query.get(actor_id)
        # if actor does not exist, return 404 code
        if(not actor):
            abort(404)
        # if exist, return json object with success and actor's info
        return jsonify(
            {
                'success': True,
                'info': actor.format(),
            }
        )

    '''
    DELETE /actors/<int : actor_id>
        deletes an actor
        requires delete:actor permission
        paramter : no parameter
        returns success boolean and the Id of the deleted actor
        or appropriate status code indicating reason for failure
    '''

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    @requires_auth('delete:actor')
    def delete_actor(payload, actor_id):
        # check if actor exist by querying Actors by the actor_id
        actor = Actors.query.get(actor_id)
        deleted = False
        if(actor):
            # if actor exist, try delete
            try:
                actor.delete()
                deleted = True
            except:
                db.session.rollback()
            finally:
                db.session.close()
        else:
            # if actor not exist, return 404 code
            abort(404)
        # return json response for success, with the deleted actor's id
        return jsonify(
            {
                'success': deleted,
                'deleted': actor_id,
            }
        )

    '''
    PATCH /actors/<int : actor_id>
        modify an actor's info
        requires edit:actor permission
        paramter : no parameter
        returns success boolean and the Id of the edited actor
        or appropriate status code indicating reason for failure
    '''

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    @requires_auth('edit:actor')
    def update_actor(payload, actor_id):
        actor_to_update = Actors.query.get(actor_id)
        # check if actor exist, if not return 404 code
        if(not actor_to_update):
            abort(404)
        # read form data from post request
        body = request.get_json()
        # check if data not provided, then return 422 code
        if(not body):
            abort(422)
        # read post data
        name = body.get('name', None)
        age = body.get('age', None)
        gender = body.get('gender', None)
        # check for each attribute if provided
        # updated provided info
        updated = False
        if(name):
            actor_to_update.name = name
        if(age):
            actor_to_update.age = age
        if(gender):
            actor_to_update.gender = gender
        try:
            actor_to_update.update()
            updated = True
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
        # return json response for success with the updated actor's id
        return jsonify(
            {
                'success': updated,
                'updated': actor_id,
            }
        )

    '''
    GET /actors/<actor_id>/movies
        get a list of all actor's movies
        requires get:actor-movies permission
        paramter : no parameter
        returns success boolean and a list of all movies
        or appropriate status code indicating reason for failure
    '''

    @app.route('/actors/<actor_id>/movies')
    @requires_auth('get:actor-movies')
    def get_actor_movies(payload, actor_id):
        actor = Actors.query.get(actor_id)
        # check if actor exist, if not return 404 code
        if(not actor):
            abort(404)
        # prepare a list of movies for that actor
        movies = [movie.format() for movie in actor.movies]
        # return json response with success and movie's list
        return jsonify({
            'success': True,
            'movies': movies
        })

    '''
    GET /movies
        get a list of all movies
        requires get:movies permission
        paramter : no parameter
        returns success boolean and a list of all movies
        or appropriate status code indicating reason for failure
    '''

    @app.route('/movies')
    @requires_auth('get:movies')
    def get_movies(payload):
        # get all movies list
        movies = Movies.query.all()
        # prepare as formatted objects, to jsonify
        movies_formatted = [movie.format() for movie in movies]
        # return json reponse with success and movies list
        return jsonify({
            'success': True,
            'movies': movies_formatted
        })

    '''
    GET /movies/<int:movie_id>
        get a movie's info
        requires get:movie-info permission
        paramter : no parameter
        returns success boolean and movie's info
        or appropriate status code indicating reason for failure
    '''

    @app.route('/movies/<int:movie_id>')
    @requires_auth('get:movie-info')
    def get_movie_info(payload, movie_id):
        # query Movies to get movie identified by movie_id
        movie = Movies.query.get(movie_id)
        # if movie not exist, return 404 code
        if(not movie):
            abort(404)
        # return json reponse with success and movie's info
        return jsonify({
            'success': True,
            'movie': movie.format()
        })

    '''
    POST /movies
        creates a new movie
        requires create:movie permission
        paramter : a json object contains the info of the movie
        returns success boolean and the new movie's id
        or appropriate status code indicating reason for failure
    '''

    @app.route('/movies', methods=['POST'])
    @requires_auth('create:movie')
    def create_movie(payload):
        # get request paramtetes
        body = request.get_json()
        # if not provided, return 400 code
        if(not body):
            abort(400)
        # read parameters
        title = body.get('title', None)
        release_date = body.get('release_date', None)
        movie_category = body.get('movie_category', None)
        movie_rating = body.get('movie_rating', None)
        created = False
        new_movie_id = 0
        # check all required attribute is provided
        if(title and release_date and movie_category and movie_rating):
            try:
                # prepare new movie object from provided data and insert to db
                new_movie = Movies(
                    title=title,
                    release_date=release_date,
                    movie_rating=movie_rating,
                    movie_category=movie_category
                )
                new_movie.insert()
                created = True
                new_movie_id = new_movie.id
            except:
                db.session.rollback()
            finally:
                db.session.close()
        else:
            # if not all required attributes provided, return 422 code
            abort(422)
        # return json reponse with success and new movie's id
        return jsonify({
            'success': created,
            'new_movie_id': new_movie_id
        })

    '''
    PATCH /movies/<int:movie_id>
        get a movie's info
        requires edit:movie permission
        paramter : a json object of the new info to be updated
        returns success boolean and the id of the movie just updated
        or appropriate status code indicating reason for failure
    '''

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    @requires_auth('edit:movie')
    def update_movie(payload, movie_id):
        # get the movie to be updated
        movie_to_update = Movies.query.get(movie_id)
        # if movie not exist, return 404
        if(not movie_to_update):
            abort(404)
        # read request data
        body = request.get_json()
        # if data not provided, return 400
        if(not body):
            abort(400)
        # read data and update availabe attributes
        title = body.get('title', None)
        release_date = body.get('release_date', None)
        movie_category = body.get('movie_category', None)
        movie_rating = body.get('movie_rating', None)
        updated = False
        if(title):
            movie_to_update.title = title
        if(release_date):
            movie_to_update.release_date = release_date
        if(movie_category):
            movie_to_update.movie_category = movie_category
        if(movie_rating):
            movie_to_update.movie_rating = movie_rating
        # try saving changes
        try:
            movie_to_update.update()
            updated = True
        except:
            db.session.rollback()
        finally:
            db.session.close()
        # return json with success result and the movie's id just updated
        return jsonify({
            'success': updated,
            'updated': movie_id
        })

    '''
    GET /movies/<int:movie_id>/actors
        get a list of all movie's actors
        requires get:movie-actors permission
        paramter : no parameter
        returns success boolean and a list of all movie's actor
        or appropriate status code indicating reason for failure
    '''

    @app.route('/movies/<int:movie_id>/actors')
    @requires_auth('get:movie-actors')
    def get_movie_actors(payload, movie_id):
        # get the movie to read actors list
        movie = Movies.query.get(movie_id)
        # if movie not available, return 404 code
        if(not movie):
            abort(404)
        # prepare a list of all movie's actors
        actors = [actor.format() for actor in movie.actors]
        # return json response with successs and actors list
        return jsonify({
            'success': True,
            'actors': actors
        })

    '''
    POST /movies/<int:movie_id>/actors
        add an actor to a movie's actors list
        requires add:movie-actor permission
        paramter : the id of the actor to be added
        returns success boolean and the id of the movie and the actor
        or appropriate status code indicating reason for failure
    '''

    @app.route('/movies/<int:movie_id>/actors', methods=['POST'])
    @requires_auth('add:movie-actor')
    def add_movie_actors(payload, movie_id):
        # get the movie to add actors for
        movie = Movies.query.get(movie_id)
        # if movie not exist, return 404 code
        if(not movie):
            abort(404)
        # read request
        body = request.get_json()
        # if request not available, return 400 code
        if(not body):
            abort(400)
        # get the actor's id from request
        actor_id = body.get("actor_id", 0)
        # get the actor identified by actor_id
        actor = Actors.query.get(actor_id)
        # if actor not exist, return 402 code
        if(not actor):
            abort(422)
        added = False
        # try to add actor to movie's actors list
        try:
            movie.actors.append(actor)
            db.session.commit()
            added = True
        except:
            db.session.rollback()
        finally:
            db.session.close()
        # return json response with success result, movie's id and actor's id
        return jsonify({
            'success': added,
            'movie': movie_id,
            'actor': actor_id
        })

    '''
    DELETE /movies/<int:movie_id>/actors
        remove an actor to a movie's actors list
        requires delete:movie-actor permission
        paramter : the id of the actor to be removed
        returns success boolean and the id of the movie and the actor
        or appropriate status code indicating reason for failure
    '''

    @app.route('/movies/<int:movie_id>/actors', methods=['DELETE'])
    @requires_auth('delete:movie-actor')
    def delete_movie_actors(payload, movie_id):
        # get the movie to delete actor from
        movie = Movies.query.get(movie_id)
        # if movie not exist, return 404 code
        if(not movie):
            abort(404)
        # read request
        body = request.get_json()
        # if request not available, return 400 code
        if(not body):
            abort(400)
        # get the actor's id from request
        actor_id = body.get("actor_id", 0)
        # get the actor identified by actor_id
        actor = Actors.query.get(actor_id)
        # if actor not exist, return 402 code
        if(not actor):
            abort(422)
        # try to delete actor to movie's actors list
        deleted = False
        try:
            movie.actors.remove(actor)
            db.session.commit()
            deleted = True
        except:
            db.session.rollback()
        finally:
            db.session.close()
        # return json response with success result, movie's id and actor's id
        return jsonify({
            'success': deleted,
            'movie': movie_id,
            'deleted': actor_id
        })

    '''
    DELETE /movies/<int:movie_id>
        delete a movie
        requires delete:movie permission
        paramter : no parameter
        returns success boolean and the id of the movie just deleted
        or appropriate status code indicating reason for failure
    '''

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    @requires_auth('delete:movie')
    def delete_movie(payload, movie_id):
        # get the movie to be deleted
        movie_to_delete = Movies.query.get(movie_id)
        # if the movie not exist, return 404
        if(not movie_to_delete):
            abort(404)
        deleted = False
        # try to delete the movie
        try:
            movie_to_delete.delete()
            deleted = True
        except:
            db.session.rollback()
        finally:
            db.session.close()

        # return json response with success result and movie's id just deleted
        return jsonify({
            'success': deleted,
            'deleted': movie_id
        })

    # Errors Handlers

    '''
    Create error handlers for all expected errors
    '''

    # error handler for 404 (Not Found)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    # error handler for 422 (unprocessable)
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    # error handler for 400 (bad request)
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    # error handler for 405 (method not allowed)
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    # error handler for 500
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    # error handling for AuthError
    @app.errorhandler(AuthError)
    def auth_error_handler(auth_error):
        status_code = auth_error.status_code
        message = auth_error.error
        return jsonify({
            "success": False,
            "error": status_code,
            "message": message
            }), status_code

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host="localhost", port=5000)
