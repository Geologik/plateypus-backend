"""Test the Plateypus backend."""

from plateypus.etl import dk


def test_dmr_ftp():
    """Test the FTP connection to the DMR.

    Requires intarwebs, obvs.
    """
    ftp = dk.dmr_ftp()
    actual = ftp.getcwd()
    ftp.close()
    expected = '/ESStatistikListeModtag'
    assert actual == expected

def test_ls_lt():
    """Test that a directory is correctly sorted by time modified."""
    mock_ftp = None
    try:
        files = dk.ls_lt(mock_ftp)
    except AttributeError:
        pass

def test_update_data():
    """Test the data update."""
    pass
