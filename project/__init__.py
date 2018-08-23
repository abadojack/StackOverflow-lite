
import os
from flask import Flask
from project.questions.views import stackoverflow
from project.models.models import users

app = Flask(__name__)

app.register_blueprint(stackoverflow, url_prefix='/api/v1')
app.register_blueprint(users, url_prefix='/api/v1')

app_settings = os.getenv(
    'APP_SETTINGS',
    'project.config.DevConfig'
)
app.config.from_object(app_settings)
