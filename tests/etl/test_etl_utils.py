"""Test ETL utility methods."""

from datetime import datetime
from io import StringIO
from time import sleep
from types import SimpleNamespace as obj
from warnings import warn

from ftputil.error import TemporaryError
from lxml import etree
from pytest import fixture, mark, warns
from pytz import utc
from shortuuid import uuid

from plateypus.etl import etl_utils
from plateypus.helpers import elastic, t_0
from plateypus.models import Metadata


@fixture
def xml():
    """Yield XML pull parser events and namespace map."""
    uri = "http://example.org/"
    nsmap = dict(ns=uri)
    xmldoc = f"""<?xml version="1.0" encoding="UTF-8"?>
              <ns:root xmlns:ns="{uri}">
                <ns:textnode>foo</ns:textnode>
                <ns:notextnode><ns:filler></ns:filler></ns:notextnode>
                <ns:emptynode></ns:emptynode>
                <ns:twinnode>first</ns:twinnode>
                <ns:twinnode>second</ns:twinnode>
              </ns:root>"""
    parser = etree.XMLPullParser()
    with StringIO(xmldoc) as instream:
        for _, line in enumerate(instream):
            parser.feed(line)
    parser.close()
    events = parser.read_events()
    yield dict(events=events, nsmap=nsmap)


@mark.filterwarnings("ignore:.*use_list_a_option.*:DeprecationWarning")
def test_ftp_connect():
    """Test connection to FTP host."""
    server = "test.rebex.net"
    user = "demo"
    passwd = "password"
    cwd = "/pub/example"
    try:
        ftp = etl_utils.ftp_connect(server, user, passwd, cwd)
        assert ftp is not None
        assert cwd == ftp.getcwd()
    except TemporaryError as tmp_err:
        if tmp_err.errno == 425:
            warn(tmp_err.strerror)
        else:
            raise
    finally:
        if ftp:
            ftp.close()


@mark.filterwarnings("ignore:.*use_list_a_option.*:DeprecationWarning")
def test_ftp_noconnect():
    """Test invalid connection to FTP host."""
    ftp = etl_utils.ftp_connect("foo", "bar", "baz", "quux")
    assert ftp is None


def test_get_node_text_found(xml):
    """Test that text can be retrieved from a node inside a node."""
    expected = "foo"
    actual = "bar"
    uri = xml["nsmap"]["ns"]
    for _, elem in xml["events"]:
        if elem.tag == f"{{{uri}}}root":
            actual = etl_utils.get_node_text(elem, "textnode", xml["nsmap"])
    assert actual == expected


def test_get_node_text_not_found(xml):
    """Test that no text is retrieved from a node not found inside another node."""
    expected = ""
    actual = "bar"
    uri = xml["nsmap"]["ns"]
    for _, elem in xml["events"]:
        if elem.tag == f"{{{uri}}}root":
            with warns(UserWarning, match="Did not find notfoundnode"):
                actual = etl_utils.get_node_text(elem, "notfoundnode", xml["nsmap"])

    assert actual == expected


def test_get_node_text_on_node_with_no_text_inside(xml):
    """Test that get_node_text on a node only containing another node returns the empty string."""
    expected = ""
    actual = "bar"
    uri = xml["nsmap"]["ns"]
    for _, elem in xml["events"]:
        if elem.tag == f"{{{uri}}}root":
            actual = etl_utils.get_node_text(elem, "notextnode", xml["nsmap"])
    assert actual == expected


def test_get_node_text_on_empty_node(xml):
    """Test that get_node_text on an empty node returns the empty string."""
    expected = ""
    actual = "bar"
    uri = xml["nsmap"]["ns"]
    for _, elem in xml["events"]:
        if elem.tag == f"{{{uri}}}root":
            actual = etl_utils.get_node_text(elem, "emptynode", xml["nsmap"])
    assert actual == expected


def test_get_node_text_on_repeating_node(xml):
    """Test that get_node_text on a node found more than once
    returns the contents of the first encountered node.
    """
    expected = "first"
    actual = "bar"
    uri = xml["nsmap"]["ns"]
    for _, elem in xml["events"]:
        if elem.tag == f"{{{uri}}}root":
            with warns(UserWarning, match="Found 2 twinnode nodes"):
                actual = etl_utils.get_node_text(elem, "twinnode", xml["nsmap"])
    assert actual == expected


def test_ls_lt():
    """Test that a directory is correctly sorted by time modified."""
    expected = [
        (obj(st_mtime=309), "bar"),
        (obj(st_mtime=317), "baz"),
        (obj(st_mtime=324), "foo"),
        (obj(st_mtime=467), "quux"),
    ]
    mock_ftp = obj(curdir=".")
    mock_ftp.listdir = lambda _: ["foo", "bar", "baz", "quux"]
    mock_ftp.stat = lambda f: obj(st_mtime=sum(map(ord, f)))
    actual = etl_utils.ls_lt(mock_ftp)
    assert actual == expected


def test_newer_than_latest():
    """Test whether the timestamp is newer than the one in the database."""
    country = uuid()
    etl_utils.upsert_metadata(country, datetime.fromtimestamp(1000000001, utc))
    sleep(2)
    assert not etl_utils.newer_than_latest(
        country, datetime.fromtimestamp(1000000000, utc)
    )
    assert etl_utils.newer_than_latest(country, datetime.now(utc))

    # Teardown
    with elastic() as client:
        Metadata.search(using=client).filter("term", country=country).delete()


def test_newer_than_latest_first_run():
    """Test that newer_than_latest compares to the earliest known time
    when there is no timestamp for country in the -database."""
    country = uuid()
    assert etl_utils.newer_than_latest(country, datetime.now(utc))
    assert not etl_utils.newer_than_latest(country, t_0())


def test_upsert_metadata():
    """Test that upsert_metadata inserts or updates data."""
    country = uuid()
    datetime_2001 = datetime.fromtimestamp(1000000000, utc)
    datetime_2033 = datetime.fromtimestamp(2000000000, utc)
    with elastic() as client:
        assert (
            Metadata.search(using=client).filter("term", country=country).count() == 0
        )
        etl_utils.upsert_metadata(country, datetime_2001)

    sleep(2)
    with elastic() as client:
        assert (
            Metadata.search(using=client).filter("term", country=country).count() == 1
        )
        assert (
            Metadata.search(using=client)
            .filter("term", country=country)
            .execute()[0]
            .last_updated
            == datetime_2001
        )
        etl_utils.upsert_metadata(country, datetime_2033)

    sleep(2)
    with elastic() as client:
        assert (
            Metadata.search(using=client).filter("term", country=country).count() == 1
        )
        assert (
            Metadata.search(using=client)
            .filter("term", country=country)
            .execute()[0]
            .last_updated
            == datetime_2033
        )

    # Teardown
    with elastic() as client:
        Metadata.search(using=client).filter("term", country=country).execute()[
            0
        ].delete(using=client)
