import json
import uuid
from datetime import datetime, timedelta

import jwt
import psycopg2
from flask import jsonify, request
from validate_email import validate_email
from werkzeug.security import check_password_hash

from project.config import Config
from project.database import conn
from project.models.models import User
from . import users

try:
    cur = conn.cursor()
    cur.execute("ROLLBACK")
    conn.commit()

except Exception as e:
    print('connection exception ', e)
    cur = conn.cursor()
    cur.execute("ROLLBACK")


def auth_encode(user_id):
    """Generate auth token"""
    try:
        payload = {
            'exp': datetime.now() + timedelta(hours=1),
            'iat': datetime.now(),
            'sub': user_id
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
    query = "INSERT INTO tokens (id, expired_tokens) VALUES ('%s','%s');" % (uuid.uuid4(), token)
    cur.execute(query)
    conn.commit()


def get_token(token):
    """get token from db"""
    cur.execute("SELECT expired_tokens FROM tokens WHERE expired_tokens = '%s';" % token)
    token = cur.fetchone()
    return token


def get_user_id():
    """ get user_id from token"""
    token = request.headers.get('token', None)
    return auth_decode(token)


@users.route('/auth/signup', methods=['POST'])
def signup():
    """sign up a new user"""
    try:
        username = json.loads(request.data.decode())['username'].replace(" ", "")
        password = json.loads(request.data.decode())['password'].replace(" ", "")
        email = json.loads(request.data.decode())['email'].replace(" ", "")

        if username == "":
            return jsonify({'response': 'username must not be empty'}), 400
        if email == "":
            return jsonify({'response': 'email must not be empty'}), 400
        if not validate_email(email):
            return jsonify({'response': 'email not valid'}), 400
        if password == "":
            return jsonify({'response': 'password must not be empty'}), 400
        if len(password) < 6:
            return jsonify({'response': 'password must be 6 characters or more'}), 400

        """
        search if the user exists in the database
        """
        user = User(username, email, "")
        if user.exists() is None:
            user.create_user(password)
            return jsonify({'response': 'user created successfully'}), 201
        else:
            return jsonify({'response': 'user already exists'}), 409
    except KeyError as ex:
        print('response', ex)
        return jsonify({'response': 'json body must contain username, password and email'}), 500
    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as ex:
        print('error in signup', ex)
        return jsonify({'response': 'something went wrong'}), 500


@users.route('/auth/login', methods=['POST'])
def login():
    """
    login an existing user
    """
    try:
        username = json.loads(request.data.decode())['username'].replace(" ", "")
        password = json.loads(request.data.decode())['password'].replace(" ", "")
        user = User(username, "", "")

        user = user.exists()
        if check_password_hash(user.password_hash, password):
            """token if password is correct"""
            token = auth_encode(user.user_id)
            if token:
                response = {'response': 'login successful', 'token': token.decode()}
                return jsonify(response), 200
        else:
            return jsonify({'response': 'invalid username/password'}), 400
    except KeyError as ex:
        print('error in login', ex)
        return jsonify({'response': 'json body must contain username and password'}), 500
    except (psycopg2.DatabaseError, psycopg2.IntegrityError, Exception) as ex:
        print('error in login', ex)
        return jsonify({'response': 'user not found'}), 404


@users.route('/auth/signout', methods=['POST'])
def signout():
    """sign out user """
    try:
        token = request.headers.get('token')
        # insert token to expired db
        if get_token(token) is None:
            insert_token(token)
            return jsonify({'response': 'signed out'}), 200
        else:
            return jsonify({'response': 'Invalid token'}), 401
    except Exception as ex:
        print('response', ex)
        return jsonify({'response': 'something went wrong'}), 500
