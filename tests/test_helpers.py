"""Test the helpers module."""

from logging import DEBUG, WARNING
from os import environ

from pytest import fixture, mark
from shortuuid import uuid

from plateypus import helpers

CACHE_DEFAULT_TIMEOUT = 123
CACHE_TYPE = "simple"
ELASTIC_HOST = "localhost"
ELASTIC_PORT = "9200"
FLASK_SECRET_KEY = uuid()
TESTING = False


@fixture
def set_env():
    environ["CACHE_DEFAULT_TIMEOUT"] = str(CACHE_DEFAULT_TIMEOUT)
    environ["CACHE_TYPE"] = str(CACHE_TYPE)
    environ["ELASTIC_HOST"] = str(ELASTIC_HOST)
    environ["ELASTIC_PORT"] = str(ELASTIC_PORT)
    environ["FLASK_SECRET_KEY"] = str(FLASK_SECRET_KEY)
    environ["LOG_LEVEL"] = str(WARNING)
    environ["TESTING"] = str(TESTING)


def test_init_logger(set_env):
    logger = helpers.init_logger()
    assert logger.getEffectiveLevel() == WARNING
    environ["LOG_LEVEL"] = str(DEBUG)
    logger = helpers.init_logger()
    assert logger.getEffectiveLevel() == DEBUG


def test_get_setting():
    random_key = uuid()
    foo, bar = "foo", "bar"
    assert helpers.get_setting(random_key, foo) == foo
    environ[random_key] = bar
    assert helpers.get_setting(random_key, foo) == bar


def test_app_settings(set_env):
    cfg = helpers.app_settings()
    assert cfg["CACHE_DEFAULT_TIMEOUT"] == CACHE_DEFAULT_TIMEOUT
    assert cfg["CACHE_TYPE"] == CACHE_TYPE
    assert cfg["SECRET_KEY"] == FLASK_SECRET_KEY
    assert cfg["TESTING"] == TESTING


def test_elastic_default(set_env):
    es = helpers.elastic()
    assert str(es) == "<Elasticsearch([{'host': 'localhost', 'port': 9200}])>"


def test_elastic_explicit_no_ssl(set_env):
    es = helpers.elastic(False)
    assert str(es) == "<Elasticsearch([{'host': 'localhost', 'port': 9200}])>"


def test_elastic_ssl(set_env):
    es = helpers.elastic(True)
    assert (
        str(es)
        == "<Elasticsearch([{'host': 'localhost', 'port': 9200, 'use_ssl': True}])>"
    )
