"""This is the Plateypus backend."""

from os.path import join

from elasticapm.contrib.flask import ElasticAPM
from flask import Flask, jsonify, request, send_from_directory
from flask_caching import Cache
from packaging.version import Version

try:
    from helpers import app_settings, init_logger
except (ImportError, ModuleNotFoundError):
    from plateypus.helpers import app_settings, init_logger

PLATEYPUS = Flask(__name__)
PLATEYPUS.config.from_mapping(app_settings())
APM = ElasticAPM(PLATEYPUS)
CACHE = Cache(PLATEYPUS)
LOG = init_logger(__name__)
VERSION = Version("0.0.1")


@PLATEYPUS.route("/")
def info():
    """Return application information."""
    LOG.debug(request)
    resp = jsonify(
        dict(root=PLATEYPUS.root_path, settings=app_settings(), version=str(VERSION))
    )
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@PLATEYPUS.route("/favicon.ico")
@CACHE.cached(timeout=86400)
def favicon():
    """Return favicon."""
    LOG.debug(request)
    return send_from_directory(
        join(PLATEYPUS.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@PLATEYPUS.route("/echo", methods=["POST"])
def echo():
    """Return whatever was posted."""
    LOG.debug(request)
    LOG.debug(request.json)
    return jsonify(request.json)


if __name__ == "__main__":  # pragma: no-cover
    PLATEYPUS.run()
