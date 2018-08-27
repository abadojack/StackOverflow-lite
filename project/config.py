import os
import psycopg2

base_dir = os.path.abspath(os.path.dirname(__file__))

try:
    conn = psycopg2.connect("dbname=stackoverflow host=localhost user=abadojack password=''")
except Exception as e:
    print("connect to database failed ", e)


def create_tables():
    cur = conn.cursor()
    try:
        # delete tables if they exist
        cur.execute("DROP TABLE IF EXISTS questions,answers, users;")
        cur.execute("DROP TABLE IF EXISTS tokens;")

        # create table users
        users = "CREATE TABLE users(id VARCHAR(256) PRIMARY KEY, username VARCHAR(64) UNIQUE , email VARCHAR(64) UNIQUE," \
                "password_hash VARCHAR(256),time_created TIMESTAMP );"

        # create table questions
        questions = "CREATE TABLE questions(id VARCHAR(256) PRIMARY KEY, title VARCHAR(256), body TEXT," \
                    "uid VARCHAR(256), time_created TIMESTAMP, preferred_answer VARCHAR(256));"

        # create table answers
        answers = "CREATE TABLE answers(id VARCHAR(256) PRIMARY KEY, body TEXT," \
                  "uid VARCHAR(256), qid VARCHAR(256), preferred BOOLEAN DEFAULT FALSE, time_created TIMESTAMP);"

        # create table tokens
        tokens = "CREATE TABLE tokens(id VARCHAR(256) PRIMARY KEY, expired_tokens VARCHAR(256));"

        cur.execute(users)
        cur.execute(questions)
        cur.execute(answers)
        cur.execute(tokens)

        conn.commit()
    except Exception as ex:
        print('error in migration', ex)


def delete_tables():
    cur = conn.cursor()
    cur.execute("DELETE from users;")
    cur.execute("DELETE from questions;")
    cur.execute("DELETE from answers;")
    cur.execute("DELETE from tokens;")
    conn.commit()


# Base configuration
class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('STACKOVERFLOW_SECRET', 'KeepYourSecretsToYourself')


# Dev configuration
class DevConfig(Config):
    DEBUG = True


# Test configuration
class TestConfig(Config):
    TESTING = True
    DEBUG = True


# Staging configuration
class StagingConfig(Config):
    DEBUG = True


# Production configuration
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
