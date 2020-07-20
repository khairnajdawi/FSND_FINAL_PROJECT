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
from datetime import datetime
import dateutil.parser
import babel

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# create flask app
app = Flask(__name__, static_url_path='/static', static_folder='./static')
app.secret_key = constants.SECRET_KEY
app.debug = True

# create oauth client object
oauth = OAuth(app)
# register auth client
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

# read backend url from environment variables
BACKEND_URL=os.environ['BACKEND_URL']

# helper method to format datetimes
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  elif format == 'small':
      format="MM/dd/yyyy"
  return babel.dates.format_datetime(date, format)

# set format date for our app
app.jinja_env.filters['datetime'] = format_datetime


# decorater to require login for endpoints
def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.JWT_PAYLOAD not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


# home endpoint
@app.route('/')
def home():
    return render_template('pages/index.html')


# endpoint to handle auth0 login result
@app.route('/login-result')
def callback_handling():
    # authorize reponse with auth0
    auth_response = auth0.authorize_access_token()
    # read access token and store it in session
    access_token = auth_response.get("access_token")
    print(access_token)
    session[constants.JWT_PAYLOAD] = access_token
    # after success login, redirect to movies endpoint
    return redirect(url_for('movies'))


# login endpoint, redirects to auth0 login page
@app.route('/login')
def login():
    return auth0.authorize_redirect(
        redirect_uri=os.environ['AUTH0_CALLBACK_URL']
,        audience=os.environ['AUTH0_AUDIENCE']
        )


# logout endpoint, to logout current auth0 user
# then it will redirect to home page as configured in auth0
@app.route('/logout')
def logout():
    session.clear()
    params = {
        'returnTo': url_for('home', _external=True),
        'client_id': os.environ['AUTH0_CLIENT_ID']
        }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


# helper to prepare headers for backend api call
def get_headers():
    return {'Content-Type': 'application/json', 'Authorization': "Bearer %s"%session[constants.JWT_PAYLOAD]}


# actors endpoint, shows a list of all actors
# requires get:actors permission
@app.route('/actors')
@requires_login
@requires_auth('get:actors')
def actors(payload):
    actors = []
    # check user permissions, used to show buttons in the page
    can_add_actor = check_has_permission("create:actor")
    can_edit_actor = check_has_permission("edit:actor")
    can_delete_actor = check_has_permission("delete:actor")
    can_get_actor_info = check_has_permission("get:actor-info")
    # make request call to backend to read actors list
    get_actors_url = BACKEND_URL + '/actors'
    api_response = requests.get(get_actors_url,headers=get_headers())
    response_json = api_response.json()
    if(response_json['success'] and len(response_json['actors'])>0):
        # fetch actors list from reponse
        actors = response_json['actors']
    else:
        flash('Could not fetch actors list!!','danger')
    return render_template(
        'pages/actors/list.html',
        actors=actors,
        can_add_actor=can_add_actor,
        can_edit_actor=can_edit_actor,
        can_delete_actor=can_delete_actor,
        can_get_actor_info=can_get_actor_info)



# endpoint to add actor
# requires create:actor permission
@app.route('/actors/add')
@requires_login
@requires_auth('create:actor')
def add_actor_form(payload):
    # prepare wtf form
    form = AddActorForm()
    return render_template('pages/actors/add.html',form=form)


# endpoint to add actor action
# requires create:actor permission
@app.route('/actors/add', methods=['POST'])
@requires_login
@requires_auth('create:actor')
def add_actor(payload):
    # prepare form to read form data
    form = AddActorForm(request.form)
    # prepare json data for use with backend request
    json_body =  {
        'name':form.name.data,
        'age':form.age.data,
        'gender':form.gender.data
    }
    # backend url for actors
    actors_url = BACKEND_URL + '/actors'
    # make post request
    api_response = requests.post(actors_url, json=json_body, headers=get_headers())
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and response_json['inserted']>0):
        # flash success and return to actors list
        flash('Actor created successfully','success')
        return redirect(url_for("actors"))
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        # flash error and stay on page
        flash('Could not add actor!!','danger')
        return render_template('pages/actors/add.html',form=form)


