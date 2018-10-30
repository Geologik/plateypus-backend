"""Utility methods for ETL routines."""

from ftputil import FTPHost
from ftputil.error import FTPOSError

def ftp_connect(server, user, passwd, cwd):
    """Connect to an FTP server, change working dir and return FTPHost object."""
    try:
        ftp = FTPHost(server, user, passwd)
        ftp.chdir(cwd)
        return ftp
    except FTPOSError:
        return None

def ls_lt(ftp):
    """Return directory listing from FTP connection, sorted by time modified."""
    files = [(ftp.stat(f), f) for f in ftp.listdir(ftp.curdir)]
    files.sort(key=lambda fil: fil[0].st_mtime)
    return files
