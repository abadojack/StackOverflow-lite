import uuid
from datetime import datetime

from werkzeug.security import generate_password_hash

from project.database import conn

try:
    cur = conn.cursor()
    cur.execute("ROLLBACK")
    conn.commit()

except Exception as e:
    print('connection exception ', e)
    cur = conn.cursor()
    cur.execute("ROLLBACK")


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
                "VALUES('%s','%s', '%s', '%s', '%s')" % (
                uid, self.username, self.email, password_hash, self.time_created)
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
        self.qid = uuid.uuid4()

        # question titles should not be the same
        if self.get_question_title(self.title) is None:
            query = "INSERT INTO questions (id, title, body, uid, time_created, preferred_answer)" \
                    "VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (self.qid, self.title, self.body, self.uid,
                                                                     self.time_created, self.preferred_answer)
            cur.execute(query)
            conn.commit()
            return True
        else:
            return False

    @staticmethod
    def delete_question(qid):
        """delete question from db"""
        if Question.get_question(qid) is not None:
            cur.execute("DELETE FROM questions WHERE id='%s';" % qid)
            return True
        else:
            return False

    @staticmethod
    def get_all_questions():
        """get all questions in db"""
        cur.execute("SELECT * FROM questions;")
        all_questions = cur.fetchall()
        questions_list = []
        for question in all_questions:
            # questions_list.append(question.__dict__)
            question_dict = {'qid': question[0], 'title': question[1], 'body': question[2], 'uid': question[3],
                             'time_created': question[4], 'preferred_answer': question[5]}
            questions_list.append(question_dict)
        return questions_list

    @staticmethod
    def get_user_questions(uid):
        """get all questions by a user"""
        cur.execute("SELECT * FROM questions WHERE uid=%s;" % uid)
        all_questions = cur.fetchall()
        questions_list = []
        for question in all_questions:
            question_dict = {'qid': question[0], 'title': question[1], 'body': question[2], 'uid': question[3],
                             'time_created': question[4], 'preferred_answer': question[5]}
            questions_list.append(question_dict)
        return questions_list

    @staticmethod
    def get_question(qid):
        """get specific question from db using id"""
        cur.execute("SELECT * FROM questions WHERE id = '%s';" % qid)
        question = cur.fetchone()
        if question is not None:
            quiz = Question(question[1], question[2], question[3])
            quiz.qid = qid
            quiz.time_created = question[4]
            quiz.preferred_answer = question[5]
            return quiz
        return None

    @staticmethod
    def get_question_title(title):
        """get specific question from db using title"""
        cur.execute("SELECT * FROM questions WHERE title = '%s';" % title)
        question = cur.fetchone()
        if question is not None:
            quiz = Question(question[1], question[2], question[3])
            quiz.qid = question[0]
            quiz.time_created = question[4]
            quiz.preferred_answer = question[5]
            return quiz
        return None

    def update_question(self):
        cur.execute("UPDATE questions SET title=%s, body=%s, uid=%s, time_created=%s, preferred_answer=%s"
                    "WHERE id=%s;",
                    (self.title, self.body, self.uid, self.time_created, self.preferred_answer, self.qid))
        conn.commit()


class Answer(object):
    def __init__(self, body, uid, qid):
        self.aid = ''
        self.body = body
        self.uid = uid
        self.qid = qid
        self.preferred = False
        self.time_created = datetime.now()

    def insert_answer(self):
        """insert answer to db"""
        aid = uuid.uuid4()
        query = "INSERT INTO answers(id, body, uid, qid, preferred, time_created)" \
                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (aid, self.body, self.uid, self.qid, self.preferred,
                                                                 self.time_created)
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

    @staticmethod
    def get_answer(aid):
        """get answer using answer id"""
        cur.execute("SELECT * FROM answers WHERE id = '%s';" % aid)
        answer = cur.fetchone()
        if answer is None:
            return None
        else:
            body = answer[1]
            uid = answer[2]
            qid = answer[3]

            ans = Answer(body, uid, qid)
            ans.aid = aid
            ans.time_created = answer[5]
            ans.preferred = answer[4]

            return ans

    def update_answer(self, body, preferred):
        cur.execute("UPDATE answers SET body='%s', preferred='%s' WHERE id='%s';" % (body, preferred, self.aid))
        conn.commit()
