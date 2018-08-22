from flask import jsonify, request
import json
from . import stackoverflow
from project.models.models import questions, Question, users, Answer


@stackoverflow.errorhandler(404)
def not_found(value='Request'):
    return jsonify({'error': value + ' not found'}), 404


@stackoverflow.route('/questions', methods=['GET'])
def get_questions():
    question_dict = {}
    for question in questions:
        question_dict[question.qid] = question.unpack()
    return jsonify(question_dict)


@stackoverflow.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    if request.method == 'GET':
        try:
            return jsonify(questions[question_id].unpack())
        except IndexError:
            return not_found('question ' + str(question_id))


@stackoverflow.route('/questions', methods=['POST'])
def add_question():
    if request.method == 'POST':
        question_title = json.loads(request.data)['title']
        question_body = json.loads(request.data)['body']
        username = json.loads(request.data)['username']

        for user in users:
            if user.username == username:
                questions.append(Question(len(questions), question_title, question_body, user))
                return jsonify({'response': 'question added successfully'}), 201

        return not_found('user ' + username)


@stackoverflow.route('/questions/<int:question_id>/answers', methods=['POST'])
def add_answer(question_id):
    body = json.loads(request.data)['body']
    username = json.loads(request.data)['username']

    for user in users:
        if user.username == username:
            try:
                aid = len(questions[question_id].answers)
                questions[question_id].add_answer(Answer(aid, body, user))
                return jsonify({'response': 'answer added successfully'}), 201
            except IndexError:
                return not_found('question ' + str(question_id))
    return not_found('user ' + username)
