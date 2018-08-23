import json
import uuid
import psycopg2
from datetime import datetime, timedelta
import jwt
from flask import jsonify, request
from validate_email import validate_email
from werkzeug.security import check_password_hash, generate_password_hash
from project.config import Config, conn
from . import users

try:
    cur = conn.cursor()
    cur.execute("ROLLBACK")
    conn.commit()

except Exception as e:
    print('connection exception ', e)
    cur = conn.cursor()
    cur.execute("ROLLBACK")


def auth_encode(uid):
    """Generate auth token"""
    try:
        payload = {
            'exp': datetime.now() + timedelta(hours=1),
            'iat': datetime.now(),
            'sub': uid
        }
        return jwt.encode(
            payload,
            Config.SECRET
        )
    except Exception as ex:
        raise ex


def auth_decode(token):
    """Decode auth token"""
    try:
        payload = jwt.decode(token, Config.SECRET)
        return payload['sub']
    except Exception as e:
        print('auth_token error', e)
        return None


def insert_token(token):
    """change the status of a request"""
    query = "INSERT INTO tokens (expired_tokens) VALUES ('%s');" % token
    cur.execute(query)
    conn.commit()


def get_token(token):
    """get token from db"""
    cur.execute('SELECT expired_tokens FROM tokens WHERE expired_tokens = "%s";' % token)
    token = cur.fetchone()
    return token


def get_user_id():
    """ get uid from token"""
    token = request.headers.get('token', None)
    uid = auth_decode(token)
    if not uid:
        return jsonify({}), 404
    return uid


@users.route('/auth/signup', methods=['POST'])
def signup():
    """sign up a new user"""
    username = json.loads(request.data)['username']
    password = json.loads(request.data)['password']
    email = json.loads(request.data)['email']

    try:
        if username == "":
            return jsonify({'response': 'username must not be empty'}), 409
        if email == "":
            return jsonify({'response': 'email must not be empty'}), 409
        if not validate_email(email):
            return jsonify({'response': 'email not valid'}), 409
        if password == "":
            return jsonify({'response': 'password must not be empty'}), 409
        if len(password) < 6:
            return jsonify({'response': 'password must be 6 characters or more'}), 409

        """
        search if the user exists in the database
        """
        user = User(username, email, "")
        if user.exists() is None:
            user.create_user(password)
            return jsonify({'response': 'user created successfully'}), 201
        else:
            return jsonify({'response': 'user already exists'}), 409

    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as e:
        print('error', e)
        return jsonify({'response': 'something went wrong'}), 400


@users.route('/auth/login', methods=['POST'])
def login():
    """
    login an existing user
    """
    username = json.loads(request.data)['username']
    password = json.loads(request.data)['password']
    user = User(username, "", "")

    try:
        user = user.exists()
        if check_password_hash(user.password_hash, password):
            """token if password is correct"""
            token = auth_encode(user.uid)
            if token:
                response = {'response': 'login successful', 'token': token.decode()}
                return jsonify(response), 200
        else:
            return jsonify({'response': 'enter correct user details'}), 409
    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as e:
        print('error in login', e)
        return jsonify({'response': 'user not found'}), 409


@users.route('/signout', methods=['GET'])
def signout():
    """sign out user """
    try:
        token = request.headers.get('token')
        insert_token(token) # insert token to expired db
        return jsonify({'response': 'signed out'})

    except Exception as ex:
        print('error', ex)
        return jsonify({'error': 'sign out error'}), 409


class User(object):
    def __init__(self, username, email, password_hash):
        self.uid = ''
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.time_created = datetime.now()

    def create_user(self, password):
        """Create user in db DONE"""
        password_hash = generate_password_hash(password)
        uid = uuid.uuid4()
        query = "INSERT INTO " \
                "users (id, username,email,password_hash,time_created)" \
                "VALUES('%s','%s', '%s', '%s', '%s')" % (uid, self.username, self.email, password_hash, self.time_created)
        cur.execute(query)
        conn.commit()

    def get_user(self, uid):
        """get user using uid"""
        cur.execute("SELECT * FROM users WHERE id = %s;" % uid)
        user = cur.fetchone()
        user_dict = {'id': user[0], 'username': user[1], 'email': user[2], 'password_hash': user[3],
                         'time_created': user[4]}
        print(user_dict, "userdict")
        return user_dict

    def exists(self):
        """check if user exists using"""
        cur.execute("SELECT * FROM users WHERE username = '%s';" % self.username)
        user = cur.fetchone()
        if user is None:
            return None
        else:
            self.uid = user[0]
            self.email = user[2]
            self.password_hash = user[3]
            self.time_created = user[4]
            return self

    def unpack(self):
        answer_dict = {}
        for answer in self.answers:
            answer_dict[answer.aid] = Answer.unpack(answer)

        question_dict = {}
        for question in self.questions:
            question_dict[question.qid] = Question.unpack(question)

        return {'uid': self.uid, 'username': self.username, 'email': self.email, 'time_created': self.time_created,
                'questions': question_dict, 'answers': answer_dict}


