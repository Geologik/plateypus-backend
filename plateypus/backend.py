"""This is the Plateypus backend."""

from os.path import join

from elasticsearch.exceptions import NotFoundError
from flask import Flask, jsonify, request, send_from_directory
from flask.logging import create_logger
from packaging.version import Version

try:  # pragma: no cover
    from helpers import app_settings, build_query, elastic, search_validator
    from models import Vehicle
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    from plateypus.helpers import app_settings, build_query, elastic, search_validator
    from plateypus.models import Vehicle

PLATEYPUS = Flask(__name__)
PLATEYPUS.config.from_mapping(app_settings())
LOG = create_logger(PLATEYPUS)
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


@PLATEYPUS.route("/search", methods=["POST"])
def search():
    """Search for the submitted license plate (fragment)."""
    sval = search_validator()
    if not sval.validate(request.json):
        LOG.info("invalid search request: %s", sval.errors)
        return jsonify(sval.errors), 400
    with elastic() as client:
        _search = Vehicle.search(using=client)
        fields = request.json["fields"]
        if "country" in fields:
            _search = _search.filter("term", country=fields["country"])
        if "plate" in fields:
            _search = _search.query(build_query("plate", fields, "2"))
        for field in ("maker", "model", "vin"):
            if field in fields:
                _search = _search.query(build_query(field, fields))
        return jsonify([hit.to_dict() for hit in _search.execute()["hits"]["hits"]])


@PLATEYPUS.route("/vehicle/<string:vehicle_id>")
def vehicle(vehicle_id):
    """Return details for the given vehicle."""
    with elastic() as client:
        try:
            _vehicle = Vehicle.get(vehicle_id, using=client)
            return jsonify(_vehicle.to_dict())
        except NotFoundError:
            return jsonify(f"{vehicle_id} not found"), 404


if __name__ == "__main__":  # pragma: no cover
    PLATEYPUS.run()
