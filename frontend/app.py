"""Python Flask WebApp Auth0 integration example
"""
from functools import wraps
import json
import os
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask, request
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import flash
from flask import abort
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import http.client
from auth import AuthError, requires_auth, check_has_permission
from forms import AddActorForm,MovieForm,MovieActorsForm
import requests
import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


app = Flask(__name__, static_url_path='/static', static_folder='./static')
app.secret_key = constants.SECRET_KEY
app.debug = True

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=os.environ['AUTH0_CLIENT_ID'],
    client_secret=os.environ['AUTH0_CLIENT_SECRET'],
    api_base_url=os.environ['AUTH0_BASE_URL'],
    access_token_url=os.environ['AUTH0_BASE_URL'] + '/oauth/token',
    authorize_url=os.environ['AUTH0_BASE_URL'] + '/authorize',
    client_kwargs={
        'scope': 'openid profile email token',
    },
)
BACKEND_URL=os.environ['BACKEND_URL']
def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.JWT_PAYLOAD not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


# Controllers API
@app.route('/')
def home():
    return render_template('pages/index.html')


@app.route('/login-result')
def callback_handling():
    auth_response = auth0.authorize_access_token()
    access_token = auth_response.get("access_token")
    print(access_token)
    session[constants.JWT_PAYLOAD] = access_token
    
    return redirect(url_for('movies'))


@app.route('/login')
def login():
    return auth0.authorize_redirect(
        redirect_uri=os.environ['AUTH0_CALLBACK_URL']
,        audience=os.environ['AUTH0_AUDIENCE']
        )


@app.route('/logout')
def logout():
    session.clear()
    params = {
        'returnTo': url_for('home', _external=True),
        'client_id': os.environ['AUTH0_CLIENT_ID']
        }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


# @app.route('/dashboard')
# @requires_login
# def dashboard():
#     return render_template(
#         'pages/dashboard.html',
#         userinfo=session[constants.PROFILE_KEY],
#         userinfo_pretty=json.dumps(
#             session[constants.JWT_PAYLOAD],
#             indent=4
#             )
#         )

# helper to prepare headers for backend api call
def get_headers():
    return {'Content-Type': 'application/json', 'Authorization': "Bearer %s"%session[constants.JWT_PAYLOAD]}

@app.route('/actors')
@requires_login
@requires_auth('get:actors')
def actors(payload):
    actors = []
    can_add_actor = check_has_permission("create:actor")
    can_edit_actor = check_has_permission("edit:actor")
    can_delete_actor = check_has_permission("delete:actor")
    can_get_actor_info = check_has_permission("get:actor-info")
    get_actors_url = BACKEND_URL + '/actors'
    api_response = requests.get(get_actors_url,headers=get_headers())
    response_json = api_response.json()
    actors = response_json['actors']
    return render_template(
        'pages/actors/list.html',
        actors=actors,
        can_add_actor=can_add_actor,
        can_edit_actor=can_edit_actor,
        can_delete_actor=can_delete_actor,
        can_get_actor_info=can_get_actor_info)



@app.route('/actors/add')
@requires_login
@requires_auth('create:actor')
def add_actor_form(payload):
    form = AddActorForm()
    return render_template('pages/actors/add.html',form=form)


@app.route('/actors/add', methods=['POST'])
@requires_login
@requires_auth('create:actor')
def add_actor(payload):
    form = AddActorForm(request.form)
    json_body =  {
        'name':form.name.data,
        'age':form.age.data,
        'gender':form.gender.data
    }
    actors_url = BACKEND_URL + '/actors'
    api_response = requests.post(actors_url, json=json_body, headers=get_headers())
    response_json = api_response.json()
    if(response_json['success'] and response_json['inserted']>0):
        flash('Actor created successfully','success')
        return redirect(url_for("actors"))
    else:
        flash('Could not add actor!!','danger')
        return render_template('pages/actors/add.html',form=form)


@app.route('/actors/<int:actor_id>')
@requires_login
@requires_auth('get:actor-info')
def get_actor_info(payload,actor_id):
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    api_response = requests.get(get_actors_url, headers=get_headers())
    response_json = api_response.json()
    print(response_json)
    actor = {
        'name':'',
        'age':'',
        'gender':''
    }
    movies=[]
    if(response_json['success'] and len(response_json['info'])>0):
        actor = response_json['info']
        get_actor_movies_url = BACKEND_URL + '/actors/'+ str(actor_id) + "/movies"
        movies_response = requests.get(get_actor_movies_url, headers=get_headers())
        movies_response_json = movies_response.json()
        if(response_json['success'] and len(movies_response_json['movies'])>0):
            movies = movies_response_json['movies']
            print(movies)
    elif 'error' in response_json:
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    return render_template('pages/actors/info.html',actor=actor,movies=movies)



@app.route('/actors/<int:actor_id>/edit')
@requires_login
@requires_auth('edit:actor')
def edit_actor_info_form(payload,actor_id):
    form=AddActorForm()
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    api_response = requests.get(get_actors_url, headers=get_headers())
    response_json = api_response.json()
    print(response_json)
    actor = {
        'name':'',
        'age':'',
        'gender':''
    }
    if(response_json['success'] and len(response_json['info'])>0):
        actor = response_json['info']
        form.age.data = actor['age']
        form.name.data = actor['name']
        form.gender.data = actor['gender']
    elif 'error' in response_json:
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    return render_template('pages/actors/edit.html',form=form)



