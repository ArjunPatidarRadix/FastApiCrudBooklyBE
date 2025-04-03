from src.db.main import get_session
from src.main import app
from unittest.mock import Mock
import pytest
from fastapi.testclient import TestClient
from src.auth.dependencies import RoleChecker, AccessTokenBearer

mock_session = Mock()
mock_user_service = Mock()
mock_book_service = Mock()


def get_mock_session():
    yield mock_session


access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin"])

app.dependency_overrides[get_session] = get_mock_session
app.dependency_overrides[role_checker] = Mock()
app.dependency_overrides[access_token_bearer] = Mock()

# Additional setup for testing here...


@pytest.fixture
def fake_session():
    return mock_session


@pytest.fixture
def fake_user_service():
    return mock_user_service


@pytest.fixture
def fake_book_service():
    return mock_book_service


@pytest.fixture
def test_client():
    return TestClient(app)
