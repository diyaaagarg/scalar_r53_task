import os

os.environ["ROUTE53_DATABASE_URL"] = "sqlite:///./test_route53.db"
os.environ["ROUTE53_SESSION_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, engine
from app.main import app
from app.scripts.seed import seed


@pytest.fixture(autouse=True)
def database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed()
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authenticated_client(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.com", "password": "Password123!"},
    )
    assert response.status_code == 200
    return client
