import os
import sys
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Ensure backend package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.base import Base
from app.db.database import get_db
from app.core import security
from app.models.enums import UserRole

# Import all models to register them with Base.metadata before create_all
from app.models.camera import Camera  # noqa: F401
from app.models.zone import Zone  # noqa: F401
from app.models.event import Event  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.evidence import Evidence  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401

# Create unified test SQLite in-memory engine with StaticPool to persist tables across connections
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=test_engine)
    
    # Seed users for testing each role
    db = TestingSessionLocal()
    users = [
        User(
            id="admin-uuid-000",
            username="admin",
            email="admin@ibvap.local",
            password_hash=security.hash_password("Admin@123"),
            role=UserRole.OPERATOR,
            is_active=True,
            mfa_enabled=False
        ),
        User(
            id="admin-uuid-001",
            username="admin_user",
            email="admin@ibvap.test",
            password_hash=security.hash_password("AdminSecret123!"),
            role=UserRole.ADMINISTRATOR,
            is_active=True,
            mfa_enabled=False
        ),
        User(
            id="operator-uuid-001",
            username="operator_user",
            email="operator@ibvap.test",
            password_hash=security.hash_password("OperatorSecret123!"),
            role=UserRole.OPERATOR,
            is_active=True
        ),
        User(
            id="analyst-uuid-001",
            username="analyst_user",
            email="analyst@ibvap.test",
            password_hash=security.hash_password("AnalystSecret123!"),
            role=UserRole.ANALYST,
            is_active=True
        ),
        User(
            id="auditor-uuid-001",
            username="auditor_user",
            email="auditor@ibvap.test",
            password_hash=security.hash_password("AuditorSecret123!"),
            role=UserRole.AUDITOR,
            is_active=True
        ),
        User(
            id="inactive-uuid-001",
            username="inactive_user",
            email="inactive@ibvap.test",
            password_hash=security.hash_password("InactiveSecret123!"),
            role=UserRole.OPERATOR,
            is_active=False
        )
    ]
    for u in users:
        db.add(u)
    db.commit()
    db.close()

    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="module")
def unauthenticated_client() -> Generator[TestClient, None, None]:
    """Unauthenticated TestClient fixture."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def admin_client(unauthenticated_client: TestClient) -> TestClient:
    """Authenticated TestClient as ADMINISTRATOR."""
    token = security.create_access_token({"sub": "admin-uuid-001", "username": "admin_user", "role": "ADMINISTRATOR"})
    unauthenticated_client.headers["Authorization"] = f"Bearer {token}"
    return unauthenticated_client


@pytest.fixture(scope="module")
def operator_client(unauthenticated_client: TestClient) -> TestClient:
    """Authenticated TestClient as OPERATOR."""
    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db
    token = security.create_access_token({"sub": "operator-uuid-001", "username": "operator_user", "role": "OPERATOR"})
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture(scope="module")
def analyst_client(unauthenticated_client: TestClient) -> TestClient:
    """Authenticated TestClient as ANALYST."""
    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db
    token = security.create_access_token({"sub": "analyst-uuid-001", "username": "analyst_user", "role": "ANALYST"})
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture(scope="module")
def auditor_client(unauthenticated_client: TestClient) -> TestClient:
    """Authenticated TestClient as AUDITOR."""
    client = TestClient(app)
    app.dependency_overrides[get_db] = override_get_db
    token = security.create_access_token({"sub": "auditor-uuid-001", "username": "auditor_user", "role": "AUDITOR"})
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture(scope="module")
def client(admin_client: TestClient) -> TestClient:
    """
    Default `client` fixture alias for backward compatibility with existing tests,
    authenticated as ADMINISTRATOR.
    """
    return admin_client


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    SQLite in-memory session fixture for model unit testing.
    Creates schema tables before each test and drops them afterwards.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