# endpoint for actors details
# requires get:actor-info permissions
@app.route('/actors/<int:actor_id>')
@requires_login
@requires_auth('get:actor-info')
def get_actor_info(payload,actor_id):
    # backend url for actor's info
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    # make get request
    api_response = requests.get(get_actors_url, headers=get_headers())
    response_json = api_response.json()
    # create empty actor info
    actor = {
        'name':'',
        'age':'',
        'gender':''
    }
    # empty movies array to store actor's movies
    movies=[]
    # read backend response
    if(response_json['success'] and len(response_json['info'])>0):
        # read actor info
        actor = response_json['info']
        # make request for actor's movies /actors/<int:actor_id>/movies
        get_actor_movies_url = BACKEND_URL + '/actors/'+ str(actor_id) + "/movies"
        movies_response = requests.get(get_actor_movies_url, headers=get_headers())
        movies_response_json = movies_response.json()
        # read actor's movies from response
        if(response_json['success'] and len(movies_response_json['movies'])>0):
            movies = movies_response_json['movies']
            print(movies)
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    return render_template('pages/actors/info.html',actor=actor,movies=movies)



# endpoint for edit actor's info
# requires edit:actor permission
@app.route('/actors/<int:actor_id>/edit')
@requires_login
@requires_auth('edit:actor')
def edit_actor_info_form(payload,actor_id):
    # prepare form
    form=AddActorForm()
    # get actor's info from backend
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    api_response = requests.get(get_actors_url, headers=get_headers())
    response_json = api_response.json()
    print(response_json)
    actor = {
        'name':'',
        'age':'',
        'gender':''
    }
    # read actor's info from response and prepare form inputs
    if(response_json['success'] and len(response_json['info'])>0):
        actor = response_json['info']
        form.age.data = actor['age']
        form.name.data = actor['name']
        form.gender.data = actor['gender']
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    return render_template('pages/actors/edit.html',form=form)



# endpoint for edit actor's info action
# requires edit:actor permission
@app.route('/actors/<int:actor_id>/edit', methods=['POST'])
@requires_login
@requires_auth('edit:actor')
def edit_actor_info(payload,actor_id):
    # prepare from from posted data
    form=AddActorForm(request.form)
    # edit actor's info backend url
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    # prepare json data to use with backend post
    json_data = {
        'name':form.name.data,
        'age':form.age.data,
        'gender':form.gender.data
    }
    # make post request
    api_response = requests.patch(get_actors_url, headers=get_headers(),json = json_data)
    response_json = api_response.json()
    # read backend response and 
    if(response_json['success'] and response_json['updated']>0):
        # flash success and return to actors list
        flash('Actor updated successfully','success')
        return redirect(url_for("actors"))
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Could not update actor\'s info !!','danger')
        return render_template('pages/actors/edit.html',form=form)


# delete actor endpoint
# require delete:actor permission
@app.route('/actors/<int:actor_id>/delete')
@requires_login
@requires_auth('delete:actor')
def delete_actor_info_form(payload,actor_id):
    # get actor info backend url, to display actor name
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    api_response = requests.get(get_actors_url, headers=get_headers())
    response_json = api_response.json()
    # empty actor info
    actor = {
        'name':'',
        'age':'',
        'gender':''
    }
    # read info from backend response
    if(response_json['success'] and len(response_json['info'])>0):
        actor = response_json['info']
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    return render_template('pages/actors/delete.html',actor=actor)


# delete actor action endpoint
# require delete:actor permission
@app.route('/actors/<int:actor_id>/delete', methods=['POST'])
@requires_login
@requires_auth('delete:actor')
def delete_actor_info(payload,actor_id):
    # delete actor backend url
    get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
    # make delete request to backend
    api_response = requests.delete(get_actors_url, headers=get_headers())
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and response_json['deleted']==actor_id):
        # if deleted successfully, flash success and return to actors list
        flash('Actor deleted successfully','success')
        return redirect(url_for("actors"))
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Could not delete actor!!','danger')
        return render_template('pages/actors/delete.html')


