import time


class User(object):
    def __init__(self, uid, username, email, password):
        self.uid = uid
        self.username = username
        self.email = email
        self.password = password
        self.questions = []
        self.answers = []
        self.time_created = time.asctime()

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
    def __init__(self, qid, title, body, poster, answers=[]):
        self.qid = qid
        self.title = title
        self.body = body
        self.poster = poster
        self.time_created = time.asctime()
        self.answers = answers

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
    def __init__(self, aid, body, poster=User(id,'Anonymous', 'anonymous@stackoverflow.com', 'anonymous')):
        self.aid = aid
        self.body = body
        self.poster = poster
        self.time_created = time.asctime()

    def unpack(self):
        poster = User.unpack(self.poster)
        return {'id': self.aid, 'body': self.body, 'time_created': self.time_created,
                'poster': poster}


users = [User(0, "starlord", "starlord@avengers.universe", "password"),
         User(1, "ironman", "stark@avengers.universe", "password"),
         User(2, "drax", "drax@avengers.universe", "password")]

answers = [Answer(0, "Yeah, I'll do you one better. Who's Gamora ?", users[1]),
           Answer(1, "Yeah, I'll do you one better. Why's Gamora ?", users[2])]

questions = [Question(0, "Where", "Where is Gamora?", users[0], [answers[0]]),
             Question(1, "Who?", "Who is Gamora?", users[1], [answers[1]]),
             Question(2, "Why", "why is Gamora?", users[2])]
