"""Test ETL routines for the Danish Motor Register."""

from pytest import mark
from pytest_mock import mocker

from plateypus.etl.dk import Extract, extract_transform_load
from plateypus.helpers import t_0


@mark.filterwarnings("ignore:.*use_list_a_option.*:DeprecationWarning")
def test_dmr_ftp():
    """Test the FTP connection to the DMR.

    Requires intarwebs, obvs.
    """
    expected = "/ESStatistikListeModtag"
    extr = Extract()
    actual = extr.ftp.getcwd()
    assert actual == expected


@mark.filterwarnings("ignore:.*use_list_a_option.*:DeprecationWarning")
def test_no_new_data(mocker):
    """Test no new data path."""
    expected = False
    mocker.patch.object(Extract, "download_if_newer")
    extr = Extract()
    extr.download_if_newer.return_value = (False, t_0())
    actual = extract_transform_load()
    assert actual == expected


@mark.filterwarnings("ignore:.*use_list_a_option.*:DeprecationWarning")
def test_metadata_connection_error():
    """Test that no FTP host is created when trying to open an invalid URL."""
    extr = Extract()
    extr.METADATA_URL = "https://foo.invalid/bar"
    extr.open_dmr_ftp()
    assert extr.ftp is None
