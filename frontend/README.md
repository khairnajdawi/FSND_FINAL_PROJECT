# Casting Agency Front End
this front end app was built using flask forms wtf, for using with the backend in this repo.


## Running the server

From within root directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:
```bash
source ./frontend/setup.py;
```
so you get the environment variables needed


To run the server, execute:

```bash
python3 ./fronend/app.py
```

## Authentication & Authorization
The authentication system used for this project is Auth0. ```./frontend/auth.py``` contains the logic to retrieve access token from session, decode it and verify it, and check for permissions for each endpoint using the ```require_auth``` decorator. Also there is ```check_has_permission``` method to check if the current user has a specific permission to do some action, for example : ```check_has_permission("create:actor")``` is used in actors endpoint to check if the user can add new actor, so we show or hide the button to add new actor.
For endpoints ```./frontend/app.py``` containts the app routes, each route have its ```require_auth(permission)``` corresponding to its action, and contains the auth error handler and error handlers for other erros like 401,403 ...etc.


## Setup Auth0
### if you didn't already setup auth0 with backend, then :
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
