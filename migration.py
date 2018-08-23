from project.config import conn


def migration():
    """create db tables"""
    cur = conn.cursor()

    try:
        # delete tables if they exist
        cur.execute("DROP TABLE IF EXISTS questions,answers, users;")
        cur.execute("DROP TABLE IF EXISTS tokens;")


        # create table users
        users = "CREATE TABLE users(id UUID PRIMARY KEY, username VARCHAR(64) UNIQUE , email VARCHAR(64) UNIQUE," \
                "password_hash VARCHAR(256),time_created TIMESTAMP );"

        # create table questions
        questions = "CREATE TABLE questions(id UUID PRIMARY KEY, title VARCHAR(256), body TEXT," \
                    "uid UUID, time_created TIMESTAMP, preferred_answer UUID);"

        # create table answers
        answers = "CREATE TABLE answers(id UUID PRIMARY KEY, body TEXT," \
                    "uid UUID, qid UUID, preferred BOOLEAN DEFAULT FALSE, time_created TIMESTAMP);"


        # create table tokens
        tokens = "CREATE TABLE tokens(id UUID PRIMARY KEY, expired_tokens VARCHAR(256));"

        cur.execute(users)
        cur.execute(questions)
        cur.execute(answers)
        cur.execute(tokens)

        conn.commit()
    except Exception as e:
        print('error in migration', e)


migration()
