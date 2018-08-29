import json
import unittest

from . import BaseTest


class TestQuestions(BaseTest):

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
        self.assertEqual(resp_data['response'], 'could not generate user id from token')

    def test_delete_question(self):
        self.client().post('api/v1/questions', data=json.dumps(
            dict(title='test title', body='some body of quiz')),
                           content_type='application/json',
                           headers=dict(token=self.login()))

        # add another question
        self.client().post('api/v1/questions', data=json.dumps(
            dict(title='test title 1', body='some body of quiz 1')),
                           content_type='application/json',
                           headers=dict(token=self.login()))

        res = self.client().get('/api/v1/questions', content_type='application/json',
                                headers=dict(token=self.login()))
        resp_data = json.loads(res.data.decode())

        qid = resp_data['questions'][1]['qid']

        resp = self.client().delete('api/v1/questions/' + qid, content_type='application/json',
                                    headers=dict(token=self.login()))
        assert resp.status_code == 200
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'question deleted successfully')


if __name__ == '__main__':
    unittest.main()
