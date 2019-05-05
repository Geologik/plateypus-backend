"""Test ETL routines for the Danish Motor Register."""

from io import TextIOWrapper
from os.path import dirname, normpath, realpath
from tempfile import SpooledTemporaryFile

from pytest import mark
from pytest_mock import mocker

from plateypus.etl.dk import Extract, Transform, extract_transform_load
from plateypus.helpers import t_0

PATH_TO_TESTDATA = normpath(
    f"{dirname(realpath(__file__))}/../testdata/testdata_dk.zip"
)

# region Extract


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


# endregion

# region Transform


def test_xml_stream_not_zipfile():
    """None is returned if trying to read a non-zipfile."""
    with SpooledTemporaryFile(max_size=1024, suffix=".zip") as nonzipf:
        nonzipf.rollover()
        trf = Transform(nonzipf.name)
        assert trf.xml_stream() is None


def test_xml_stream():
    """A ``TextIOWrapper'' is returned if a zipfile is provided."""
    trf = Transform(PATH_TO_TESTDATA)
    xml_stream = trf.xml_stream()
    assert isinstance(xml_stream, TextIOWrapper)
    assert xml_stream.encoding == "utf-8"


# endregion

# region Load

# endregion
