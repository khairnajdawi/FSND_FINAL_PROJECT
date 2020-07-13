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
so you get the environment variables needed

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
```bash
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

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

Use test_setup.sh in backend folder to setup test environment, it will create a test db and all tables required, and will add some records to db to use in testing, you need to edit the file and change the DATABASE_URL to meet your host.
Test your endpoints with [Postman](https://getpostman.com):
- Test steps
    - Register 3 users - assign the Casting Assistant role to one, Casting Director role to another, and Executive Producer to a third.
    - Sign into each account and make note of the JWT.
    - Import the postman collection `./backend/udacity-fsnd-final-project.postman_collection.json`
    - Right-clicking the collection folder for barista and manager, navigate to the authorization tab, and including the JWT in the token field (you should have noted these JWTs).
    - Run the collection and correct any errors.
    - Export the collection overwriting the one we've included so that we have your proper JWTs during review!
    - you can use a test db , all needed command can be found in test_setup.sh.
        -to run test environment, navigate to backend directory then run command :
        ``` source test_setup.sh ```
        it will create test db and adds some data then start flask app

## Endpoints
- GET '/actors'
    - gets a list of all actors
    - Request Arguments: None
    - Returns: A boolean success, and a list of actors
    - Request example :
        ``` curl http://localhost:5000/actors```
    - Response sample : 
        ```json
        {
        "actors": [
            {
                "age": 62,
                "gender": "Male",
                "id": 1,
                "name": "Will Smith"
            },
            {
                "age": 56,
                "gender": "Male",
                "id": 2,
                "name": "Leonardo DiCaprio"
            },
            {
                "age": 35,
                "gender": "Female", 
                "name": "Scarlett Johansson"
            }
        ],
        "success": true
        } \
        ```

- POST '/actors'
    - creates a new actor
    - Request Argument : A json object contains actor's attribute : name, age, and gender
    - Returens : A boolean success, and the new actor's Id
    - Request example :
        ```
        curl --location --request POST 'http://localhost:5000/actors'
        --header 'Content-Type: application/json'
        --data-raw '{
            "name":"Will Smith",
            "age":"55",
            "gender":"Male"
        }'
        ```
    - Response sample :
        ```json
        {
            "inserted": 4,
            "success": true
        } 
        ```

- GET '/actors/&lt;int : actor_id&gt;'
    - Gets actor's info
    - Request arguments : None
    - Returns : A boolean success, and a json object of actor's info
    - Request example : 
        ```curl --location --request GET 'http://localhost:5000/actors/1'```
    - Response Sample : 
        ```json
        { 
            "info": { 
                "age": 62, 
                "gender": "Male", 
                "id": 1, 
                "name": "Will Smith" 
            }, 
            "success": true 
        } 
        ```

- DELETE '/actors/&lt;int : actor_id&gt;'
    - deletes an actor identified by the actor_id
    - Request Arguments : None
    - Returns : A boolean success, and the id of the actor just deleted
    - Request example : 
        ```curl --location --request DELETE 'http://localhost:5000/actors/4'```
    - Response Sample :
        ```json
        {
            "deleted": 4,
            "success": true
        } 
        ```

- PATCH '/actors/&lt;int : actor_id&gt;'
    - updates an actor's info whose id is actor_id
    - Request Arguments : one or more attribute of the actor : age, gender, or name
    - Returns : A boolean success, and the id of the actor just updated
    - Request example : 
        ```
        curl --location --request PATCH 'http://localhost:5000/actors/1'
        --header 'Content-Type: application/json'
        --data-raw '{
            "name":"Will Smith",
            "age":"62",
            "gender":"Male"
        }' 
        ```
    - Response Sample :
        ```json
        {
                "success": true,
                "updated": 1
        } 
        ```

- GET '/actors/&lt;actor_id&gt;/movies'
    - get a list of an actor's movies
    - Request Arguments : None
    - Returns : A boolean success, and the list of movies
    - Request example : 
        ```
        curl --location --request GET 'http://localhost:5000/actors/1/movies''
        ```
    - Response Sample :
        ```json
        {
            "movies": [
                {
                "id": 1,
                "movie_category": "Action",
                "movie_rating": "PG-13",
                "release_date": "Fri, 04 Jan 2008 00:00:00 GMT",
                "title": "I Am Legend"
                }
            ],
            "success": true
        }
        ```

