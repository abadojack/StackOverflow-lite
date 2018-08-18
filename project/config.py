# project/config file


import os
import psycopg2

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Base config class"""
    DEBUG = False
    CSRF_ENABLED = True


class DevConfig(Config):
    """Configuration for development"""
    DEBUG = True


class TestConfig(Config):
    """Test config"""
    TESTING = True
    DEBUG = True


class StagingConfig(Config):
    """Staging configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Staging for production"""
    DEBUG = False
    TESTING = False
