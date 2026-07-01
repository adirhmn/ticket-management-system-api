from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# NOTE: SQLite is used as a lightweight database engine for the Pytest unit testing suite (see tests/conftest.py).
# Injects 'check_same_thread=False' to allow FastAPI's asynchronous/multi-threaded request workers 
# to access the temporary SQLite database safely without blocking.
connect_args = {}
if settings.sqlalchemy_database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False



engine = create_engine(
    settings.sqlalchemy_database_url,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
