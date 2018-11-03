"""This module contains ORM model definitions."""

from sqlalchemy import Column, BigInteger, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql.expression import text as sql_text

from backend import DB


class Metadata(DB.Model):
    """Represents metadata for the application state."""
    __tablename__ = 'plateypus_metadata'

    id = Column(Integer, primary_key=True)
    last_updated = Column(JSON, default=sql_text("'{}'::json"))

    def __repr__(self):
        return f'<Metadata {self.id}>'


class Vehicle(DB.Model):
    """Represents a vehicle."""
    __tablename__ = 'plateypus_vehicle'

    id = Column(BigInteger, primary_key=True)
    plate = Column(String(24))
    vin = Column(String(24))
