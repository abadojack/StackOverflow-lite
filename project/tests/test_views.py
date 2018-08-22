import unittest
from project import app
import json
from project.models.models import questions


class TestRequests(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app
        self.client = self.app.test_client

    def tearDown(self):
        if len(questions) > 3:
            questions.pop(3)
        pass

    def test_get_questions(self):
        resp = self.client().get('/api/v1/questions')
        assert resp.status_code == 200

        resp_data = json.loads(resp.data)
        assert len(resp_data) == 3
        assert resp_data["0"]["poster"]["username"] == "starlord"

    def test_get_question_success(self):
        resp = self.client().get('/api/v1/questions/1')
        assert resp.status_code == 200
        resp_data = json.loads(resp.data)
        assert resp_data['body'] == 'Who is Gamora?'
        assert resp_data["poster"]["username"] == "ironman"

    def test_get_question_not_found(self):
        resp = self.client().get('/api/v1/questions/30')
        assert resp.status_code == 404

    def test_get_question_invalid_character(self):
        resp = self.client().get('/api/v1/questions/*')
        assert resp.status_code == 404

    def test_add_question(self):
        resp = self.client().post('/api/v1/questions',
                                  data=json.dumps({'body': 'Is this the real life?', 'title': 'reality',
                                                   'username': 'ironman'}))
        assert len(questions) == 4
        assert resp.status_code == 201

    def test_add_question_user_not_found(self):
        resp = self.client().post('/api/v1/questions',
                                  data=json.dumps({'body': 'Is this the real life?', 'title': 'reality',
                                                   'username': 'gamora'}))
        assert len(questions) == 3
        assert resp.status_code == 404

    def test_add_answer(self):
        resp = self.client().post('/api/v1/questions/0/answers', data=json.dumps({'body': 'It is 42',
                                                                                  'username': 'drax'}))
        answers = questions[0].__dict__['answers']
        assert len(answers) == 2
        assert answers[1].__dict__['poster'].__dict__['username'] == 'drax'
        assert resp.status_code == 201

    def test_add_answer_qid_not_found(self):
        resp = self.client().post('/api/v1/questions/10/answers', data=json.dumps({'body': 'It is 42',
                                                                                  'username': 'drax'}))
        assert resp.status_code == 404

    def test_add_answer_user_not_found(self):
        resp = self.client().post('/api/v1/questions/10/answers', data=json.dumps({'body': 'It is 42',
                                                                                  'username': 'gamora'}))
        assert resp.status_code == 404


if __name__ == '__main__':
    unittest.main()
