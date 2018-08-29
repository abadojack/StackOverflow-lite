import json
from . import BaseTest


class TestUsers(BaseTest):
    def test_sign_up_success(self):
        res = self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='test@gmail.com', username='test', password='password')),
                                 content_type='application/json')
        resp_data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(resp_data['response'], 'user created successfully')

    def test_sign_up_empty_email(self):
        res = self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='', username='test', password='password')),
                                 content_type='application/json')
        resp_data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(resp_data['response'], 'email must not be empty')

    def test_sign_up_invalid_email(self):
        res = self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='mail', username='test', password='password')),
                                 content_type='application/json')
        resp_data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(resp_data['response'], 'email not valid')

    def test_sign_up_no_email(self):
        res = self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(username='test', password='password')),
                                 content_type='application/json')
        resp_data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 500)
        self.assertEqual(resp_data['response'], 'json body must contain username, password and email')

    def test_sign_up_empty_username(self):
        res = self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='test@gmail.com', username='', password='password')),
                                 content_type='application/json')
        resp_data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(resp_data['response'], 'username must not be empty')

    def test_sign_up_empty_username(self):
        res = self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='test@gmail.com', username='test', password='')),
                                 content_type='application/json')
        resp_data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 400)
        self.assertEqual(resp_data['response'], 'password must not be empty')

    def test_login_success(self):
        # sign up new user
        self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='test@gmail.com', username='test', password='password')),
                           content_type='application/json')

        res_login = self.client().post('api/v1/auth/login', data=json.dumps(
            dict(username='test', password='password')),
                                       content_type='application/json')

        resp_data = json.loads(res_login.data.decode())
        self.assertTrue(resp_data['token'])
        self.assertEqual(res_login.status_code, 200)
        self.assertEqual(res_login.content_type, 'application/json')
        self.assertEqual(resp_data['response'], 'login successful')

    def test_sign_out_success(self):
        # sign up new user
        self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='test@gmail.com', username='test', password='password')),
                           content_type='application/json')

        # log in the user
        res_login = self.client().post('api/v1/auth/login', data=json.dumps(
            dict(username='test', password='password')),
                                       content_type='application/json')

        token = json.loads(res_login.data.decode())["token"]

        res = self.client().get('api/v1/auth/signout', content_type='application/json', headers=dict(token=token))

        resp_data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(resp_data['response'], 'signed out')
