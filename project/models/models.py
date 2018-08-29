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
        self.user_id = ''
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.time_created = datetime.now()

    def create_user(self, password):
        """Create user in db DONE"""
        password_hash = generate_password_hash(password)
        user_id = uuid.uuid4()
        query = "INSERT INTO " \
                "users (id, username,email,password_hash,time_created)" \
                "VALUES('%s','%s', '%s', '%s', '%s')" % (
                user_id, self.username, self.email, password_hash, self.time_created)
        cur.execute(query)
        conn.commit()

    def get_user(self, user_id):
        """get user using user_id"""
        cur.execute("SELECT * FROM users WHERE id = %s;" % user_id)
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
            self.user_id = user[0]
            self.email = user[2]
            self.password_hash = user[3]
            self.time_created = user[4]
            return self


class Question(object):
    def __init__(self, title, body, user_id):
        self.question_id = ''
        self.title = title
        self.body = body
        self.user_id = user_id
        self.time_created = datetime.now()
        self.preferred_answer = ''
        self.answers = []

    def insert_question(self):
        """insert question to db"""
        self.question_id = uuid.uuid4()

        # question titles should not be the same
        if self.get_question_title(self.title) is None:
            query = "INSERT INTO questions (id, title, body, user_id, time_created, preferred_answer)" \
                    "VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (self.question_id, self.title, self.body, self.user_id,
                                                                     self.time_created, self.preferred_answer)
            cur.execute(query)
            conn.commit()
            return True
        else:
            return False

    @staticmethod
    def delete_question(question_id):
        """delete question from db"""
        if Question.get_question(question_id) is not None:
            cur.execute("DELETE FROM questions WHERE id='%s';" % question_id)
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
            answers = Answer.get_question_answers(question[0])
            question_dict = {'question_id': question[0], 'title': question[1], 'body': question[2], 'user_id': question[3],
                             'time_created': question[4], 'preferred_answer': question[5], "answers": answers}
            questions_list.append(question_dict)
        return questions_list

    @staticmethod
    def get_user_questions(user_id):
        """get all questions by a user"""
        cur.execute("SELECT * FROM questions WHERE user_id=%s;" % user_id)
        all_questions = cur.fetchall()
        questions_list = []
        for question in all_questions:
            answers = Answer.get_question_answers(question[0])
            question_dict = {'question_id': question[0], 'title': question[1], 'body': question[2], 'user_id': question[3],
                             'time_created': question[4], 'preferred_answer': question[5], "answers": answers}
            questions_list.append(question_dict)
        return questions_list

    @staticmethod
    def get_question(question_id):
        """get specific question from db using id"""
        cur.execute("SELECT * FROM questions WHERE id = '%s';" % question_id)
        question = cur.fetchone()
        if question is not None:
            answers = Answer.get_question_answers(question_id)
            quiz = Question(question[1], question[2], question[3])
            quiz.question_id = question_id
            quiz.time_created = question[4]
            quiz.preferred_answer = question[5]
            quiz.answers = answers
            return quiz
        return None

    @staticmethod
    def get_question_title(title):
        """get specific question from db using title"""
        cur.execute("SELECT * FROM questions WHERE title = '%s';" % title)
        question = cur.fetchone()
        if question is not None:
            quiz = Question(question[1], question[2], question[3])
            quiz.question_id = question[0]
            quiz.time_created = question[4]
            quiz.preferred_answer = question[5]
            return quiz
        return None

    def update_question(self):
        cur.execute("UPDATE questions SET title=%s, body=%s, user_id=%s, time_created=%s, preferred_answer=%s"
                    "WHERE id=%s;",
                    (self.title, self.body, self.user_id, self.time_created, self.preferred_answer, self.question_id))
        conn.commit()


class Answer(object):
    def __init__(self, body, user_id, question_id):
        self.answer_id = ''
        self.body = body
        self.user_id = user_id
        self.question_id = question_id
        self.preferred = False
        self.time_created = datetime.now()

    def insert_answer(self):
        """insert answer to db"""
        question = Question.get_question(self.question_id)
        if question:
            answer_id = uuid.uuid4()
            if self.get_answer_from_body(self.body) is None:
                query = "INSERT INTO answers(id, body, user_id, question_id, preferred, time_created)" \
                        "VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (answer_id, self.body, self.user_id, self.question_id, self.preferred,
                                                                         self.time_created)
                cur.execute(query)
                conn.commit()
                return 'success'
            else:
                return 'duplicated'
        else:
            return 'question not found'

    def delete_answer(self, answer_id):
        """delete answer from db"""
        cur.execute("DELETE FROM answers WHERE id=%s;" % answer_id)

    @staticmethod
    def get_question_answers(question_id):
        """get answers for a particular question"""
        cur.execute("SELECT * FROM answers WHERE question_id='%s'" % question_id)
        answers = cur.fetchall()
        answers_list = []
        for answer in answers:
            answer_dict = {'answer_id': answer[0], 'body': answer[1], 'user_id': answer[2], 'preferred': answer[4]}
            answers_list.append(answer_dict)
        return answers_list

    def get_user_answers(self, user_id):
        """get answers by a particular user"""
        cur.execute("SELECT * FROM answers WHERE user_id=%s" % user_id)
        return cur.fetchall()

    @staticmethod
    def get_answer(answer_id):
        """get answer using answer id"""
        cur.execute("SELECT * FROM answers WHERE id = '%s';" % answer_id)
        answer = cur.fetchone()
        if answer is None:
            return None
        else:
            body = answer[1]
            user_id = answer[2]
            question_id = answer[3]

            ans = Answer(body, user_id, question_id)
            ans.answer_id = answer_id
            ans.time_created = answer[5]
            ans.preferred = answer[4]

            return ans

    @staticmethod
    def get_answer_from_body(body):
        """get answer using answer using body"""
        cur.execute("SELECT * FROM answers WHERE body = '%s';" % body)
        answer = cur.fetchone()
        if answer is None:
            return None
        else:
            body = answer[1]
            user_id = answer[2]
            question_id = answer[3]

            ans = Answer(body, user_id, question_id)
            ans.answer_id = answer[0]
            ans.time_created = answer[5]
            ans.preferred = answer[4]

            return ans

    def update_answer(self, body, preferred):
        cur.execute("UPDATE answers SET body='%s', preferred='%s' WHERE id='%s';" % (body, preferred, self.answer_id))
        conn.commit()
