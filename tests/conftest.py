"""
Pytest configuration and shared fixtures for all tests.

This file provides:
- Fresh app instances for each test (no state leakage)
- TestClient instances bound to fresh apps
- Sample activities data for testing
"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src.app import create_app, DEFAULT_ACTIVITIES


@pytest.fixture
def app():
    """
    ARRANGE: Provide a fresh FastAPI app instance for each test.
    
    Each test gets its own app instance with a deep copy of DEFAULT_ACTIVITIES,
    ensuring complete test isolation with no shared state between tests.
    """
    fresh_app = create_app(activities_data=deepcopy(DEFAULT_ACTIVITIES))
    yield fresh_app


@pytest.fixture
def client(app):
    """
    ARRANGE: Provide a TestClient bound to a fresh app instance.
    
    This client is connected to the fresh app from the app fixture,
    allowing HTTP-level testing with proper isolation.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    ARRANGE: Provide a deep copy of sample activities data for test setup.
    
    Use this fixture when you need direct access to activities data
    (not via HTTP). Each test gets a fresh copy.
    """
    return deepcopy(DEFAULT_ACTIVITIES)


@pytest.fixture
def empty_app():
    """
    ARRANGE: Provide a FastAPI app instance with no activities.
    
    Useful for testing edge cases with empty data.
    """
    fresh_app = create_app(activities_data={})
    yield fresh_app


@pytest.fixture
def empty_client(empty_app):
    """
    ARRANGE: Provide a TestClient bound to an app with no activities.
    
    Useful for testing error handling with empty activity list.
    """
    return TestClient(empty_app)
