"""Test the Plateypus backend."""

from pytest import fixture
from shortuuid import uuid

from plateypus import backend, helpers, models


@fixture
def client():
    """Yield client fixture.

    See <http://flask.pocoo.org/docs/1.0/testing/#the-testing-skeleton>
    for ideas to expand this.
    """
    yield backend.PLATEYPUS.test_client()


@fixture
def vehicle(scope="module"):
    """Yield a Vehicle document that has already been saved."""
    country = uuid()
    plate = uuid()
    vin = uuid()
    maker = uuid()
    model = uuid()
    _vehicle = models.Vehicle(
        country=country, plate=plate, vin=vin, maker=maker, model=model
    )
    with helpers.elastic() as es_client:
        _vehicle.save(using=es_client)
        yield _vehicle
        _vehicle.delete(using=es_client)


def okay(resp):
    """Check whether an HTTP response is 200 OK."""
    return resp.status_code == 200


def test_tautology():
    """This test canary always passes."""
    assert 2 + 2 == 4


def test_testing():
    """Assert that we are always running tests in test mode."""
    testing = backend.PLATEYPUS.config["TESTING"]
    assert testing and isinstance(testing, bool)


def test_echo(client):
    """The ``echo'' endpoint should return whatever is sent to it."""
    payload = dict(foo="bar", baz=42)
    resp = client.post("/echo", json=payload)
    assert okay(resp)

    result = resp.get_json(force=True)
    expected = payload
    assert result == expected


def test_favicon(client):
    """A favicon should be available at the default URL."""
    resp = client.get("/favicon.ico")
    assert okay(resp)
    assert resp.mimetype == "image/vnd.microsoft.icon"


def test_search(client, vehicle):
    """Search should return something."""
    payload = dict(fields=dict(country=vehicle.country, maker=vehicle.maker))
    resp = client.post("/search", json=payload)
    assert okay(resp)
    payload = dict(fields=dict(vin=vehicle.vin, maker=vehicle.maker))
    resp = client.post("/search", json=payload)
    assert okay(resp)
    payload = dict(fields=dict(plate=vehicle.plate))
    resp = client.post("/search", json=payload)
    assert okay(resp)
    payload = dict(fields=dict(vin=f"{vehicle.vin[:6]}*"))
    resp = client.post("/search", json=payload)
    assert okay(resp)
    payload = dict(fields=dict(model=vehicle.model))
    resp = client.post("/search", json=payload)
    assert okay(resp)


def test_search_bad_request(client):
    """Submitting a malformed search request should result in HTTP error code 400."""
    payload = dict(foo="bar", baz=42)
    resp = client.post("/search", json=payload)
    assert resp.status_code == 400


def test_version(client):
    """The ``version'' endpoint should return the version defined in the backend."""
    resp = client.get("/")
    assert okay(resp)

    result = resp.get_json()
    expected = dict(
        root=backend.PLATEYPUS.root_path,
        settings=helpers.app_settings(),
        version=str(backend.VERSION),
    )
    assert result == expected


def test_vehicle_found(client, vehicle):
    """Vehicle details are returned when requesting an existing id."""
    resp = client.get(f"/vehicle/{vehicle.meta.id}")
    assert okay(resp)
    assert resp.json["country"] == vehicle.country
    assert resp.json["plate"] == vehicle.plate
    assert resp.json["vin"] == vehicle.vin
    assert resp.json["maker"] == vehicle.maker
    assert resp.json["model"] == vehicle.model


def test_vehicle_not_found(client):
    """404 is returned when vehicle is not found."""
    resp = client.get("/vehicle/xyz")
    assert resp.status_code == 404
