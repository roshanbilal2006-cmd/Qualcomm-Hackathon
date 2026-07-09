import json
from sqlalchemy import Column, String, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DBModelBase(Base):
    __abstract__ = True

class DBObservation(DBModelBase):
    __tablename__ = "observations"

    observation_id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, nullable=True, index=True)
    timestamp = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    images_json = Column(Text, default="[]")  # JSON list of image URIs/Base64
    voice_query = Column(String, nullable=True)
    construction_stage = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    progress = Column(Float, nullable=True)
    noise_db = Column(Float, nullable=True)
    dust_pm25 = Column(Float, nullable=True)
    dust_pm10 = Column(Float, nullable=True)
    sensor_status = Column(String, default="degraded")
    rera_projects_json = Column(Text, default="[]")  # JSON list of matched RERA details
    development_score = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    embedding_json = Column(Text, default="[]")  # JSON list of float vector

    @property
    def images(self):
        return json.loads(self.images_json or "[]")

    @images.setter
    def images(self, value):
        self.images_json = json.dumps(value)

    @property
    def rera_projects(self):
        return json.loads(self.rera_projects_json or "[]")

    @rera_projects.setter
    def rera_projects(self, value):
        self.rera_projects_json = json.dumps(value)

    @property
    def embedding(self):
        return json.loads(self.embedding_json or "[]")

    @embedding.setter
    def embedding(self, value):
        self.embedding_json = json.dumps(value)


class DBReraProject(DBModelBase):
    __tablename__ = "rera_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    builder = Column(String, nullable=False)
    status = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    expected_completion = Column(String, nullable=True)
