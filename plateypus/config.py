"""Plateypus configuration module."""

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base (dev) configuration."""
    DEBUG = True
    DEVELOPMENT = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'not so bloody secret innit?'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    """Production configuration. Explicit for safety's sake!"""
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False


class StagingConfig(Config):
    """Staging configuration."""
    DEVELOPMENT = False


class DevelopmentConfig(Config):
    """Dev configuration."""
    pass


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    DEVELOPMENT = False
    TESTING = True
