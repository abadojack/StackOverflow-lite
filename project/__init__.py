import os
from flask import Flask, redirect
from flask_cors import CORS
from project.questions.views import questions
from project.users.views import users

app = Flask(__name__)
CORS(app)
app.register_blueprint(questions, url_prefix='/api/v1')
app.register_blueprint(users, url_prefix='/api/v1')


@app.route('/')
def root():
    return redirect("https://stackoverflow3.docs.apiary.io/", code=302)


@app.route('/ping', methods=['GET'])
def pong():
    return 'pong', 200


app_settings = os.getenv(
    'APP_SETTINGS',
    'project.config.DevConfig'
)
app.config.from_object(app_settings)
