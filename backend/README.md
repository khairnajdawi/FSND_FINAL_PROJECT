# Casting Agency Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries to handle the lightweight sqlite database. Since we want you to focus on auth, we handle the heavy lift for you in `./src/database/models.py`. We recommend skimming this code first so you know how to interface with the Drink model.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS.

## Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:
```bash
source ./setup.py;
```
so you get the environment variable needed

```bash
export FLASK_APP=flaskr;
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## Tasks

### configure DB
edit the model class './backend/setup.sh' 
and change the DATABASE_URL value to meet your host
then use Migration to create your db
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade

### Setup Auth0

1. Create a new Auth0 Account
2. Select a unique tenant domain
3. Create a new, single page web application
4. Create a new API
    - in API Settings:
        - Enable RBAC
        - Enable Add Permissions in the Access Token
5. Create new API permissions:
    - `get:actors`
    - `get:actor-info`
    - `create:actor`
    - `edit:actor`
    - `delete:actor`
    - `get:actor-movies`
    - `get:movies`
    - `get:movie-info`
    - `create:movie`
    - `edit:movie`
    - `delete:movie`
    - `get:movie-actors`
    - `add:movie-actor`
    - `delete:movie-actor`
6. Create new roles for:
    - Casting Assistant
        - can `get:actors`, `get:actor-info`, `get:actor-movies`,
         `get:movies`, `get:movie-info`, `get:movie-actors`
    - Casting Director
        - can `get:actors`, `get:actor-info`, `get:actor-movies`,
         `get:movies`, `get:movie-info`, `get:movie-actors`,
         `create:actor`, `edit:actor`, `delete:actor`,
         `edit:movie`, `add:movie-actor`, `delete:movie-actor`
    - Executive Producer
        - can perform all actions

## Testing
Use test_setup.sh in backend folder to setup test environment,
it will create a test db and all tables required,
and will add some records to db to use in testing,
you need to edit the file and change the DATABASE_URL to meet your host
Test your endpoints with [Postman](https://getpostman.com). 
    - Register 3 users - assign the Casting Assistant role to one, Casting Director role to another, and Executive Producer to a third.
    - Sign into each account and make note of the JWT.
    - Import the postman collection `./backend/udacity-fsnd-final-project.postman_collection.json`
    - Right-clicking the collection folder for barista and manager, navigate to the authorization tab, and including the JWT in the token field (you should have noted these JWTs).
    - Run the collection and correct any errors.
    - Export the collection overwriting the one we've included so that we have your proper JWTs during review!