# endpoint for movies list
# requires get:movies permission
@app.route('/movies')
@requires_login
@requires_auth('get:movies')
def movies(payload):
    # movies array to store movies from backend response
    movies = []
    # backend url to read movies list
    get_actors_url = BACKEND_URL + '/movies'
    # make get request to backend
    api_response = requests.get(get_actors_url,headers=get_headers())
    response_json = api_response.json()
    if(response_json['success'] and 'movies' in response_json):
        movies = response_json['movies']        
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Could not get movies list!!','danger')
    
    # check user permissions
    # if can create a new movie
    can_add_movie = check_has_permission("create:movie")
    # if can read movie info
    can_get_movie_info = check_has_permission("get:movie-info")
    # if can edit movie's info
    can_edit_movie = check_has_permission("edit:movie")
    # if can delete movie
    can_delete_movie = check_has_permission("delete:movie")
    return render_template(
        'pages/movies/list.html',
        movies=movies,
        can_add_movie=can_add_movie,
        can_get_movie_info=can_get_movie_info,
        can_edit_movie=can_edit_movie,
        can_delete_movie=can_delete_movie
        )


# endpoint to display movie's info
# requires get:movie-info permission
@app.route('/movies/<int:movie_id>')
@requires_login
@requires_auth('get:movie-info')
def movie_info(payload,movie_id):
    # prepare movie object with empty data
    movie={
        'title':'',
        'movie_rating':'',
        'movie_category':'',
        'release_date':''
    }
    # get movie backend url
    get_movie_url = BACKEND_URL + '/movies/'+str(movie_id)
    # make get response
    api_response = requests.get(get_movie_url,headers=get_headers())
    response_json = api_response.json()
    # empty actors list to store movie's actors list
    actors=[]
    # check backend response
    if(response_json['success'] and len(response_json['movie'])>0):
        # read movie info
        movie = response_json['movie']
        # backend url for reading movie's actors list
        get_actors_url = BACKEND_URL + '/movies/{}/actors'.format(movie_id)
        # make get request
        api_response = requests.get(get_actors_url,headers=get_headers())
        response_json = api_response.json()
        # read actors list
        actors = response_json['actors']
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    # check user permissions
    # if can add actor to movie's actors list
    can_add_actor_to_movie = check_has_permission('add:movie-actor')
    # if can remove an actor from movie's actors list
    can_delete_movie_actor = check_has_permission('delete:movie-actor')

    return render_template(
        'pages/movies/info.html',
        movie=movie,
        actors=actors,
        can_add_actor_to_movie=can_add_actor_to_movie,
        can_delete_movie_actor = can_delete_movie_actor
        )


# endpoint to add actor to movie's actors list
# requires add:movie-actor permission
@app.route('/movies/<int:movie_id>/addactor')
@requires_login
@requires_auth('add:movie-actor')
def add_movie_actor_form(payload,movie_id):
    # prepare form
    form = MovieActorsForm()
    # empty movie info object
    movie={
        'title':'',
        'movie_rating':'',
        'movie_category':'',
        'release_date':''
    }
    # backend url to read movie's info
    get_movie_url = BACKEND_URL + '/movies/'+str(movie_id)
    # make get request to read movie's info
    api_response = requests.get(get_movie_url,headers=get_headers())
    response_json = api_response.json()
    # empty list to store movie's actors list
    actors=[]
    # check backend response
    if(response_json['success'] and len(response_json['movie'])>0):
        # read movie info
        movie = response_json['movie']
        # backend to read all actors list
        get_actors_url = BACKEND_URL + '/actors'
        api_response = requests.get(get_actors_url,headers=get_headers())
        response_json = api_response.json()
        # read actors list from backend response
        actors = response_json['actors']
        
        # backend to read movie's actors list
        get_movie_actors_url = BACKEND_URL + '/movies/{}/actors'.format(movie_id)
        api_response = requests.get(get_movie_actors_url,headers=get_headers())
        response_json = api_response.json()
        # read movie's actors list from backend response
        movie_actors = response_json['actors']
        # prepare form with actor's that can be added to movie's actors list
        # such that an actor is not already added
        form.actor.choices = [(actor['id'],actor['name']) for actor in actors if actor not in movie_actors]
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    return render_template('pages/movies/addactor.html',form=form,movie=movie,movie_actors=movie_actors)



