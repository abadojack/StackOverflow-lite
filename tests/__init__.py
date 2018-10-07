import json
import unittest

from project import app
from project.database import create_tables, delete_tables


class BaseTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app
        self.client = self.app.test_client

        # create db tables
        create_tables()

        # create user 0
        self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='cis@gmail.com', username='cis', password='password')),
                           content_type='application/json')

        # create user 1
        self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='cis1@gmail.com', username='cis1', password='password')),
                           content_type='application/json')

        # add question
        self.client().post('api/v1/questions', data=json.dumps(
            dict(title='test title', body='some body of quiz')),
                           content_type='application/json',
                           headers=dict(token=self.login_user_0()))

    def login_user_0(self):
        res_login = self.client().post('api/v1/auth/login', data=json.dumps(
            dict(username='cis', password='password')),
                                       content_type='application/json')
        return json.loads(res_login.data.decode())["token"]

    def login_user_1(self):
        res_login = self.client().post('api/v1/auth/login', data=json.dumps(
            dict(username='cis1', password='password')),
                                       content_type='application/json')
        return json.loads(res_login.data.decode())["token"]

    def tearDown(self):
        delete_tables()
