import os

base_dir = os.path.abspath(os.path.dirname(__file__))


# Base configuration
class Config(object):
    DEBUG = False
    SECRET = os.getenv('STACKOVERFLOW_SECRET', 'KeepYourSecretsToYourself')
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "stackoverflow")


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