# endpoint for add movie's actor action
# requires add:movie-actor permission
@app.route('/movies/<int:movie_id>/addactor',methods=['POST'])
@requires_login
@requires_auth('add:movie-actor')
def add_movie_actor_action(payload,movie_id):
    # prepare form to read data from
    form = MovieActorsForm(request.form)
    # read selected actor's id to add to movie's actors list
    selected_actor_id  = form.actor.data
    # backend url
    add_movie_actor_url = BACKEND_URL + '/movies/'+str(movie_id)+"/actors"
    # make post request to add selected actor
    api_response = requests.post(
        add_movie_actor_url,
        headers=get_headers(),
        json={'actor_id': selected_actor_id}
        )
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and response_json['actor']==selected_actor_id):
        # if success, flash success
        flash('Actor added successfully','success')
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        # in other cases, i.e not added nor there is exception, flash error
        flash('Something went wrong!!','danger')
    # in all cases, return to movie's info page
    return redirect('/movies/'+str(movie_id))


# endpoint to remove an actor from movie's actors list
# requires delete:movie-actor
@app.route('/movies/<int:movie_id>/deleteactor/<int:actor_id>')
@requires_login
@requires_auth('delete:movie-actor')
def delete_movie_actor_form(payload,movie_id,actor_id):  
    # empty movie object  
    movie={
        'title':'',
        'movie_rating':'',
        'movie_category':'',
        'release_date':''
    }
    # empty actor object
    actor = {
        'name':'',
        'age':'',
        'gender':''
    }
    # get movie's info backend url
    get_movie_url = BACKEND_URL + '/movies/'+str(movie_id)
    # make get request to read movie's info
    api_response = requests.get(get_movie_url,headers=get_headers())
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and len(response_json['movie'])>0):
        # read movie's info
        movie = response_json['movie']
        # backend url to read actor's info
        get_actors_url = BACKEND_URL + '/actors/'+ str(actor_id)
        # make get request to read actor's info
        api_response = requests.get(get_actors_url, headers=get_headers())
        response_json = api_response.json()
        # read actors info from response
        actor = response_json['info']
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    return render_template('pages/movies/deleteactor.html',movie=movie,actor=actor)


# endpoint to remove an actor from movie's actors list
# requires delete:movie-actor
@app.route('/movies/<int:movie_id>/deleteactor/<int:actor_id>', methods=['POST'])
@requires_login
@requires_auth('delete:movie-actor')
def delete_movie_actor_action(payload,movie_id,actor_id):    
    # backend to delete actor's from movie's actors list
    delete_movie_actor_url = BACKEND_URL + '/movies/'+str(movie_id)+'/actors'
    # json data to use with backend request
    json_data = {'actor_id': actor_id}
    # make delete request
    api_response = requests.delete(
        delete_movie_actor_url,
        headers=get_headers(),
        json=json_data
        )
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and response_json['deleted']==actor_id):
        # flash success if actor were removed
        flash('Actor were removed from movie!!','success')
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    # in all cases, return to movie's info page
    return redirect('/movies/'+str(movie_id))


# enpoint to add new movie
# requires create:movie permission
@app.route('/movies/add')
@requires_login
@requires_auth('create:movie')
def add_movie_form(payload):
    # prepare form and show page
    form = MovieForm()
    return render_template('pages/movies/add.html',form=form)


# enpoint to add new movie
# requires create:movie permission
@app.route('/movies/add', methods=['POST'])
@requires_login
@requires_auth('create:movie')
def add_new_movie(payload):
    # prepare form to read posted data
    form = MovieForm(request.form)
    # create json object to use with backend request
    new_movie = {
        'title': form.title.data,
        'movie_category': form.movie_category.data,
        'movie_rating': form.movie_rating.data,
        'release_date': str(form.release_date.data)
    }
    # add movie backend url
    create_movie_url = BACKEND_URL + '/movies'
    # make post request to backend
    api_response = requests.post(
        create_movie_url,
        headers = get_headers(),
        json = new_movie
    )
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and response_json['new_movie_id']>0):
        # if addedd successfully, flash success and return to movie's list page
        flash('Movie created successfully!','success')
        return redirect(url_for('movies'))
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
    
    return render_template('pages/movies/add.html',form=form)


