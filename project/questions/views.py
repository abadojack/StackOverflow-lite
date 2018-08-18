from flask import jsonify, Blueprint, request
import json

# configure blueprint
stackoverflow = Blueprint('stackoverflow', __name__)


@stackoverflow.errorhandler(404)
def request_not_found():
    return jsonify({'error': 'Request not found'}), 404


@stackoverflow.route('/questions', methods=['GET'])
def get_questions():
    return jsonify(questions)


@stackoverflow.route('/questions/<int:question_id>', methods=['GET'])
def get_question(question_id):
    if request.method == 'GET':
        if question_id in questions.keys():
            return jsonify(questions[question_id])
        else:
            return request_not_found()


@stackoverflow.route('/questions', methods=['POST'])
def add_question():
    if request.method == 'POST':
        question = json.loads(request.data)['question']
        question_id = len(questions)
        questions[question_id] = {'text': question, 'answers': [], 'upvotes': 0, 'downvotes': 0}
        return jsonify({'response': 'question added successfully'}), 201


@stackoverflow.route('/questions/<int:question_id>/answers', methods=['POST'])
def add_answer(question_id):
    answer = json.loads(request.data)['answer']
    questions[question_id]['answers'].append(answer)
    return jsonify({'response': 'answer added successfully'}), 201


questions = {
    0: {
     'text': 'What is the answer to life, the universe and everything?',
     'answers': ['42'],
     'upvotes': 42,
     'downvotes': 0
    },
    1: {
     'text': 'Why are there so many JavaScript frameworks ?',
     'answers': ['Humans are insatiable', 'Each has a specific functions'],
     'upvotes': 10,
     'downvotes': 3
    },
    2: {
     'text': 'Alexa or Siri ?',
     'answers': ['Alexa, Siri is horrible', 'I\'m an Apple fanboy so Siri', 'Are you trying to start a war?'],
     'upvotes': 420,
     'downvotes': 56
    }
}
