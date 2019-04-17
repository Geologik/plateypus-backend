"""Load data from the Danish Motor Register (DMR)."""

from datetime import datetime, timezone as tz
from io import TextIOWrapper
from os.path import join as path_join
from re import search
from tempfile import gettempdir
from warnings import warn
from xml.etree.ElementTree import XMLPullParser, tostring
from zipfile import ZipFile, is_zipfile

from ftputil.file_transfer import MAX_COPY_CHUNK_SIZE
from progress.bar import Bar
from progress.spinner import Spinner
from requests import get
from requests.exceptions import ConnectionError as RequestsConnectionError
from sqlalchemy.orm import sessionmaker

from plateypus.backend import DB
from plateypus.models import Metadata, Vehicle
from etl_utils import ftp_connect, ls_lt, newer_than_latest


def extract_transform_load():
    """Update DMR entries if newer data dump exists."""
    dump, last_updated = Extract().download_if_newer()
    if not dump:
        print('No newer file found. Exiting.')
        return False
    entities = Transform(dump).build_from_xml()
    if not entities:
        print('No entities parsed from data dump. Exiting.')
        return False
    if not Load().insert(entities, last_updated):
        print('No data loaded. Exiting.')
    print('Done.')
    return True


class Extract(object):
    """Methods to extract data from the DMR."""

    METADATA_URL = 'http://datahub.virk.dk/api/2/rest/package/k-ret-jsdata'

    ftp = None

    def __init__(self):
        self.open_dmr_ftp()

    def __del__(self):
        if self.ftp:
            self.ftp.close()

    def download_if_newer(self):
        """Download latest zipped dump from the DMR
        if newer than the last downloaded."""

        newest_file = ls_lt(self.ftp)[-1]
        filename = newest_file[1]
        last_modified = datetime.fromtimestamp(newest_file[0].st_mtime, tz.utc)
        return '/mnt/c/Temp/test.zip', last_modified
        # return '/mnt/c/Temp/ESStatistikListeModtag-20181015-070837.zip'
        chunks = round(newest_file[0].st_size / MAX_COPY_CHUNK_SIZE)
        if newer_than_latest('dk', last_modified):
            target = path_join(gettempdir(), filename)
            indicator = '%(percent).1f%% (done in %(eta_td)s)'
            progbar = Bar(f'Downloading {filename}',
                          max=chunks, suffix=indicator)
            self.ftp.download(filename, target, lambda chunk: progbar.next())
            progbar.finish()
            return target, last_modified
        return False, datetime.min

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
            return None  # Network connection issue. Hopefully transient!
        except KeyError:
            return None  # Metadata format probably changed…

    def open_dmr_ftp(self):
        """Connect to the DMR FTP server and set the FTPHost."""
        ftp_conn_data = self.get_ftp_connection_data()
        self.ftp = ftp_conn_data and ftp_connect(**ftp_conn_data)


class Transform(object):
    """Methods to transform extracted data into loadable form."""

    def __init__(self, path_to_dump):
        self.dump = path_to_dump

    def build_from_xml(self):
        """Return a list of entities from the data dump."""
        nsmap = {}
        entities = []

        # TODO move to utils
        def get_node_text(elem, node_name):
            xpath = f'.//ns:{node_name}'
            count = len(elem.findall(xpath, namespaces=nsmap)) == 1
            if count == 0:
                warn(f'Did not find {node_name}')
                return ''
            if count > 1:
                warn(f'Found #{count}# {node_name}')
            return elem.findtext(xpath, namespaces=nsmap)

        for event, elem in self.xml_pull_events():
            if event == 'start-ns':
                namespace, url = elem
                nsmap[namespace] = url
            if event == 'end':
                if elem.tag == f'{{{nsmap["ns"]}}}Statistik':
                    vehicle = Vehicle(
                        country='dk',
                        plate=get_node_text(
                            elem, 'RegistreringNummerNummer'),
                        first_reg=get_node_text(
                            elem, 'KoeretoejOplysningFoersteRegistreringDato'),
                        vin=get_node_text(
                            elem, 'KoeretoejOplysningStelNummer'),
                        maker=get_node_text(
                            elem, 'KoeretoejMaerkeTypeNavn'),
                        model='{} {}'.format(
                            get_node_text(elem, 'KoeretoejModelTypeNavn'),
                            get_node_text(elem, 'KoeretoejVariantTypeNavn')),
                        fuel_type=get_node_text(
                            elem, 'DrivkraftTypeNavn'),
                        colour=get_node_text(
                            elem, 'FarveTypeNavn'),
                        raw_xml=tostring(elem, encoding='unicode'))
                    print(vehicle)
                    entities.append(vehicle)
                    elem.clear()
        return entities

    def xml_pull_events(self):
        """Return a list of XML parser events from the data dump."""
        parser = XMLPullParser(['start-ns', 'end'])
        spinner = Spinner('Parsing XML dump … ')
        spinner.next()
        with self.xml_stream() as instream:
            for _, line in enumerate(instream):
                spinner.next()
                parser.feed(line)
            print('\bdone.')
            parser.close()
            spinner.finish()
            return parser.read_events()

    def xml_stream(self):
        """Open one-file archive and return a buffered stream
        suitable for plugging into a pull parser."""
        if is_zipfile(self.dump):
            with ZipFile(self.dump, 'r') as zipf:
                infolist = zipf.infolist()
                if len(infolist) == 1:
                    return TextIOWrapper(zipf.open(infolist[0].filename, 'r'))
        return None


class Load(object):
    """Methods to insert data into the database."""

    def __init__(self):
        self.session = sessionmaker(bind=DB.engine)()

    def clean(self):
        """Delete all Danish vehicles."""
        count = self.session.query(Vehicle)  \
                    .filter_by(country='dk') \
                    .delete(synchronize_session=False)
        self.session.commit()
        print(f'> deleted {count} vehicles')

    def insert(self, entities, last_updated):
        """Insert entities into database."""
        self.clean()

        self.session.add_all(entities)
        self.session.commit()
        print(f'> inserted {len(entities)} vehicles')

        dk_meta = self.session.query(Metadata).filter_by(country='dk').first()
        if dk_meta:
            dk_meta.last_updated = last_updated
        else:
            self.session.add(Metadata(country='dk', last_updated=last_updated))
        self.session.commit()

        return True


if __name__ == '__main__':
    extract_transform_load()  # pragma: no cover
