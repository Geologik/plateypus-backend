"""This is the Plateypus backend."""

from flask import Flask, jsonify, request
PLATEYPUS = Flask(__name__)


@PLATEYPUS.route('/')
def hello():
    """Return Hello world! json."""
    resp = jsonify({'Hello': 'world!'})
    resp.headers['Cache-Control'] = 'no-cache'
    return resp


@PLATEYPUS.route('/echo', methods=['POST'])
def echo():
    """Return whatever was posted."""
    return jsonify(request.json)


if __name__ == '__main__':
    PLATEYPUS.run()