# endpoint to edit movie's info
# requires edit:movie permission
@app.route('/movies/<int:movie_id>/edit')
@requires_login
@requires_auth('edit:movie')
def edit_movie_form(payload,movie_id):
    # perpare form
    form = MovieForm()
    # empty movie's info object
    movie={
        'id':movie_id,
        'title':'',
        'movie_rating':'',
        'movie_category':'',
        'release_date':''
    }
    # backend url to read movie's info
    get_movie_url = BACKEND_URL + '/movies/'+str(movie_id)
    # make get request to read movie's info
    api_response = requests.get(get_movie_url,headers=get_headers())
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and len(response_json['movie'])>0):
        # read movie's info
        movie = response_json['movie']
        # prepare form with movie's info
        form.title.data = movie['title']
        form.movie_rating.data = movie['movie_rating']
        form.movie_category.data = movie['movie_category']
        # date1 = movie['movie_category'].strftime("%y/%m%d")

        date = dateutil.parser.parse(movie['release_date'])
        print(date)
        form.release_date.data = date
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')
        return redirect(url_for("movies"))
    
    return render_template(
        'pages/movies/edit.html',
        movie=movie,
        form = form
        )


# endpoint to edit movie's info action
# requires edit:movie permission
@app.route('/movies/<int:movie_id>/edit', methods=['POST'])
@requires_login
@requires_auth('edit:movie')
def edit_movie_action(payload,movie_id):
    # prepare form with posted data
    form = MovieForm(request.form)
    # create movie object to use with backend request
    updated_movie_info = {
        'title': form.title.data,
        'movie_category': form.movie_category.data,
        'movie_rating': form.movie_rating.data,
        'release_date': str(form.release_date.data)
    }
    # backend to update movie's info
    edit_movie_url = BACKEND_URL + '/movies/'+str(movie_id)
    # make patch request
    api_response = requests.patch(
        edit_movie_url,
        headers = get_headers(),
        json = updated_movie_info
    )
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and response_json['updated']==movie_id):
        # if updated successfully, flash success and return to movie's info list
        flash('Movie updated successfully!','success')
        return redirect('/movies/'+str(movie_id))
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        flash('Something went wrong!!','danger')

    return render_template('pages/movies/edit.html',form=form)


# endpoint to delete movie
# requires delete:movie permission
@app.route('/movies/<int:movie_id>/delete')
@requires_login
@requires_auth("delete:movie")
def delete_movie_form(payload,movie_id):
    # empty object to read movie's info
    movie={
        'title':'',
        'movie_rating':'',
        'movie_category':'',
        'release_date':''
    }
    # backend url to read movie's info
    get_movie_url = BACKEND_URL + '/movies/'+str(movie_id)
    # make get request to read movie's info
    api_response = requests.get(get_movie_url,headers=get_headers())
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and len(response_json['movie'])>0):
        # read movie's info
        movie = response_json['movie']
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        # if there is another error, flash error and return to movies list
        flash('Something went wrong!!','danger')
        return redirect(url_for('movies'))
    return render_template('pages/movies/delete.html',movie=movie)


# endpoint to delete movie
# requires delete:movie permission
@app.route('/movies/<int:movie_id>/delete', methods=['POST'])
@requires_login
@requires_auth("delete:movie")
def delete_movie_action(payload,movie_id):
    # backend url to delete movie
    delete_movie_url = BACKEND_URL + '/movies/'+str(movie_id)
    # make delete request
    api_response = requests.delete(delete_movie_url,headers=get_headers())
    response_json = api_response.json()
    # check backend response
    if(response_json['success'] and response_json['deleted']==movie_id):
        # if successfully deleted, flash success
        flash('Movie deleted successfully','success')
    elif 'error' in response_json:
        # if there is error in response, abort for error code
        abort(response_json['error'])
    else:
        # another error
        flash('Something went wrong!!','danger')

    # in all cases, return to movies list
    return redirect(url_for('movies'))


# General exceptions handler
@app.errorhandler(Exception)
def handle_debug_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


# error handling for AuthError
@app.errorhandler(AuthError)
def auth_error_handler(auth_error):
    return render_template('pages/errors/autherror.html', auth_error=auth_error)


# error handler for 404
@app.errorhandler(404)
def not_found(error):
    return render_template('pages/errors/not_found.html')


# error handler for 401
@app.errorhandler(401)
def unauthorized(error):
    return render_template('pages/errors/unauthorized.html')


# error handler for 403
@app.errorhandler(403)
def access_denied(error):
    return render_template('pages/errors/access_denied.html')


# run appa on localhost port 3000
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env.get('PORT', 3000))
