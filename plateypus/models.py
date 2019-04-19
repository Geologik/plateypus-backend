"""This module contains ORM model definitions."""

from sqlalchemy import TIMESTAMP, BigInteger, Column, Integer, String, Text

from backend import DB


class Metadata(DB.Model):
    """Represents metadata for the application state."""

    __tablename__ = "plateypus_metadata"

    id = Column(Integer, primary_key=True)
    country = Column(String(2), unique=True)
    last_updated = Column(TIMESTAMP(timezone=True))

    def __repr__(self):
        return f"<Metadata {self.country}[{self.last_updated}]>"


class Vehicle(DB.Model):
    """Represents a vehicle."""

    __tablename__ = "plateypus_vehicle"

    id = Column(BigInteger, primary_key=True)
    country = Column(String(2))
    plate = Column(String(24))
    first_reg = Column(String(24))
    vin = Column(String(24))
    maker = Column(String(128))
    model = Column(String(128))
    fuel_type = Column(String(128))
    colour = Column(String(128))
    raw_xml = Column(Text)

    def __repr__(self):
        return f"<Vehicle {self.country}[{self.plate}]>"


if __name__ == "__main__":
    DB.create_all()  # pragma: no cover
