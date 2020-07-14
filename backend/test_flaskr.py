import os
import unittest
import json
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Actors, Movies


class CastingAgencyTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = os.environ['DATABASE_URL']
        setup_db(self.app, self.database_path)

        self.headers = {
            'authorization':
            "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik95QUxwckNURjZqY2x3d3JBekFTRSJ9.eyJpc3MiOiJodHRwczovL2tqLWNhc3RpbmctYWdlbmN5LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZjBiN2JkMWExNWI3YjAwMTM2MjEyYjkiLCJhdWQiOiJodHRwczovL2tqLWNhc3Rpbmctc3lzdGVtLmhlcnVrb2FwcC5jb20iLCJpYXQiOjE1OTQ2NDg2MTksImV4cCI6MTU5NDczNTAxOSwiYXpwIjoibm02WFRVcjJYOU55ZWZ3cnFsOGg4VGN3N2luR0drZ1giLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImFkZDptb3ZpZS1hY3RvciIsImNyZWF0ZTphY3RvciIsImNyZWF0ZTptb3ZpZSIsImRlbGV0ZTphY3RvciIsImRlbGV0ZTptb3ZpZSIsImRlbGV0ZTptb3ZpZS1hY3RvciIsImVkaXQ6YWN0b3IiLCJlZGl0Om1vdmllIiwiZ2V0OmFjdG9yLWluZm8iLCJnZXQ6YWN0b3ItbW92aWVzIiwiZ2V0OmFjdG9ycyIsImdldDptb3ZpZS1hY3RvcnMiLCJnZXQ6bW92aWUtaW5mbyIsImdldDptb3ZpZXMiXX0.RphvEFbZHtEmw0GFQKsJB3UznIVQ3LB9OnyLoX5x7djlr28tEdv5EmAI6sNNsswbmDKZPxo2kb1IPEJSC6IBYStDaHGsphGSkhpXtAJ2OmzgYf92vT4V6cO1h9OLLnS-NGdcT4lDTYjFb3tsDBqEeZ0FoG2ikvWO4HxhpQu7ujHTl8y2gApI-Iasxr4Sv0UKW8gZbUkA44qJFO49-WMZ_szD3TswCSPpjuj9_o41s-mk1CDqx56ChSiM7fU_TC-lj18RFHQlg4AoeQEFtCVx0-xWXzM2wFfWDI4koMrWadNfp8jNKG4DoQIJT58wSMJkZ5VjymwGR4XXm8PVgTvdVw"
            }

        # create new question for add test
        self.new_actor = {
            'name': 'Test Actor',
            'age': 33,
            'gender': 'Male'
        }
        self.bad_new_actor = {
            'name': 'Test Actor'
        }
        self.new_movie = {
            'title': 'Test Movie',
            'release_date': '1/1/2020',
            'movie_rating': 'PG',
            'movie_category': 'Action'
        }
        self.bad_new_movie = {
            'title': 'Test Movie',
            'movie_category': 'Action'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # test get all actors, should return http code 200,success with actors list
    def test_get_actors(self):
        res = self.client().get('/actors', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actors']))

    # test add actor, shourld return http code 200,
    # True success with the new actor's id
    def test_add_new_actor(self):
        res = self.client().post(
            '/actors',
            json=self.new_actor,
            headers=self.headers
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['inserted'], True)

    # test add actor failure, shourld return http code 422, false success
    def test_add_new_actor_failure(self):
        res = self.client().post(
            '/actors',
            json=self.bad_new_actor,
            headers=self.headers
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # test get actor's info, should return http code 200,
    # success with the actor's info object
    def test_get_actor_info(self):
        res = self.client().get('/actors/1', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['info']))

    # test get actor's info who doesn't exist,
    # should return http code 404, false success with the actor's info object
    def test_get_not_found_actor_info(self):
        res = self.client().get('/actors/1111', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test delete actor success, should return 200 http code,
    # success with the id of actor just deleted
    def test_delete_actor_success(self):
        res = self.client().delete('/actors/4', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['deleted'], True)

    # test delete actor failure when actor doesn't exist,
    # should return 404 http code,false success
    def test_delete_actor_failure(self):
        res = self.client().delete('/actors/6666', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test edit actor's info success, should return 200 code, success boolean
    def test_edit_actor_info(self):
        res = self.client().patch(
            '/actors/1',
            headers=self.headers,
            json={"name": "Will Smith"}
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['updated'], True)

    # test edit actor's info failure when actor does not exist,
    # should return 404 http code, success boolean false
    def test_edit_actor_info_failure(self):
        res = self.client().patch(
            '/actors/444',
            headers=self.headers,
            json={"name": "Brad Pitt"}
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test edit actor's info failure when no data provided,
    # should return 422 http code, success boolean false
    def test_edit_actor_info_failure_no_data(self):
        res = self.client().patch('/actors/3', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # test get actor's movies, should return 200 http code,
    # success boolean and a list of movies
    def test_get_actor_movies(self):
        res = self.client().get('/actors/1/movies', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movies']))

    # test get actor's movies failure when actor does not exist,
    # should return 404 http code, success boolean false
    def test_get_actor_movies_failure(self):
        res = self.client().get('/actors/3333/movies', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test get movies list, should return 200 status code,
    # success boolean and a list of movies
    def test_get_movies(self):
        res = self.client().get('/movies', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movies']))

    # test get movie's info, should return 200 status code,
    # success boolean and a info object
    def test_get_movie_info(self):
        res = self.client().get('/movies/1', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['movie']))

    # test get movie's info failure, should return 404 status code,
    # success boolean and a info object
    def test_get_movie_info_failure(self):
        res = self.client().get('/movies/1111', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test create a new movie success, should return 200 http status code,
    # success boolean and new movie's id
    def test_add_movie_success(self):
        res = self.client().post(
            '/movies',
            headers=self.headers,
            json=self.new_movie
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue((data['new_movie_id']))

    # test create a new movie failure when no data or bad data,
    # should return 422 http status code, success false
    def test_add_movie_failure(self):
        res = self.client().post(
            '/movies',
            headers=self.headers,
            json=self.bad_new_movie
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # test edit a movie success, should return 200 http status code,
    # success true and the updated movie's id
    def test_edit_movie_info_success(self):
        res = self.client().patch(
            '/movies/1',
            headers=self.headers,
            json={"title": "Am Legend"}
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['updated'], 1)

    # test edit a movie failure when movie does not exist,
    # should return 404 http status code, success false
    def test_edit_movie_info_failure_not_exist(self):
        res = self.client().patch(
            '/movies/11111',
            headers=self.headers,
            json={"title": "Am Legend"}
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test edit a movie failure when no data,
    # should return 400 http status code, success false
    def test_edit_movie_info_failure_no_data(self):
        res = self.client().patch('/movies/2', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    # test get movie's actors list success, should return 200 http status code,
    # success boolean and a list of actors
    def test_get_movie_actors(self):
        res = self.client().get('/movies/2/actors', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['actors']))

    # test get movie's actors list failure if movie does not exist,
    # should return 404 http status code, false success boolean
    def test_get_movie_actors_failure_not_exist(self):
        res = self.client().get('/movies/2222/actors', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test get movie's actors list success, should return 200 http status code,
    # success boolean and a list of actors
    def test_add_movie_actor(self):
        res = self.client().post(
            '/movies/2/actors',
            headers=self.headers,
            json={"actor_id": 1}
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # test get movie's actors list failure if movie does not exist,
    # should return 404 http status code, false success boolean
    def test_add_movie_actor_failure_not_exist(self):
        res = self.client().post(
            '/movies/2222/actors',
            headers=self.headers,
            json={"actor_id": 1}
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test get movie's actors list failure if no data,
    # should return 400 http status code, false success boolean
    def test_add_movie_actor_failure_no_data(self):
        res = self.client().post('/movies/2/actors', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    # test get movie's actors list failure if actor does not exist,
    # should return 422 http status code, false success boolean
    def test_add_movie_actor_failure_actor_not_exist(self):
        res = self.client().post(
            '/movies/2/actors',
            headers=self.headers,
            json={"actor_id": 1111}
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # test ddelete movie's actor success,
    # should return 200 http status code, success boolean
    def test_delete_movie_actor(self):
        res = self.client().post(
            '/movies/2/actors',
            headers=self.headers,
            json={"actor_id": 1}
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    # test ddelete movie's actor failure if no data,
    # should return 400 http status code, success boolean
    def test_delete_movie_actor_failure_no_data(self):
        res = self.client().post('/movies/2/actors', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    # test ddelete movie's actor failure if movie not exist,
    # should return 404 http status code, success boolean
    def test_delete_movie_actor_failure_movie_not_exist(self):
        res = self.client().post(
            '/movies/222/actors',
            headers=self.headers,
            json={"actor_id": 1}
            )
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # test delete movie success,
    # should return 200 http status code,
    # succes boolean and the id of the movie just deleted
    def test_delete_movie_success(self):
        res = self.client().delete('/movies/4', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie'], 4)

    # test delete movie failure if movie not exist,
    # should return 404 http status code, succes boolean false
    def test_delete_movie_failure_not_exist(self):
        res = self.client().delete('/movies/4444', headers=self.headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