- GET '/movies'
    - get a list of all movies
    - Request Arguments : None
    - Returns : A boolean success, and the list of movies
    - Request example : 
        ```
        curl --location --request GET 'http://localhost:5000/movies/1'
        ```
    - Response Sample :
        ```json
        {
            "movies": [
                {
                "id": 1,
                "movie_category": "Action",
                "movie_rating": "PG-13",
                "release_date": "Fri, 04 Jan 2008",
                "title": "I Am Legend"
                },
                {
                "id": 2,
                "movie_category": "Action",
                "movie_rating": "R",
                "release_date": "Fri, 08 Jan 2016",
                "title": "The Revenant"
                },
                {
                "id": 3,
                "movie_category": "SciFi",
                "movie_rating": "PG-13",
                "release_date": "Fri, 06 Nov 2020",
                "title": "Black Widow"
                }
            ],
            "success": true
        }
        ```


- GET '/actors/&lt;movie_id&gt;'
    - get a specific movie's info
    - Request Arguments : None
    - Returns : A boolean success, and a json object representing movie's info
    - Request example : 
        ```
        curl --location --request GET 'http://localhost:5000/movies/1'
        ```
    - Response Sample :
        ```json
        {
            "movie": {
                "id": 1,
                "movie_category": "Action",
                "movie_rating": "PG-13",
                "release_date": "Fri, 04 Jan 2008",
                "title": "I Am Legend"
            },
            "success": true
        } 
        ```

- POST '/movies'
    - create a new movie
    - Request Arguments : a json object contains movie's info
    - Returns : A boolean success, and a json object representing movie's info
    - Request example : 
        ```
        curl --location --request POST 'http://localhost:5000/movies' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "title":"Am Legend",
            "movie_rating":"PG13",
            "movie_category":"Action",
            "release_date":"01/04/2008"
        }'
        ```
    - Response Sample :
        ```json
        {
            "new_movie_id": 4,
            "success": true
        } 
        ```

- PATCH '/movies/&lt;int:movie_id&gt;'
    - edit movie's info
    - Request Arguments : a json object contains movie's info
    - Returns : A boolean success, and the id of the movie just updated
    - Request example : 
        ```
        curl --location --request PATCH 'http://localhost:5000/movies/1' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "name":"Am Legend",
            "movie_category":"SciFi"
        }'
        ```
    - Response Sample :
        ```json
        {
            "success": true,
            "updated": 1
        } 
        ```

- GET '/movies/&lt;int:movie_id&gt;/actors'
    - get a list of all movie's actors
    - Request Arguments : None
    - Returns : A boolean success, and a list of movie's actor
    - Request example : 
        ```
        curl --location --request GET 'http://localhost:5000/movies/1/actors'
        ```
    - Response Sample :
        ```json
        {
            "actors": [
                {
                "age": 62,
                "gender": "Male",
                "id": 1,
                "name": "Will Smith"
                }
            ],
            "success": true
        } 
        ```


- POST '/movies/&lt;int:movie_id&gt;/actors'
    - add an actor from a movie's actors list
    - Request Arguments : a json object contains the id of the actor to be added
    - Returns : A boolean success, and the id of both actor and movie
    - Request example : 
        ```
        curl --location --request POST 'http://localhost:5000/movies/1/actors' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "actor_id":2
        }'
        ```
    - Response Sample :
        ```json
        {
            "actor": 2,
            "movie": 1,
            "success": true
        } 
        ```

- DELETE '/movies/&lt;int:movie_id&gt;/actors'
    - remove an actor from a movie's actors list
    - Request Arguments :  json object contains the id of the actor to be deleted
    - Returns : A boolean success, and the id of both actor and movie
    - Request example : 
        ```
        curl --location --request DELETE 'http://localhost:5000/movies/1/actors' \
        --header 'Content-Type: application/json' \
        --data-raw '{
            "actor_id":2
        }'
        ```
    - Response Sample :
        ```json
        {
            "deleted": 2,
            "movie": 1,
            "success": true
        } 
        ```

- DELETE '/movies/&lt;int:movie_id&gt;'
    - delete a movie
    - Request Arguments :  None
    - Returns : A boolean success, and the id of the movie just deleted
    - Request example : 
        ```
        curl --location --request DELETE 'http://localhost:5000/movies/4'
        ```
    - Response Sample :
        ```json
        {
            "movie": 4,
            "success": true
        } 
        ```

## Deploying to Heroku :

- DB Migration : 
```
heroku run python ./backend/manage.py db upgrade --directory ./backend/migrations
```