
import os

base_dir = os.path.abspath(os.path.dirname(__file__))


# Base configuration
class Config(object):
    DEBUG = False
    CSRF_ENABLED = True


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
