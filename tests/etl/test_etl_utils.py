"""Test ETL utility methods."""

from types import SimpleNamespace as obj

from pytest import mark

from plateypus.etl import etl_utils

@mark.filterwarnings("ignore:.*use_list_a_option.*:DeprecationWarning")
def test_ftp_connect():
    """Test connection to FTP host."""
    server = 'test.rebex.net'
    user = 'demo'
    passwd = 'password'
    cwd = '/pub/example'
    try:
        ftp = etl_utils.ftp_connect(server, user, passwd, cwd)
        assert ftp is not None
        assert cwd == ftp.getcwd()
        assert 'readme.txt' in ftp.listdir('/')
    finally:
        if ftp:
            ftp.close()

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
    actual = etl_utils.ls_lt(mock_ftp)
    assert actual == expected
