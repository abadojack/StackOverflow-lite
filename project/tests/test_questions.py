import unittest
import json
from project import app
from project.config import create_tables, delete_tables


class TestQuestions(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app
        self.client = self.app.test_client

        # create db tables
        create_tables()

        # create user
        self.client().post('api/v1/auth/signup', data=json.dumps(
            dict(email='test@gmail.com', username='test', password='password')),
                           content_type='application/json')

        # login
        res_login = self.client().post('api/v1/auth/login', data=json.dumps(
            dict(username='test', password='password')),
                                       content_type='application/json')
        resp_data = json.loads(res_login.data.decode())
        token = resp_data['token']

        # add question
        self.client().post('api/v1/questions', data=json.dumps(
            dict(title='test title', body='some body of quiz')),
                           content_type='application/json',
                           headers=dict(token=token))

    def tearDown(self):
        delete_tables()

    def login(self):
        res_login = self.client().post('api/v1/auth/login', data=json.dumps(
            dict(username='test', password='password')),
                                       content_type='application/json')
        return json.loads(res_login.data.decode())["token"]

    def test_get_questions(self):
        res = self.client().get('/api/v1/questions', content_type='application/json', headers=dict(token=self.login()))
        resp_data = json.loads(res.data.decode())
        assert res.status_code == 200
        self.assertTrue(resp_data['questions'])

    def test_get_question_success(self):
        res = self.client().get('/api/v1/questions', headers=dict(token=self.login()))
        qid = json.loads(res.data.decode())['questions'][0]['qid']

        resp = self.client().get('/api/v1/questions/%s' % qid, headers=dict(token=self.login()))
        assert resp.status_code == 200
        resp_data = json.loads(resp.data)
        self.assertTrue(resp_data["question"])

    def test_get_question_not_found(self):
        resp = self.client().get('/api/v1/questions/30')
        assert resp.status_code == 404

    def test_add_question_user_not_found(self):
        resp = self.client().post('/api/v1/questions',
                                  headers=dict(token=''),
                                  data=json.dumps({'body': 'Is this the real life?', 'title': 'question'}))
        assert resp.status_code == 401

    def test_add_answer(self):
        res = self.client().get('/api/v1/questions', headers=dict(token=self.login()))
        qid = json.loads(res.data.decode())['questions'][0]['qid']

        resp = self.client().post('/api/v1/questions/' + qid + '/answers', data=json.dumps(
            dict(title='test title', body='some body of quiz')),
                                  content_type='application/json',
                                  headers=dict(token=self.login()))

        assert resp.status_code == 201
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'answer posted successfully')

    def test_add_answer_user_not_found(self):
        res = self.client().get('/api/v1/questions')
        qid = json.loads(res.data.decode())['questions'][0]['qid']

        resp = self.client().post('/api/v1/questions/' + qid + '/answers', data=json.dumps(
            dict(title='test title', body='some body of quiz')),
                                  content_type='application/json',
                                  headers=dict(token=''))

        assert resp.status_code == 401
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['error'], 'could not generate user id from token')


if __name__ == '__main__':
    unittest.main()
