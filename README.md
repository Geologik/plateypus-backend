# Plateypus Backend

[![Python 3](https://pyup.io/repos/github/Geologik/plateypus-backend/python-3-shield.svg)](https://pyup.io/repos/github/Geologik/plateypus-backend/)
[![Build Status](https://travis-ci.org/Geologik/plateypus-backend.svg?branch=master)](https://travis-ci.org/Geologik/plateypus-backend)
[![Codecov Status](https://codecov.io/gh/Geologik/plateypus-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/Geologik/plateypus-backend)
[![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=plateypus-backend&metric=alert_status)](https://sonarcloud.io/dashboard?id=plateypus-backend)
[![Requirements Status](https://requires.io/github/Geologik/plateypus-backend/requirements.svg?branch=master)](https://requires.io/github/Geologik/plateypus-backend/requirements/?branch=master)
[![Updates](https://pyup.io/repos/github/Geologik/plateypus-backend/shield.svg)](https://pyup.io/repos/github/Geologik/plateypus-backend/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Backend service for the [Plateypus app](https://github.com/Geologik/plateypus).

## Configuration

The Plateypus backend is configured using environment variables. User-controllable settings and their default values are:

| Key                     | Description | Default |
| ----------------------- | ----------- | ------- |
| `APM_PATH`              | Path to a folder containing the `apm-server` executable. Only intended for use in a development environment. | |
| `CACHE_DEFAULT_TIMEOUT` | Cache default timeout in seconds. | `600` |
| `CACHE_REDIS_URL`       | URL to connect to Redis server, e.g. `redis://usr:pwd@localhost:6379/2`. Only used if `CACHE_TYPE` is `redis`. | |
| `CACHE_TYPE`            | Specifies which type of caching to use. See [Configuring Flask-Caching](https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching) for more information. Supported values are `null`, `simple` and `redis`. | `null` |
| `ELASTIC_HOST`          | Base URL or IP of the Elasticsearch server to use. | `localhost` |
| `ELASTIC_PORT`          | Elasticsearch server port. | `9200` |
| `ELASTIC_PROTOCOL`      | Elasticsearch server protocol. | `http` |
| `FLASK_ENV`             | Controls whether the app is running in development or production mode. Supported values are `development` and `production`. | `production` |
| `FLASK_SECRET_KEY`      | For session support, a secret key must be set. You may generate a new key with `pipenv run keygen`. | |
| `FLASK_TESTING`         | Enable testing mode. Exceptions are propagated rather than handled by the the app's error handlers. Supported values are `True` and `False` (case-insensitive). | `False` |
| `LOG_LEVEL`             | Minimum threshold for log messages. See [Logging Levels](https://docs.python.org/3/library/logging.html#levels). Must be explicitly given as an integer. | `30` (i.e. `WARNING`) |
| `LOG_OUTPUT`            | If set, log messages will be appended to this file. A fully qualified path must be given. | |

## CLI scripts

The project's `Pipfile` defines a number of scripts, which can be run in a command prompt by typing `pipenv run <script>`.

Script    | Description
--------- | -----------
`debug`   | Execute unit tests, dropping to the `pdb` debugger on the first error. *Windows only.*
`elastic` | Start clean dockerized [Elasticsearch](https://elastic.co/products/elasticsearch) and [Kibana](https://elastic.co/products/kibana) servers, as well as an [APM Server](https://elastic.co/solutions/apm) if the `APM_PATH` environment variable is set.
`flask`   | Start a local development server.
`keygen`  | Generate a key suitable for use with the `FLASK_SECRET_KEY` setting.
`lint`    | Run a chain of analysis tools and linters: `isort` → `black` → `pylint` → `bandit`.
`test`    | Execute unit tests and calculate code coverage. *Windows only.* |
