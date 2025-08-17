"""
Pytest configuration and common fixtures for AI Health Navigator tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ai_health_navigator.api.main import app
from ai_health_navigator.database.session import get_db
from ai_health_navigator.database.models import Base
from ai_health_navigator.core.config import settings


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """Create a test client with a fresh database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "phone": "+1234567890"
    }


@pytest.fixture
def sample_symptom_data():
    """Sample symptom data for testing."""
    return {
        "symptoms": ["headache", "fever"],
        "severity": "moderate",
        "duration": "2 days",
        "additional_notes": "Started after a cold"
    }


@pytest.fixture
def sample_triage_data():
    """Sample triage data for testing."""
    return {
        "symptoms": ["chest pain", "shortness of breath"],
        "severity": "severe",
        "duration": "30 minutes",
        "age": 45,
        "gender": "male",
        "medical_history": ["hypertension"]
    }
