import json

import psycopg2

from flask import request, jsonify

from project.users.views import get_token, get_user_id
from . import questions
from project.models.models import *


def token_is_expired():
    """check if token is valid"""
    token = request.headers.get('token', None)

    # try getting user_id from token
    if get_user_id() is None:
        return 'Invalid token'
    else:
        # check if token is expired
        token_found = get_token(token)
        if token_found:
            return token_found


@questions.app_errorhandler(404)
def not_found(error):
    return jsonify({'response': 'Not found'}), 404


@questions.app_errorhandler(405)
def not_found(error):
    return jsonify({'response': 'Method not found'}), 405


@questions.route('/questions', methods=['GET'])
def get_questions():
    """
    get:
        summary: Get questions endpoint.
        description: Fetch all questions.
        headers:
                token: <auth-token>
        responses:
            200:
                description: a list of questions.
                schema: {"questions":
                     [
                         {"title:"my title", "body":"body of question", "user_id": "user34"},
                         {"title:"my title", "body":"body of question", "user_id": "user34"}
                     ]
                 }
            204:
                description: returned if there are no questions.
                schema: {"response": "It's empty here"}
            409:
                description: returned if token used is invalid.
                schema: {"error": "invalid token ..."}
            500:
                description: Internal server error.
                schema: {"error": "something went wrong ..."}
    """
    try:
        if token_is_expired() is None:
            questions = Question.get_all_questions()
            if questions:
                return jsonify({'questions': questions}), 200
            else:
                return jsonify({}), 204
        else:
            return jsonify({'response': 'Invalid token'}), 401
    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as ex:
        print('response', ex)
        return jsonify({'response': 'something went wrong'}), 500


@questions.route('/questions/<string:question_id>', methods=['GET'])
def get_question(question_id):
    try:
        if token_is_expired() is None:
            question = Question.get_question(question_id)
            if question:
                return jsonify({"question": question.__dict__}), 200
            else:
                return jsonify({"response": "question not found"}), 404
        else:
            return jsonify({'response': 'Invalid token'}), 401
    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as ex:
        print('response', ex)
        return jsonify({'response': 'could not get requests'}), 500


@questions.route('/questions', methods=['POST'])
def add_question():
    """
        post:
            summary: post a question endpoint.
            description: add a question.
            headers:
                token: <auth-token>
            body:
                {"title": "question title", "body": "question body"}
            responses:
                201:
                    description: question posted successfully.
                    schema: {"response": "question posted successfully"}
                409:
                    description: returned if token used is invalid.
                    schema: {"error": "invalid token ..."}
                500:
                    description: Internal server error.
                    schema: {"error": "something went wrong ..."}
        """
    if token_is_expired() is None:
        try:
            title = json.loads(request.data)['title']
            body = json.loads(request.data)['body']

            user_id = get_user_id()
            if user_id:
                question = Question(title, body, user_id)
                if question.insert_question():
                    return jsonify({'response': 'question posted successfully'}), 201
                else:
                    return jsonify({'response': 'question with same title already exists'}), 409
            else:
                return jsonify({'response': 'could not generate user id from token'}), 401
        except (psycopg2.DatabaseError, psycopg2.IntegrityError, KeyError, Exception) as ex:
            print('response', ex)
            return jsonify({'response': 'something went wrong'}), 500
    return jsonify({'response': 'Invalid token'}), 401


@questions.route('/questions/<string:question_id>/answers', methods=['POST'])
def add_answer(question_id):
    """
            post:
                summary: post answer endpoint.
                description: add an answer to a question.
                parameters:
                    - name: question_id
                      in: path
                      description: ID of the question to add answer to
                      type: string
                      required: true
                headers:
                    token: <auth-token>
                body:
                    {"body": "answer body"}
                responses:
                    201:
                        description: answer posted successfully.
                        schema: {"response": "answer posted successfully"}
                    409:
                        description: returned if token used is invalid.
                        schema: {"error": "invalid token ..."}
                    500:
                        description: Internal server error.
                        schema: {"error": "something went wrong ..."}
            """
    if token_is_expired() is None:
        try:
            body = json.loads(request.data)['body']

            user_id = get_user_id()
            if user_id:
                answer = Answer(body, user_id, question_id)
                status = answer.insert_answer()
                if status == 'success':
                    return jsonify({'response': 'answer posted successfully'}), 201
                elif status == 'question not found':
                    return jsonify({"response": "question not found"}), 404
                elif status == 'duplicated':
                    return jsonify({"response": "answer already exists"}), 409
                else:
                    return jsonify({"response": status}), 500
            else:
                return jsonify({'response': 'could not generate user id from token'}), 401
        except (psycopg2.DatabaseError, psycopg2.IntegrityError, KeyError, Exception) as ex:
            print('response', ex)
            return jsonify({'response': 'something went wrong'}), 500
    return jsonify({'response': 'Invalid token'}), 401


@questions.route('/questions/<question_id>/answers/<answer_id>', methods=['PUT'])
def update_answer(question_id, answer_id):
    """
                put:
                    summary: edit answer.
                    description: Mark an answer as accepted or update an answer.
                    parameters:
                        - name: question_id
                          in: path
                          description: ID of the question which the answer belongs to
                          type: string
                          required: true
                        - name: answer_id
                          in: path
                          description: ID of the answer to update
                          type: string
                          required: true
                    headers:
                        token: <auth-token>
                    body:
                        {"body": "answer body"}
                    responses:
                        201:
                            description: answer updated successfully or preferred answer marked successfully.
                            schema: {"response": "..."}
                        409:
                            description: returned if token used is invalid.
                            schema: {"error": "invalid token ..."}
                        500:
                            description: Internal server error.
                            schema: {"error": "something went wrong ..."}
                """
    if token_is_expired() is None:
        try:
            user_id = get_user_id()
            if user_id:
                answer = Answer.get_answer(answer_id)
                question = Question.get_question(question_id)

                if question.user_id == user_id:
                    question.preferred_answer = answer_id
                    question.update_question()
                    answer.update_answer(answer.body, True)
                    return jsonify({'response': 'preferred answer marked successfully'}), 200
                elif answer.user_id == user_id:
                    body = json.loads(request.data)['body']
                    answer.update_answer(body, answer.preferred)
                    return jsonify({'response': 'answer updated successfully'}), 200
            else:
                return jsonify({'response': 'could not generate user id from token'}), 401
        except Exception as ex:
            print(ex)
            return jsonify({"response": "Something went wrong"}), 500
    return jsonify({'response': 'Invalid token'}), 401


@questions.route('/questions/<question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        if token_is_expired() is None:
            if Question.delete_question(question_id):
                return jsonify({"response": "question deleted successfully"}), 200
            else:
                return jsonify({"response": "question not found"}), 404
        else:
            return jsonify({'response': 'Invalid token'}), 401
    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as ex:
        print('response', ex)
        return jsonify({'response': 'something went wrong'}), 500
