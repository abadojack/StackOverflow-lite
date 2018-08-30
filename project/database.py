import psycopg2
from .config import Config

try:
    #conn = psycopg2.connect("dbname=%s host=%s user=%s password=%s" % (Config.DATABASE_NAME,
    #                                                                  Config.DATABASE_HOST,
    #                                                                  Config.DATABASE_USER,
    #                                                                  Config.DATABASE_PASSWORD))
    # conn = psycopg2.connect("dbname=dtf1o3dihcmjh host=ec2-50-17-194-129.compute-1.amazonaws.com user=sclbsmrebwfsnt password=010cef844685c852fc51be3afe0e72d3220154a228f00bf1ec6a27cd03caa3a4")
    # conn = psycopg2.connect("dbname=stackoverflow1 host=localhost user=abadojack password=''")
    conn = psycopg2.connect("dbname=stackoverflow1 host=localhost user=postgres password=''")
    # conn = psycopg2.connect("dbname=dc8m25uqlnpb2n host=ec2-50-16-196-57.compute-1.amazonaws.com user=tyhuqknsihddcw password=63a38bce0f36449d6b23fc3a142570066bdbfb961b819805dd93132307fbbfdd")
except Exception as e:
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
                    "user_id VARCHAR(256), time_created TIMESTAMP, preferred_answer VARCHAR(256));"

        # create table answers
        answers = "CREATE TABLE answers(id VARCHAR(256) PRIMARY KEY, body TEXT," \
                  "user_id VARCHAR(256), question_id VARCHAR(256), preferred BOOLEAN DEFAULT FALSE, time_created TIMESTAMP);"

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
