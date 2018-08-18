import unittest
from project import app
import json
from project.questions.views import questions


class TestRequests(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app
        self.client = self.app.test_client

    def tearDown(self):
        pass

    def test_get_questions(self):
        resp = self.client().get('/api/v1/questions')
        assert resp.status_code == 200
        resp_data = json.loads(resp.data)
        assert resp_data['0']['answers'][0] == '42'
        assert resp_data['1']['downvotes'] == 3
        assert resp_data['2']['upvotes'] == 420

    def test_get_question(self):
        resp = self.client().get('/api/v1/questions/0')
        assert resp.status_code == 200
        resp_data = json.loads(resp.data)
        assert resp_data['text'] == 'What is the answer to life, the universe and everything?'

        resp = self.client().get('/api/v1/questions/30')
        assert resp.status_code == 404

    def test_add_question(self):
        resp = self.client().post('/api/v1/questions', data=json.dumps({'question': 'Is this the real life?'}))
        assert len(questions) == 4
        assert resp.status_code == 201

    def test_add_answer(self):
        resp = self.client().post('/api/v1/questions/0/answers', data=json.dumps({'answer': 'It is 42'}))
        assert len(questions[0]['answers']) == 2
        assert resp.status_code == 201


if __name__ == '__main__':
    unittest.main()
