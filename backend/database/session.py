from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from backend.models.db import Base

DATABASE_URL = "sqlite:///./landsense.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    observation_columns = []
    if inspector.has_table("observations"):
        observation_columns = [column["name"] for column in inspector.get_columns("observations")]
    if "observations" in inspector.get_table_names() and "owner_id" not in observation_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE observations ADD COLUMN owner_id VARCHAR"))
    if "observations" in inspector.get_table_names() and "opencv_analysis_json" not in observation_columns:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE observations ADD COLUMN opencv_analysis_json TEXT DEFAULT '{}'"))
