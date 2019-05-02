"""Test the helpers module."""

from logging import DEBUG, WARNING
from os import environ
from pathlib import Path
from tempfile import gettempdir

from pytest import fixture
from shortuuid import uuid

from plateypus import helpers

CACHE_DEFAULT_TIMEOUT = 123
CACHE_TYPE = "simple"
ELASTIC_HOST = "localhost"
ELASTIC_PORT = "9200"
FLASK_SECRET_KEY = uuid()
TESTING = True


@fixture
def set_env():
    """Setup some environment values."""
    environ["CACHE_DEFAULT_TIMEOUT"] = str(CACHE_DEFAULT_TIMEOUT)
    environ["CACHE_TYPE"] = str(CACHE_TYPE)
    environ["ELASTIC_HOST"] = str(ELASTIC_HOST)
    environ["ELASTIC_PORT"] = str(ELASTIC_PORT)
    environ["FLASK_SECRET_KEY"] = str(FLASK_SECRET_KEY)
    environ["FLASK_TESTING"] = str(TESTING)
    environ["LOG_LEVEL"] = str(WARNING)


def test_init_logger(set_env):
    """Test initialization of the root logger."""
    logger = helpers.init_logger()
    assert logger.getEffectiveLevel() == WARNING
    environ["LOG_LEVEL"] = str(DEBUG)
    logger = helpers.init_logger()
    assert logger.getEffectiveLevel() == DEBUG

    # Teardown
    environ["LOG_LEVEL"] = str(WARNING)


def test_init_logger_default_level():
    """Test initialization of the root logger when LOG_LEVEL is not set."""
    logger = helpers.init_logger()
    assert logger.getEffectiveLevel() == WARNING


def test_init_logger_with_logfile(set_env):
    """Test initialization of a logger with a log file."""
    log_path = f"{gettempdir()}/{uuid()}.log"
    assert not Path(log_path).exists()
    environ["LOG_OUTPUT"] = log_path
    logger = helpers.init_logger(uuid())
    msg = "Write to disk."
    logger.warning(msg)
    assert Path(log_path).exists()
    with open(log_path, 'r') as log:
        assert msg in log.read()

    # Teardown
    del environ["LOG_OUTPUT"]


def test_get_setting():
    """Test that env settings can be retrieved, or if not then a default value is returned."""
    random_key = uuid()
    default_value, actual_value = "foo", "bar"
    assert helpers.get_setting(random_key, default_value) == default_value
    environ[random_key] = actual_value
    assert helpers.get_setting(random_key, default_value) == actual_value


def test_app_settings(set_env):
    """Test that settings are correctly loaded into the Flask app."""
    cfg = helpers.app_settings()
    assert cfg["CACHE_DEFAULT_TIMEOUT"] == CACHE_DEFAULT_TIMEOUT
    assert cfg["CACHE_TYPE"] == CACHE_TYPE
    assert cfg["SECRET_KEY"] == FLASK_SECRET_KEY
    assert cfg["TESTING"] == TESTING


def test_elastic_default(set_env):
    """Test creation of Elasticsearch client."""
    with helpers.elastic() as client:
        assert str(client) == "<Elasticsearch([{'host': 'localhost', 'port': 9200}])>"


# def test_elastic_ssl(set_env):
#     environ["ELASTIC_PROTOCOL"] = "https"
#     with helpers.elastic() as client:
#         assert str(client) == "<Elasticsearch([{'host': 'localhost', 'port': 9200, 'use_ssl': True}])>"
#
#     # Teardown
#     environ["ELASTIC_PROTOCOL"] = "http"
#     helpers.elastic()
