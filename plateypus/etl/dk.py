"""Load data from the Danish Motor Register (DMR)."""

from datetime import datetime, timezone as tz
from os.path import join as path_join
from re import search
from tempfile import gettempdir

from ftputil import FTPHost
from ftputil.file_transfer import MAX_COPY_CHUNK_SIZE
from progress.bar import Bar
from requests import get

METADATA_URL = 'http://datahub.virk.dk/api/2/rest/package/k-ret-jsdata'


def dmr_ftp():
    """Connect to the DMR FTP server and return an FTPHost."""
    ftp_conn = _ftp_connection_data()
    if ftp_conn is None:
        return None
    ftp = FTPHost(**ftp_conn['login'])
    ftp.chdir(ftp_conn['cwd'])
    return ftp


def ls_lt(ftp):
    """Return directory listing sorted by time from FTP connection."""
    files = [(ftp.stat(f), f) for f in ftp.listdir(ftp.curdir)]
    files.sort(key=lambda fil: fil[0].st_mtime)
    return files



def update_data():
    """Update DMR entries if newer data dump exists."""
    fil = _download_if_newer()
    if not fil:
        print('No newer file found. Exiting.')
    ## TODO Process file and insert into database
    print('Done.')


def _download_if_newer():
    """Download latest zipped dump from the DMR if newer than the last downloaded."""
    with dmr_ftp() as ftp:
        newest_file = ls_lt(ftp).pop()
        filename = newest_file[1]
        last_modified = datetime.fromtimestamp(newest_file[0].st_mtime, tz.utc)
        chunks = round(newest_file[0].st_size / MAX_COPY_CHUNK_SIZE)
        if _newer_than_latest(last_modified):
            target = path_join(gettempdir(), filename)
            indicator = '%(percent).1f%% (done in %(eta_td)s)'
            progbar = Bar('Downloading {}'.format(filename), max=chunks, suffix=indicator)
            dmr_ftp().download(filename, target, lambda chunk: progbar.next())
            progbar.finish()
            return target
        return False


def _ftp_connection_data():
    """Retrieve FTP details for the DMR from the Virk Datahub."""
    try:
        resp = get(METADATA_URL)
        metadata = resp.json()
        conn = metadata['resources'][1]['url']
        tokens = search(r'^ftp://([^:]+):([^@]+)@([^/]+)/([^/]+)/$', conn)

        if not tokens:
            return None

        def tok(num):
            return tokens.group(num)

        return dict(login=dict(user=tok(1), passwd=tok(2), host=tok(3)), cwd=tok(4))
    except ConnectionError:
        return None # Network connection issue. Hopefully transient!
    except KeyError:
        return None # Metadata format probably changed...


def _newer_than_latest(timestamp):
    """Check whether the given timestamp is newer than the last downloaded dump."""
    ## TODO Implement when database is done
    return timestamp < datetime.now(tz.utc)

if __name__ == '__main__':
    update_data()
