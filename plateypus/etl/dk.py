"""Load data from the Danish Motor Register (DMR)."""

from datetime import datetime, timezone as tz
from io import TextIOWrapper
from os.path import join as path_join
from re import search
from tempfile import gettempdir
from xml.etree.ElementTree import XMLPullParser
from xml.etree.ElementTree import ParseError, iterparse
from zipfile import ZipFile, is_zipfile

from ftputil.file_transfer import MAX_COPY_CHUNK_SIZE
from progress.bar import Bar
from progress.spinner import Spinner
from requests import get
from requests.exceptions import ConnectionError as RequestsConnectionError

from etl_utils import ftp_connect, ls_lt

def extract_transform_load():
    """Update DMR entries if newer data dump exists."""
    dump = Extract().download_if_newer()
    if not dump:
        print('No newer file found. Exiting.')
        return False
    entities = Transform(dump).build_from_xml()
    if not entities:
        print('No entities parsed from data dump. Exiting.')
        return False
    if not Load().insert(entities):
        print('No data loaded. Exiting.')
    print('Done.')
    return True


class Extract:
    """Methods to extract data from the DMR."""

    METADATA_URL = 'http://datahub.virk.dk/api/2/rest/package/k-ret-jsdata'

    ftp = None

    def __init__(self):
        self.open_dmr_ftp()

    def __del__(self):
        if self.ftp:
            self.ftp.close()

    def download_if_newer(self):
        """Download latest zipped dump from the DMR if newer than the last downloaded."""
        return '/mnt/c/Temp/test.zip'                                   # TODO Delete this line! :)
        return '/mnt/c/Temp/ESStatistikListeModtag-20181015-070837.zip' # TODO Delete this line! :)
        newest_file = ls_lt(self.ftp)[-1]
        filename = newest_file[1]
        last_modified = datetime.fromtimestamp(newest_file[0].st_mtime, tz.utc)
        chunks = round(newest_file[0].st_size / MAX_COPY_CHUNK_SIZE)
        if self.newer_than_latest(last_modified):
            target = path_join(gettempdir(), filename)
            indicator = '%(percent).1f%% (done in %(eta_td)s)'
            progbar = Bar(f'Downloading {filename}', max=chunks, suffix=indicator)
            self.ftp.download(filename, target, lambda chunk: progbar.next())
            progbar.finish()
            return target
        return False

    def get_ftp_connection_data(self):
        """Retrieve FTP details for the DMR from the Virk Datahub."""
        try:
            resp = get(self.METADATA_URL)
            metadata = resp.json()
            conn = metadata['resources'][1]['url']
            tokens = search(r'^ftp://([^:]+):([^@]+)@([^/]+)/([^/]+)/$', conn)

            if not tokens:
                return None

            def tok(num):
                return tokens.group(num)

            return dict(user=tok(1), passwd=tok(2), server=tok(3), cwd=tok(4))
        except RequestsConnectionError:
            return None # Network connection issue. Hopefully transient!
        except KeyError:
            return None # Metadata format probably changed…

    def newer_than_latest(self, timestamp):
        """Check whether the given timestamp is newer than the last downloaded dump."""
        ## TODO Implement when database is done
        return timestamp < datetime.now(tz.utc)

    def open_dmr_ftp(self):
        """Connect to the DMR FTP server and set the FTPHost."""
        ftp_conn_data = self.get_ftp_connection_data()
        self.ftp = ftp_conn_data and ftp_connect(**ftp_conn_data)


class Transform:
    """Methods to transform extracted data into loadable form."""

    def __init__(self, path_to_dump):
        self.dump = path_to_dump

    def build_from_xml(self):
        """Return a list of entities from the data dump."""
        nsmap = {}
        entities = []
        for event, elem in self.xml_pull_events():
            if event == 'start-ns':
                namespace, url = elem
                nsmap[namespace] = url
        return entities

    def xml_pull_events(self):
        """Return a list of XML parser events from the data dump."""
        parser = XMLPullParser(['start', 'end', 'start-ns', 'end-ns'])
        spinner = Spinner('Parsing XML dump … ')
        spinner.next()
        with self.xml_stream() as instream:
            for _, line in enumerate(instream):
                spinner.next()
                parser.feed(line)
            spinner.finish()
            print('\bdone.')
            return parser.read_events()

    def xml_stream(self):
        """Open one-file archive and return a buffered stream
        suitable for plugging into a pull parser."""
        if is_zipfile(self.dump):
            with ZipFile(self.dump, 'r') as archive:
                infolist = archive.infolist()
                if len(infolist) == 1:
                    return TextIOWrapper(archive.open(infolist[0].filename, 'r'))
        return None


class Load:
    """Methods to insert data into the database."""

    def clean(self):
        """Delete all old data."""
        raise NotImplementedError

    def insert(self, entities):
        """Insert entities into database."""
        # TODO: Implement!
        return True

if __name__ == '__main__':
    extract_transform_load()
