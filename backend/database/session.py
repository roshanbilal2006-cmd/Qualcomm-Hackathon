from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.db import Base, DBReraProject

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
    db = SessionLocal()
    try:
        # Check if ReraProjects table is empty and seed it
        if db.query(DBReraProject).count() == 0:
            seed_projects = [
                DBReraProject(
                    name="Prestige Kings County",
                    builder="Prestige Group",
                    status="Approved",
                    latitude=12.9718,
                    longitude=77.7505,
                    expected_completion="2027-12-31"
                ),
                DBReraProject(
                    name="Sobha Rose Apartments",
                    builder="Sobha Limited",
                    status="Approved",
                    latitude=12.9698,
                    longitude=77.7499,
                    expected_completion="2026-06-30"
                ),
                DBReraProject(
                    name="Brigade Metropolis",
                    builder="Brigade Enterprises",
                    status="Pending Review",
                    latitude=12.9780,
                    longitude=77.7410,
                    expected_completion="2028-03-31"
                ),
                DBReraProject(
                    name="Nambiar Bellezea",
                    builder="Nambiar Builders",
                    status="Approved",
                    latitude=12.9716,
                    longitude=77.5946,  # Center city mock RERA
                    expected_completion="2027-06-30"
                ),
                DBReraProject(
                    name="Unapproved High-rise Site",
                    builder="Unknown Developer",
                    status="Disputed / Unauthorized",
                    latitude=12.9730,
                    longitude=77.5960,
                    expected_completion="Unknown"
                )
            ]
            db.add_all(seed_projects)
            db.commit()
    finally:
        db.close()
