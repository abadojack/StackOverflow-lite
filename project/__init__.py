# project/app.py

# imports
import os
from flask import Flask
# blueprints
from project.questions.views import stackoverflow

# configuration
app = Flask(__name__)

# register blueprints
app.register_blueprint(stackoverflow, url_prefix='/api/v1')

# app configuration
app_settings = os.getenv(
    'APP_SETTINGS',
    'project.config.DevConfig'
)
app.config.from_object(app_settings)
