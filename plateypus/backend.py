"""This is the Plateypus backend."""

from os.path import join

from elasticapm.contrib.flask import ElasticAPM
from flask import Flask, jsonify, request, send_from_directory
from flask.logging import create_logger
from packaging.version import Version

try:
    from helpers import app_settings
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    from plateypus.helpers import app_settings

PLATEYPUS = Flask(__name__)
PLATEYPUS.config.from_mapping(app_settings())
LOG = create_logger(PLATEYPUS)
APM = ElasticAPM(PLATEYPUS)
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
def favicon():
    """Return favicon."""
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


if __name__ == "__main__":  # pragma: no cover
    PLATEYPUS.run()
