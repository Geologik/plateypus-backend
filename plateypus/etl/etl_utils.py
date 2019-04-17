"""Utility methods for ETL routines."""

from datetime import datetime

from ftputil import FTPHost
from ftputil.error import FTPOSError
from sqlalchemy.orm import sessionmaker

from plateypus.backend import DB
from plateypus.models import Metadata


def ftp_connect(server, user, passwd, cwd):
    """Connect to an FTP server, change working dir
    and return FTPHost object."""
    try:
        ftp = FTPHost(server, user, passwd)
        ftp.chdir(cwd)
        return ftp
    except FTPOSError:
        return None


def ls_lt(ftp):
    """Return directory listing from FTP connection,
    sorted by time modified."""
    files = [(ftp.stat(f), f) for f in ftp.listdir(ftp.curdir)]
    files.sort(key=lambda fil: fil[0].st_mtime)
    return files


def newer_than_latest(country, timestamp):
    """Check whether the given timestamp is newer
    than the last downloaded dump for country."""
    with sessionmaker(bind=DB.engine)() as session:
        last_updated = session.query(Metadata) \
            .filter_by(country=country)        \
            .first()                           \
            .last_updated or datetime.min
        return timestamp > last_updated
