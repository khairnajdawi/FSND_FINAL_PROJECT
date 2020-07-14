"""Python Flask WebApp Auth0 integration example
"""
from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv
from flask import Flask, request
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import http.client
import constants

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = 'http://localhost:3000/login-result'
AUTH0_CLIENT_ID = 'nm6XTUr2X9Nyefwrql8h8Tcw7inGGkgX'
AUTH0_CLIENT_SECRET = 'PKCuDxSCLSoqJ4ew_RSyDy4wwfZkne4hcyYJ5Zz7Cb1ZxrGBpPYXvPMjwqiFLhEf'
AUTH0_DOMAIN = 'kj-casting-agency.us.auth0.com'
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = 'https://kj-casting-system.herukoapp.com'

app = Flask(__name__, static_url_path='/static', static_folder='./static')
app.secret_key = constants.SECRET_KEY
app.debug = True

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)



def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if constants.PROFILE_KEY not in session:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorated


# Controllers API
@app.route('/')
def home():
    return render_template('pages/index.html')


@app.route('/login-result')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    code = request.get('code');
    print(code)

    conn = http.client.HTTPSConnection("")

    payload = "grant_type=authorization_code&client_id=${account.clientId}&client_secret={AUTH0_CLIENT_SECRET}&code={code}&redirect_uri=${account.callback}"

    headers = { 'content-type': "application/x-www-form-urlencoded" }

    conn.request("POST", "/{AUTH0_DOMAIN}/oauth/token", payload, headers)

    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))

    return redirect('/movies')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)


@app.route('/logout')
def logout():
    session.clear()
    params = {'returnTo': url_for('home', _external=True), 'client_id': AUTH0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('pages/dashboard.html',
                           userinfo=session[constants.PROFILE_KEY],
                           userinfo_pretty=json.dumps(session[constants.JWT_PAYLOAD], indent=4))

@app.route('/actors')
@requires_auth 
def actors():
    actors = []
    return render_template('pages/actors/list.html',actors=actors)


@app.route('/movies')
def movies():
    movies = []
    return render_template('pages/movies/list.html',movies=movies)



@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=env.get('PORT', 3000))

