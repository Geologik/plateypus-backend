"""This is the Plateypus backend."""

from os import environ
from os.path import join

from elasticsearch import Elasticsearch
from flask import Flask, jsonify, request, send_from_directory

VERSION = "0.0.1"


def app_settings():
    """Retrieve the environment app settings."""
    return dict(
        TESTING=environ["TESTING"] == "True",
        SECRET_KEY=environ["FLASK_SECRET_KEY"],
        ELASTIC_HOST=environ["ELASTIC_HOST"],
        ELASTIC_PORT=environ["ELASTIC_PORT"],
    )


def elastic(ssl=False):
    """Return an initialized Elastic client."""
    cfg = app_settings()
    protocol = "https" if ssl else "http"
    host = cfg["ELASTIC_HOST"]
    port = cfg["ELASTIC_PORT"]
    return Elasticsearch(f"{protocol}://{host}:{port}")


def make_app():
    """Create and return the backend app."""
    app = Flask(__name__)
    app.config.from_mapping(app_settings())

    @app.route("/")
    def info():
        """Return application information."""
        resp = jsonify(
            dict(root=app.root_path, settings=app_settings(), version=VERSION)
        )
        resp.headers["Cache-Control"] = "no-cache"
        return resp

    @app.route("/favicon.ico")
    def favicon():
        """Return favicon."""
        return send_from_directory(
            join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    @app.route("/echo", methods=["POST"])
    def echo():
        """Return whatever was posted."""
        return jsonify(request.json)

    return app


if __name__ == "__main__":  # pragma: no-cover
    app = make_app()
    app.run()
