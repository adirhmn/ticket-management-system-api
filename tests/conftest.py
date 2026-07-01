import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import Ticket
from app.main import app
from app.config import settings

from sqlalchemy.pool import NullPool

# Use a local file-based SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create all tables in the test database
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test run
        Base.metadata.drop_all(bind=engine)
        # Delete the temp database file
        if os.path.exists("test_temp.db"):
            try:
                os.remove("test_temp.db")
            except Exception:
                pass


@pytest.fixture(scope="function")
def client(db):
    # Override get_db dependency to use the in-memory test database session
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
