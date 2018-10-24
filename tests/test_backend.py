"""Test the Plateypus backend."""

import pytest
from plateypus import backend


@pytest.fixture
def client():
    """Yield client fixture.

    See <http://flask.pocoo.org/docs/1.0/testing/#the-testing-skeleton>
    for ideas to expand this.
    """
    yield backend.PLATEYPUS.test_client()


def okay(resp):
    """Check whether an HTTP response is 200 OK."""
    return resp.status_code == 200


def test_tautology():
    """This test canary always passes."""
    assert 2 + 2 == 4


def test_hello(client):
    resp = client.get('/')
    assert okay(resp)

    result = resp.get_json()
    expected = dict(Hello='world!')
    assert result == expected


def test_echo(client):
    payload = dict(foo='bar', baz=42)
    resp = client.post('/echo', json=payload)
    assert okay(resp)

    result = resp.get_json(force=True)
    expected = payload
    assert result == expected