@app.route('/actors/<int:actor_id>/edit', methods=['POST'])
@requires_login
@requires_auth('edit:actor')
def edit_actor_info(payload,actor_id):
    form=AddActorForm(request.form)
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    json_data = {
        'name':form.name.data,
        'age':form.age.data,
        'gender':form.gender.data
    }
    api_response = requests.patch(get_actors_url, headers=get_headers(),json = json_data)
    response_json = api_response.json()
    print(response_json)
    response_json = api_response.json()
    if(response_json['success'] and response_json['updated']>0):
        flash('Actor updated successfully','success')
        return redirect(url_for("actors"))
    elif 'error' in response_json:
        abort(response_json['error'])
    else:
        flash('Could not update actor\'s info !!','danger')
        return render_template('pages/actors/edit.html',form=form)


@app.route('/actors/<int:actor_id>/delete')
@requires_login
@requires_auth('delete:actor')
def delete_actor_info_form(payload,actor_id):
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    api_response = requests.get(get_actors_url, headers=get_headers())
    response_json = api_response.json()
    print(response_json)
    actor = {
        'name':'',
        'age':'',
        'gender':''
    }
    if(response_json['success'] and len(response_json['info'])>0):
        actor = response_json['info']
    elif 'error' in response_json:
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    return render_template('pages/actors/delete.html',actor=actor)


@app.route('/actors/<int:actor_id>/delete', methods=['POST'])
@requires_login
@requires_auth('delete:actor')
def delete_actor_info(payload,actor_id):
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    json_data = {
        'actor_id':actor_id
    }
    api_response = requests.delete(get_actors_url, headers=get_headers(),json = json_data)
    response_json = api_response.json()
    print(response_json)
    response_json = api_response.json()
    if(response_json['success'] and response_json['deleted']==actor_id):
        flash('Actor deleted successfully','success')
        return redirect(url_for("actors"))
    elif 'error' in response_json:
        abort(response_json['error'])
    else:
        flash('Could not delete actor!!','danger')
        return render_template('pages/actors/delete.html')


@app.route('/movies')
@requires_login
@requires_auth('get:movies')
def movies(payload):
    movies = []
    get_actors_url = BACKEND_URL + '/movies'
    api_response = requests.get(get_actors_url,headers=get_headers())
    response_json = api_response.json()
    movies = response_json['movies']
    can_add_movie = check_has_permission("create:movie")
    can_get_movie_info = check_has_permission("get:movie-info")
    can_edit_movie = check_has_permission("edit:movie")
    can_delete_movie = check_has_permission("delete:movie")
    return render_template(
        'pages/movies/list.html',
        movies=movies,
        can_add_movie=can_add_movie,
        can_get_movie_info=can_get_movie_info,
        can_edit_movie=can_edit_movie,
        can_delete_movie=can_delete_movie
        )


@app.route('/movies/<int:movie_id>')
@requires_login
@requires_auth('get:movie-info')
def movie_info(payload,movie_id):
    movie={
        'title':'',
        'movie_rating':'',
        'movie_category':'',
        'release_date':''
    }
    get_movie_url = BACKEND_URL + '/movies/'+str(movie_id)
    api_response = requests.get(get_movie_url,headers=get_headers())
    response_json = api_response.json()
    actors=[]
    if(response_json['success'] and len(response_json['movie'])>0):
        movie = response_json['movie']
        get_actors_url = BACKEND_URL + '/movies/{}/actors'.format(movie_id)
        api_response = requests.get(get_actors_url,headers=get_headers())
        response_json = api_response.json()
        actors = response_json['actors']
    elif 'error' in response_json:
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    can_add_actor_to_movie = check_has_permission('add:movie-actor')
    can_delete_movie_actor = check_has_permission('delete:movie-actor')

    return render_template(
        'pages/movies/info.html',
        movie=movie,
        actors=actors,
        can_add_actor_to_movie=can_add_actor_to_movie,
        can_delete_movie_actor = can_delete_movie_actor
        )


@app.route('/movies/<int:movie_id>/add-actor')
@requires_login
@requires_auth('add:movie-actor')
def add_movie_actor_form(payload,movie_id):
    return "add movie actor"



@app.route('/movies/<int:movie_id>/delete-actor')
@requires_login
@requires_auth('delete:movie-actor')
def delete_movie_actor_form(payload,movie_id):
    return "delete movie actor"


@app.route('/movies/add')
@requires_login
@requires_auth('create:movie')
def add_movie_form(payload):
    form = MovieForm()
    return render_template('pages/movies/add.html',form=form)

@app.route('/movies/<int:movie_id>/edit')
@requires_login
@requires_auth('edit:movie')
def edit_movie_form(payload,movie_id):
    movie={
        'id':movie_id,
        'title':'',
        'movie_rating':'',
        'movie_category':'',
        'release_date':''
    }
    get_movie_url = BACKEND_URL + '/movies/'+str(movie_id)
    api_response = requests.get(get_movie_url,headers=get_headers())
    response_json = api_response.json()
    if(response_json['success'] and len(response_json['movie'])>0):
        movie = response_json['movie']
    elif 'error' in response_json:
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    

    return render_template(
        'pages/movies/edit.html',
        movie=movie,
        actors=actors,
        can_add_actor_to_movie=can_add_actor_to_movie,
        can_delete_movie_actor = can_delete_movie_actor
        )


@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


# error handling for AuthError
@app.errorhandler(AuthError)
def auth_error_handler(auth_error):
    return render_template('pages/errors/autherror.html', auth_error=auth_error)

@app.errorhandler(404)
def not_found(error):
    return render_template('pages/errors/not_found.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env.get('PORT', 3000))
