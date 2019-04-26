"""This is the Plateypus backend."""

from os.path import join

from flask import Flask, jsonify, request, send_from_directory
from flask_caching import Cache
from packaging.version import Version

try:
    from helpers import app_settings
except (ImportError, ModuleNotFoundError):
    from plateypus.helpers import app_settings

PLATEYPUS = Flask(__name__)
PLATEYPUS.config.from_mapping(app_settings())
CACHE = Cache(PLATEYPUS)
VERSION = Version("0.0.1")


@PLATEYPUS.route("/")
def info():
    """Return application information."""
    resp = jsonify(
        dict(root=PLATEYPUS.root_path, settings=app_settings(), version=str(VERSION))
    )
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@PLATEYPUS.route("/favicon.ico")
@CACHE.cached(timeout=86400)
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
    return jsonify(request.json)


if __name__ == "__main__":  # pragma: no-cover
    PLATEYPUS.run()
