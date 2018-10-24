"""This is the Plateypus backend."""

from flask import Flask
PLATEYPUS = Flask(__name__)


@PLATEYPUS.route('/')
def hello():
    """The essential minimum."""
    return u'Hello world!'


if __name__ == '__main__':
    PLATEYPUS.run()
