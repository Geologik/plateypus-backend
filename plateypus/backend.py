"""This is the Plateypus backend."""

from os import environ
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

SETTINGS = environ['APP_SETTINGS']
VERSION = '0.0.1'

PLATEYPUS = Flask(__name__)
PLATEYPUS.config.from_object(SETTINGS)

PLATEYPUS.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DB = SQLAlchemy(PLATEYPUS)


@PLATEYPUS.route('/')
def info():
    """Return application information."""
    resp = jsonify(dict(settings=SETTINGS, version=VERSION))
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@PLATEYPUS.route('/echo', methods=['POST'])
def echo():
    """Return whatever was posted."""
    return jsonify(request.json)


if __name__ == '__main__':
    PLATEYPUS.run()  # pragma: no cover
