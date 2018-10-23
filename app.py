"""This is the Plateypus Backend."""

from flask import Flask
APP = Flask(__name__)


@APP.route('/')
def hello():
    """The essential minimum."""
    return u'Hello world!'


if __name__ == '__main__':
    APP.run()
