"""This is the Plateypus backend."""

from flask import Flask, jsonify, request
PLATEYPUS = Flask(__name__)
VERSION = '0.0.1'


@PLATEYPUS.route('/')
def version():
    """Return current version number."""
    resp = jsonify(dict(version=VERSION))
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@PLATEYPUS.route('/echo', methods=['POST'])
def echo():
    """Return whatever was posted."""
    return jsonify(request.json)


if __name__ == '__main__':
    PLATEYPUS.run()
