import json
from sqlalchemy import Column, String, Float, Integer, TypeDecorator
from .database import Base

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Observation(Base):
    __tablename__ = "observations"

    observation_id = Column(String, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(String, index=True, nullable=False) # Stored as ISO8601 string for easy sorting/filtering
    construction_stage = Column(String, nullable=False)
    progress = Column(Integer, nullable=False)
    dust = Column(Float, nullable=False)
    noise = Column(Float, nullable=False)
    development_score = Column(Integer, nullable=False)
    summary = Column(String, nullable=False)
    embedding = Column(JSONEncodedDict, nullable=False)
