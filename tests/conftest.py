"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock, patch
from typing import Generator


@pytest.fixture
def mock_komorebi_client() -> Mock:
    """Mock Komorebi client for testing."""
    mock_client = Mock()
    mock_client.get_monitors.return_value = [
        {"index": 1, "name": "Monitor 1"},
        {"index": 2, "name": "Monitor 2"}
    ]
    mock_client.get_workspaces.return_value = [
        {"index": 1, "name": "Work"},
        {"index": 2, "name": "Personal"},
        {"index": 3, "name": "Gaming"}
    ]
    return mock_client


@pytest.fixture
def mock_qt_app() -> Generator[Mock, None, None]:
    """Mock Qt application for testing."""
    with patch("PyQt6.QtWidgets.QApplication") as mock_app:
        mock_app.instance.return_value = Mock()
        yield mock_app


@pytest.fixture
def sample_workspace_data() -> dict:
    """Sample workspace data for testing."""
    return {
        "monitor": 1,
        "workspace": 2,
        "name": "Work",
        "active": True
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Add any global test setup here
    pass


@pytest.fixture(autouse=True)
def teardown_test_environment():
    """Cleanup after each test."""
    yield
    # Add any global test cleanup here
    pass 