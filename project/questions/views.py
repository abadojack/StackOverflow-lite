
from . import stackoverflow
from project.models.models import *


def token_is_expired():
    """check if token is valid"""
    token = request.headers.get('token', None)
    token_found = get_token(token)
    if token_found:
        return token_found


@stackoverflow.route('/questions', methods=['GET'])
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
                         {"title:"my title", "body":"body of question", "uid": "user34"},
                         {"title:"my title", "body":"body of question", "uid": "user34"}
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
                return jsonify({'response': 'It\'s empty here'}), 204
        else:
            return jsonify({'error': 'Invalid token, login again'}), 409
    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as ex:
        print('error', ex)
        return jsonify({'error': 'something went wrong'}), 500


@stackoverflow.route('/questions/<string:question_id>', methods=['GET'])
def get_question(question_id):
    try:
        if token_is_expired() is None:
            question = Question.get_question(question_id)
            if question:
                return jsonify({"question": question.__dict__}), 200
            else:
                return jsonify({"response": "question not found"}), 404
        else:
            return jsonify({'response': 'Invalid token, login again'}), 409
    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as ex:
        print('error', ex)
        return jsonify({'error': 'could not get requests'}), 500


@stackoverflow.route('/questions', methods=['POST'])
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
    if request.method == 'POST':
        try:
            title = json.loads(request.data)['title']
            body = json.loads(request.data)['body']

            uid = get_user_id()
            if uid:
                question = Question(title, body, uid)
                question.insert_question()
                return jsonify({'response': 'question posted successfully'}), 201
            else:
                return jsonify({'error': 'could not generate user id from token'}), 409
        except (psycopg2.DatabaseError, psycopg2.IntegrityError, KeyError, Exception) as ex:
            print('error', ex)
            return jsonify({'response': 'something went wrong'}), 500


@stackoverflow.route('/questions/<string:question_id>/answers', methods=['POST'])
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
    if request.method == 'POST':
        try:
            body = json.loads(request.data)['body']

            uid = get_user_id()
            if uid:
                answer = Answer(body, uid, question_id)
                answer.insert_answer()
                return jsonify({'response': 'answer posted successfully'}), 201
            else:
                return jsonify({'error': 'could not generate user id from token'}), 409
        except (psycopg2.DatabaseError, psycopg2.IntegrityError, KeyError, Exception) as ex:
            print('error', ex)
            return jsonify({'response': 'something went wrong'}), 500


@stackoverflow.route('/questions/<question_id>/answers/<answer_id>', methods=['PUT'])
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
    try:
        uid = get_user_id()
        if uid:
            answer = Answer.get_answer(answer_id)
            question = Question.get_question(question_id)

            if question.uid == uid:
                question.preferred_answer = answer_id
                question.update_question()
                answer.update_answer(answer.body, True)
                return jsonify({'response': 'preferred answer marked successfully'}), 200
            elif answer.uid == uid:
                body = json.loads(request.data)['body']
                answer.update_answer(body, answer.preferred)
                return jsonify({'response': 'answer updated successfully'}), 200
        else:
            return jsonify({'error': 'could not generate user id from token'}), 409
    except Exception as ex:
        print(ex)
        return jsonify({"response": "Something went wrong"}), 500


@stackoverflow.route('/questions/<question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        if token_is_expired() is None:
            Question.delete_question(question_id)
            return jsonify({"response": "request successfull"}), 200
        else:
            return jsonify({'response': 'Invalid token, login again'}), 409
    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as ex:
        print('error', ex)
        return jsonify({'error': 'something went wrong'}), 500
