import json

from project.models.models import Question, Answer
from project.users.views import auth_decode
from . import BaseTest


class TestQuestions(BaseTest):

    def test_get_questions(self):
        res = self.client().get('/api/v1/questions', content_type='application/json', headers=dict(token=self.login()))
        resp_data = json.loads(res.data.decode())
        assert res.status_code == 200
        self.assertTrue(resp_data['questions'])

    def test_get_questions_no_token(self):
        res = self.client().get('/api/v1/questions', content_type='application/json', headers=dict(token='1'))
        resp_data = json.loads(res.data.decode())
        assert res.status_code == 401
        self.assertTrue(resp_data['response'] == 'Invalid token')

    def test_get_question_success(self):
        res = self.client().get('/api/v1/questions', headers=dict(token=self.login()))
        question_id = json.loads(res.data.decode())['questions'][0]['question_id']

        resp = self.client().get('/api/v1/questions/%s' % question_id, headers=dict(token=self.login()))
        assert resp.status_code == 200
        resp_data = json.loads(resp.data)
        self.assertTrue(resp_data["question"])

    def test_get_question_invalid_token(self):
        res = self.client().get('/api/v1/questions/1', headers=dict(token=''))

        assert res.status_code == 401

    def test_get_question_not_found(self):
        resp = self.client().get('/api/v1/questions/30', headers=dict(token=self.login()))
        assert resp.status_code == 404

    def test_add_question_empty_title(self):
        resp = self.client().post('/api/v1/questions',
                                  headers=dict(token=self.login()),
                                  data=json.dumps({'body': 'Is this the real life?', 'title': ''}))
        assert resp.status_code == 400

    def test_add_question_empty_body(self):
        resp = self.client().post('/api/v1/questions',
                                  headers=dict(token=self.login()),
                                  data=json.dumps({'body': '', 'title': 'life'}))
        assert resp.status_code == 400

    def test_add_question_same_title(self):
        question = Question('unique title', 'question 10 body', 1)
        question.insert_question()

        resp = self.client().post('/api/v1/questions',
                                  headers=dict(token=self.login()),
                                  data=json.dumps({'body': 'body is here', 'title': 'unique title'}))
        assert resp.status_code == 409

    def test_add_question_user_empty_token(self):
        resp = self.client().post('/api/v1/questions',
                                  headers=dict(token=''),
                                  data=json.dumps({'body': 'Is this the real life?', 'title': 'question'}))
        assert resp.status_code == 401

    def test_add_answer(self):
        question = Question('question add answer', 'question 10 body', 1)
        question.insert_question()

        resp = self.client().post('/api/v1/questions/' + question.question_id.__str__() + '/answers', data=json.dumps(
            dict(title='test title', body='some body of quiz')),
                                  content_type='application/json',
                                  headers=dict(token=self.login()))

        assert resp.status_code == 201
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'answer posted successfully')

    def test_add_answer_duplicate(self):
        question = Question('question add answer another one', 'question 10 body', 1)
        question.insert_question()

        Answer('duplicate', 1, question.question_id).insert_answer()

        resp = self.client().post('/api/v1/questions/' + question.question_id.__str__() + '/answers', data=json.dumps(
            dict(body='duplicate')),
                                  content_type='application/json',
                                  headers=dict(token=self.login()))

        assert resp.status_code == 409

    def test_add_answer_invalid_token(self):
        res = self.client().get('/api/v1/questions', headers=dict(token=self.login()))
        question_id = json.loads(res.data.decode())['questions'][0]['question_id']

        resp = self.client().post('/api/v1/questions/' + question_id + '/answers', data=json.dumps(
            dict(title='test title', body='some body of quiz')),
                                  content_type='application/json',
                                  headers=dict(token=''))

        assert resp.status_code == 401
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'Invalid token')

    def test_add_answer_question_not_found(self):
        resp = self.client().post('/api/v1/questions/1/answers', data=json.dumps(
            dict(title='test title 1 not found', body='some body of quiz')),
                                  content_type='application/json',
                                  headers=dict(token=self.login()))

        assert resp.status_code == 404

    def test_delete_question(self):
        question = Question('question delete title', 'question 10 body', 1)
        question.insert_question()

        Answer('answer delete title', 1, question.question_id).insert_answer()

        resp = self.client().delete('api/v1/questions/' + question.question_id.__str__(),
                                    content_type='application/json',
                                    headers=dict(token=self.login()))
        assert resp.status_code == 200
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'question deleted successfully')

    def test_delete_question_invalid_token(self):
        resp = self.client().delete('api/v1/questions/1',
                                    content_type='application/json',
                                    headers=dict(token=''))
        assert resp.status_code == 401

    def test_delete_question_not_found(self):
        resp = self.client().delete('api/v1/questions/1',
                                    content_type='application/json',
                                    headers=dict(token=self.login()))
        assert resp.status_code == 404

    def test_get_popular_question(self):
        question = Question('question 10 title', 'question 10 body', 1)
        question.insert_question()

        Answer('answer 10 title', 1, question.question_id).insert_answer()
        Answer('answer 101 title', 1, question.question_id).insert_answer()
        Answer('answer 102 title', 1, question.question_id).insert_answer()
        Answer('answer 103 title', 1, question.question_id).insert_answer()

        res = self.client().get('api/v1/questions/popular', content_type='application/json',
                                headers=dict(token=self.login()))

        assert res.status_code == 200

        resp_data = json.loads(res.data.decode())

        assert resp_data['question']

    def test_get_popular_question_invalid_token(self):
        res = self.client().get('api/v1/questions/popular', content_type='application/json',
                                headers=dict(token=''))

        assert res.status_code == 401

    def test_update_answer_body(self):
        question = Question('update answer', 'question 10 body', 1)
        question.insert_question()

        token = self.login()
        user_id = auth_decode(token)
        answer = Answer('update answer', user_id, question.question_id)
        answer.insert_answer()

        resp = self.client().put('/api/v1/questions/' + question.question_id.__str__() + '/answers/' +
                                 answer.answer_id.__str__(), data=json.dumps(
            dict(body='newly updated answer')),
                                 content_type='application/json',
                                 headers=dict(token=token))

        assert resp.status_code == 200
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'answer updated successfully')

    def test_update_answer_body_invalid_json(self):
        question = Question('update answer 1', 'question 10 body', 1)
        question.insert_question()

        token = self.login()
        user_id = auth_decode(token)
        answer = Answer('update answer 1', user_id, question.question_id)
        answer.insert_answer()

        resp = self.client().put('/api/v1/questions/' + question.question_id.__str__() + '/answers/' +
                                 answer.answer_id.__str__(), data=json.dumps(
            dict(bod='newly updated answer')),
                                 content_type='application/json',
                                 headers=dict(token=token))

        assert resp.status_code == 400
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'Invalid json')

    def test_update_answer_body_invalid_token(self):
        question = Question('update answer 2', 'question 10 body', 1)
        question.insert_question()

        token = self.login()
        user_id = auth_decode(token)
        answer = Answer('update answer 2', user_id, question.question_id)
        answer.insert_answer()

        resp = self.client().put('/api/v1/questions/' + question.question_id.__str__() + '/answers/' +
                                 answer.answer_id.__str__(), data=json.dumps(
            dict(bod='newly updated answer')),
                                 content_type='application/json',
                                 headers=dict(token=''))

        assert resp.status_code == 401
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'Invalid token')

    def test_update_answer_body_mark_as_preferred(self):
        token = self.login()
        user_id = auth_decode(token)
        question = Question('update answer preferred', 'question 10 body', user_id)
        question.insert_question()

        answer = Answer('update answer preferred', 1, question.question_id)
        answer.insert_answer()

        resp = self.client().put('/api/v1/questions/' + question.question_id.__str__() + '/answers/' +
                                 answer.answer_id.__str__(),
                                 content_type='application/json',
                                 headers=dict(token=token))

        assert resp.status_code == 200
        resp_data = json.loads(resp.data.decode())
        self.assertEqual(resp_data['response'], 'preferred answer marked successfully')

    def test_endpoint_not_found(self):
        resp = self.client().get('/api/v1/questions/answers/',
                                 content_type='application/json',
                                 headers=dict(token=''))

        resp.status_code = 404

    def test_endpoint_not_found(self):
        resp = self.client().patch('/api/v1/questions/answers/',
                                   content_type='application/json',
                                   headers=dict(token=''))

        resp.status_code = 405
