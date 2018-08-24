import os
import psycopg2

base_dir = os.path.abspath(os.path.dirname(__file__))

try:
    conn = psycopg2.connect("dbname=stackoverflow host=localhost user=postgres password=''")
except Exception as e:
    print("connect to database failed ", e)


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
