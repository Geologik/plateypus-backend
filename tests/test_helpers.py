"""Test the helpers module."""

from logging import DEBUG, ERROR, WARNING
from pathlib import Path
from random import choice, randint
from secrets import token_urlsafe
from tempfile import gettempdir

from shortuuid import uuid

from plateypus import helpers


def test_init_logger(monkeypatch):
    """Test initialization of the root logger with default values."""
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("LOG_OUTPUT", raising=False)
    logger = helpers.init_logger()
    assert logger.getEffectiveLevel() == WARNING
    monkeypatch.setenv("LOG_LEVEL", str(DEBUG))
    logger = helpers.init_logger()
    assert logger.getEffectiveLevel() == DEBUG


def test_init_logger_explicit_level():
    """Test initialization of the root logger with explicit LOG_LEVEL."""
    logger = helpers.init_logger(uuid(), lvl=ERROR)
    assert logger.getEffectiveLevel() == ERROR


def test_init_logger_with_logfile(monkeypatch):
    """Test initialization of a logger with a log file."""
    log_path = f"{gettempdir()}/{uuid()}.log"
    assert not Path(log_path).exists()
    monkeypatch.setenv("LOG_OUTPUT", log_path)
    logger = helpers.init_logger(uuid())
    msg = "Write to disk."
    logger.warning(msg)
    assert Path(log_path).exists()
    with open(log_path, "r") as log:
        assert msg in log.read()


def test_get_setting(monkeypatch):
    """Test that env settings can be retrieved, or if not then a default value is returned."""
    random_key = uuid()
    default_value, actual_value = "foo", "bar"
    assert helpers.get_setting(random_key, default_value) == default_value
    monkeypatch.setenv(random_key, actual_value)
    assert helpers.get_setting(random_key, default_value) == actual_value


def test_app_settings(monkeypatch):
    """Test that settings are correctly loaded into the Flask app."""
    cache_default_timeout = randint(100, 1200)
    cache_type = choice(["null", "simple", "redis"])
    flask_secret_key = token_urlsafe(16)
    testing = bool(randint(0, 1))
    monkeypatch.setenv("CACHE_DEFAULT_TIMEOUT", str(cache_default_timeout))
    monkeypatch.setenv("CACHE_TYPE", cache_type)
    monkeypatch.setenv("FLASK_SECRET_KEY", flask_secret_key)
    monkeypatch.setenv("FLASK_TESTING", str(testing))

    cfg = helpers.app_settings()
    assert cfg["CACHE_DEFAULT_TIMEOUT"] == cache_default_timeout
    assert cfg["CACHE_TYPE"] == cache_type
    assert cfg["SECRET_KEY"] == flask_secret_key
    assert cfg["TESTING"] == testing


def test_elastic_default(monkeypatch):
    """Test creation of Elasticsearch client."""
    elastic_host = uuid().lower()
    elastic_port = str(randint(1024, 65535))
    monkeypatch.setenv("ELASTIC_HOST", elastic_host)
    monkeypatch.setenv("ELASTIC_PORT", elastic_port)
    with helpers.elastic() as client:
        assert (
            str(client)
            == f"<Elasticsearch([{{'host': '{elastic_host}', 'port': {elastic_port}}}])>"
        )


def test_elastic_ssl(monkeypatch):
    """Test creation of HTTPS Elasticsearch client."""
    elastic_host = uuid().lower()
    elastic_port = str(randint(1024, 65535))
    monkeypatch.setenv("ELASTIC_HOST", elastic_host)
    monkeypatch.setenv("ELASTIC_PORT", str(elastic_port))
    monkeypatch.setenv("ELASTIC_PROTOCOL", "https")
    with helpers.elastic() as client:
        assert (
            str(client)
            == f"<Elasticsearch([{{'host': '{elastic_host}', 'port': {elastic_port}, 'use_ssl': True}}])>"
        )
