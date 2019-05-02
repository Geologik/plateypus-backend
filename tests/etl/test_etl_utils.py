"""Test ETL utility methods."""

from datetime import datetime
from types import SimpleNamespace as obj
from warnings import warn

from ftputil.error import TemporaryError
from pytest import mark
from pytz import utc

from plateypus.etl import etl_utils
from plateypus.helpers import t_0


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


# TODO this test requires a fixture with Metadata for dk
#def test_newer_than_latest():
#    """Test whether the timestamp is newer than the one in the database."""
#    assert etl_utils.newer_than_latest("dk", datetime(1970, 1, 1, tzinfo=utc))
#    assert not etl_utils.newer_than_latest("dk", datetime.now(utc))


def test_newer_than_latest_first_run():
    """Test that newer_than_latest compares to the earliest known time
    when there is no timestamp for country in the database."""
    assert etl_utils.newer_than_latest("yy", datetime.now(utc))
    assert not etl_utils.newer_than_latest("yy", t_0())