class Question(object):
    def __init__(self, title, body, uid):
        self.qid = ''
        self.title = title
        self.body = body
        self.uid = uid
        self.time_created = datetime.now()
        self.preferred_answer = ''

    def insert_question(self):
        """insert question to db"""
        query = "INSERT INTO questions (id, title, body, uid, time_created, preferred_answer)" \
                "VALUES (%s, %s, %s, %s, %s, %s)" % (self.qid, self.title, self.body, self.uid, self.time_created,
                                                     self.preferred_answer)
        cur.execute(query)
        conn.commit()

    def delete_question(self, qid):
        """delete question from db"""
        cur.execute("DELETE FROM questions WHERE qid=%s;" % qid)

    @staticmethod
    def get_all_questions():
        """get all questions in db"""
        cur.execute = "SELECT * FROM questions;"
        all_questions = cur.fetchall()
        questions_list = []
        for question in all_questions:
            # questions_list.append(question.__dict__)
            question_dict = {'qid': question[0], 'title': question[1], 'body': question[2],'uid': question[3],
                             'time_created': question[4], 'preferred_answer': question[5]}
            questions_list.append(question_dict)
        return questions_list

    def get_user_questions(self, uid):
        """get all questions by a user"""
        cur.execute("SELECT * FROM questions WHERE uid=%s;" % uid)
        all_questions = cur.fetchall()
        questions_list = []
        for question in all_questions:
            # questions_list.append(question.__dict__)
            question_dict = {'qid': question[0], 'title': question[1], 'body': question[2], 'uid': question[3],
                             'time_created': question[4], 'preferred_answer': question[5]}
            questions_list.append(question_dict)
        return questions_list

    def get_question(self, qid):
        """get specific question ffrom db"""
        cur.execute("SELECT * FROM questions WHERE id=%s;" % qid)
        question = cur.fetchone()
        question_dict = {'qid': question[0], 'title': question[1], 'body': question[2], 'uid': question[3],
                         'time_created': question[4], 'preferred_answer': question[5]}
        return question_dict

    def update_question(self, qid, title, body, uid, time_created, preferred_answer):
        cur.execute("UPDATE questions SET title=%s, body=%s, uid=%s, time_created=%s, preferred_answer=%s"
                    "WHERE id=%s;",
                    (title, body, uid, time_created, preferred_answer, qid))
        conn.commit()


    def add_answer(self, answer):
        self.answers.append(answer)

    def unpack(self):
        poster = User.unpack(self.poster)
        answer_dict = {}
        for answer in self.answers:
            answer_dict[answer.aid] = Answer.unpack(answer)
        return {'id': self.qid, 'title': self.title, 'body': self.body, 'time_created': self.time_created,
                'poster': poster, 'answers': answer_dict}


class Answer(object):
    def __init__(self, body, uid, qid):
        self.aid = ''
        self.body = body
        self.uid = uid
        self.qid = qid
        self.preferred = False
        self.time_created = datetime.now()

    def unpack(self):
        return {'id': self.aid, 'body': self.body, 'uid': self.uid, 'qid': self.qid,
                'preferred': self.preferred, 'time_created': self.time_created}

    def insert_answer(self):
        """insert answer to db"""
        query = "INSERT INTO answers (body, uid, qid, preferred, time_created)" \
                "VALUES (%s, %s, %s, %s, %s)" % (self.body, self.uid, self.qid, self.preferred, self.time_created)
        cur.execute(query)
        conn.commit()

    def delete_answer(self, aid):
            """delete answer from db"""
            cur.execute("DELETE FROM answers WHERE id=%s;" % aid)

    def get_question_answers(self, qid):
        """get answers for a particular question"""
        cur.execute("SELECT * FROM answers WHERE qid=%s" % qid)
        return cur.fetchall()

    def get_user_answers(self, uid):
        """get answers by a particular user"""
        cur.execute("SELECT * FROM answers WHERE uid=%s" % uid)
        return cur.fetchall()