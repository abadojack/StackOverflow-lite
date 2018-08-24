import unittest
import json
from project import app
from project.config import conn


class TestRequests(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app
        self.client = self.app.test_client

        # create user
        res = self.client().post('api/v1/auth/signup', data=json.dumps(
                                          dict(email='test@gmail.com', username='test', password='password')),
                                 content_type='application/json')
        resp_data = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.content_type, 'application/json')
        self.assertEqual(resp_data['response'], 'user created successfully')

        # login
        res_login = self.client().post('api/v1/auth/login', data=json.dumps(
                                          dict(username='test', password='password')),
                                 content_type='application/json')
        resp_data = json.loads(res_login.data.decode())
        self.assertTrue(resp_data['token'])
        self.assertEqual(res_login.status_code, 200)
        self.assertEqual(res_login.content_type, 'application/json')
        self.assertEqual(resp_data['response'], 'login successful')
        token = resp_data['token']

        # add question
        res_add_question = self.client().post('api/v1/questions', data=json.dumps(
                                              dict(title='test title', body='some body of quiz')),
                                              content_type='application/json',
                                              headers=dict(token=token))
        resp_data = json.loads(res_add_question.data.decode())
        self.assertEqual(res_add_question.status_code, 201)
        self.assertEqual(resp_data['response'], 'question posted successfully')

    def tearDown(self):
        cur = conn.cursor()
        cur.execute("DELETE from users;")
        cur.execute("DELETE from questions;")
        cur.execute("DELETE from answers;")
        cur.execute("DELETE from tokens;")
        conn.commit()

    def test_get_questions(self):
        res = self.client().get('/api/v1/questions')
        resp_data = json.loads(res.data.decode())
        assert res.status_code == 200
        self.assertTrue(resp_data['questions'])

    def test_get_question_success(self):
        res = self.client().get('/api/v1/questions')
        qid = json.loads(res.data.decode())['questions'][0]['qid']

        resp = self.client().get('/api/v1/questions/%s' % qid)
        assert resp.status_code == 200
        resp_data = json.loads(resp.data)
        self.assertTrue(resp_data["question"])

    def test_get_question_not_found(self):
        resp = self.client().get('/api/v1/questions/30')
        assert resp.status_code == 404

    def test_add_question_user_not_found(self):
        resp = self.client().post('/api/v1/questions',
                                  data=json.dumps({'body': 'Is this the real life?', 'title': 'question'}))
        assert resp.status_code == 409

    def test_add_answer(self):
        res_login = self.client().post('api/v1/auth/login', data=json.dumps(
            dict(username='test', password='password')),
                                       content_type='application/json')
        resp_data = json.loads(res_login.data.decode())
        token = resp_data['token']

        res = self.client().get('/api/v1/questions')
        qid = json.loads(res.data.decode())['questions'][0]['qid']

        resp = self.client().post('/api/v1/questions/' + qid + '/answers', data=json.dumps(
                                              dict(title='test title', body='some body of quiz')),
                                              content_type='application/json',
                                              headers=dict(token=token))

        assert resp.status_code == 201
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'answer posted successfully')

    def test_add_answer_user_not_found(self):
        res_login = self.client().post('api/v1/auth/login', data=json.dumps(
            dict(username='test', password='password')),
                                       content_type='application/json')
        resp_data = json.loads(res_login.data.decode())
        token = resp_data['token']

        res = self.client().get('/api/v1/questions')
        qid = json.loads(res.data.decode())['questions'][0]['qid']

        resp = self.client().post('/api/v1/questions/' + qid + '/answers', data=json.dumps(
            dict(title='test title', body='some body of quiz')),
                                  content_type='application/json',
                                  headers=dict(token=''))

        assert resp.status_code == 409
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['error'], 'could not generate user id from token')


if __name__ == '__main__':
    unittest.main()
