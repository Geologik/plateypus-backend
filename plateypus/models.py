"""ODM model definitions."""

from elasticsearch_dsl import Date, Document, Keyword, Text

try:
    from helpers import elastic
except (ImportError, ModuleNotFoundError):  # pragma: no cover
    from plateypus.helpers import elastic


INDEX_METADATA = "plateypus-metadata"
INDEX_VEHICLES = "plateypus-vehicles"


class Metadata(Document):
    """Represents metadata for the application state."""

    country = Keyword(required=True)
    last_updated = Date()

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = INDEX_METADATA


class Vehicle(Document):
    """Represents a vehicle."""

    country = Keyword(required=True)
    plate = Text(required=True)
    first_reg = Text()
    vin = Text()
    maker = Text()
    model = Text()
    fuel_type = Text()
    colour = Text()
    raw_xml = Text()

    class Index:  # pylint: disable=missing-docstring,too-few-public-methods
        name = INDEX_VEHICLES


if __name__ == "__main__":  # pragma: no cover
    with elastic() as client:
        Metadata.init(using=client)
        Vehicle.init(using=client)
