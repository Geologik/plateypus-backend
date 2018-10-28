"""Test ETL routines for the Danish Motor Register."""

from types import SimpleNamespace as obj

from pytest import mark
from pytest_mock import mocker
import requests

from plateypus.etl import dk

@mark.filterwarnings("ignore:.*use_list_a_option.*:DeprecationWarning")
def test_dmr_ftp():
    """Test the FTP connection to the DMR.

    Requires intarwebs, obvs.
    """
    expected = '/ESStatistikListeModtag'
    ftp = dk.dmr_ftp()
    actual = ftp.getcwd()
    ftp.close()
    assert actual == expected

def test_ls_lt():
    """Test that a directory is correctly sorted by time modified."""
    expected = [
        (obj(st_mtime=309), 'bar'),
        (obj(st_mtime=317), 'baz'),
        (obj(st_mtime=324), 'foo'),
        (obj(st_mtime=467), 'quux')]
    mock_ftp = obj(curdir='.')
    mock_ftp.listdir = lambda _: ['foo', 'bar', 'baz', 'quux']
    mock_ftp.stat = lambda f: obj(st_mtime=sum(map(ord, f)))
    actual = dk.ls_lt(mock_ftp)
    assert actual == expected

def test_update_data(mocker):
    """Test the data update."""
    expected = False
    mocker.patch.object(dk, '_download_if_newer')
    dk._download_if_newer.return_value = False
    actual = dk.update_data()
    assert actual == expected

def test_metadata_connection_error():
    dk.METADATA_URL = 'https://foo.invalid/bar'
    ftp = dk.dmr_ftp()
    assert ftp is None
