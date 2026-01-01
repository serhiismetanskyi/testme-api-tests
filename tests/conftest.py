"""Pytest configuration and fixtures."""

import pytest
from playwright.sync_api import APIRequestContext, Playwright

from api.auth_client import AuthClient
from api.stats_client import StatsClient
from api.test_cases_client import TestCasesClient
from config import settings
from data.factories import TestDataFactory
from utils.logger import get_logger

logger = get_logger(__name__, settings.log_level)


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> APIRequestContext:
    """Create API request context for the session."""
    request_context = playwright.request.new_context(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
    )
    yield request_context
    request_context.dispose()


@pytest.fixture(scope="function")
def auth_client(api_request_context: APIRequestContext) -> AuthClient:
    """Create authentication client."""
    return AuthClient(api_request_context)


@pytest.fixture(scope="function")
def test_cases_client(api_request_context: APIRequestContext) -> TestCasesClient:
    """Create test cases client."""
    return TestCasesClient(api_request_context)


@pytest.fixture(scope="function")
def stats_client(api_request_context: APIRequestContext) -> StatsClient:
    """Create statistics client."""
    return StatsClient(api_request_context)


@pytest.fixture(scope="function")
def authenticated_client(auth_client: AuthClient) -> AuthClient:
    """Create authenticated client with logged-in user."""
    response = auth_client.login(settings.test_username, settings.test_password)
    logger.info(f"Login status: {response.status}")

    yield auth_client

    try:
        logout_response = auth_client.logout()
        logger.info(f"Logout status: {logout_response.status}")
    except Exception as e:
        logger.warning(f"Logout failed: {e}")


@pytest.fixture(scope="function")
def authenticated_test_client(
    authenticated_client: AuthClient,
    test_cases_client: TestCasesClient,
) -> TestCasesClient:
    """Create test cases client with authentication token."""
    test_cases_client.csrf_token = authenticated_client.csrf_token
    return test_cases_client


@pytest.fixture(scope="function")
def authenticated_stats_client(
    authenticated_client: AuthClient,
    stats_client: StatsClient,
) -> StatsClient:
    """Create stats client with authentication token."""
    stats_client.csrf_token = authenticated_client.csrf_token
    return stats_client


@pytest.fixture(scope="function")
def created_test_id(authenticated_test_client: TestCasesClient) -> int:
    """Create a test case and return its ID, cleanup after test."""
    test_data = TestDataFactory.generate_random_test_data()
    response = authenticated_test_client.create_test(test_data["name"], test_data["description"])
    if response.status != 201:
        raise ValueError(f"Failed to create test. Response status: {response.status}, body: {response.text()}")
    create_data = TestCasesClient.parse_create_response(response)
    test_id = create_data.test_id

    logger.info(f"Created test with ID: {test_id}")
    yield test_id

    try:
        delete_response = authenticated_test_client.delete_test(test_id)
        logger.info(f"Deleted test {test_id}, status: {delete_response.status}")
    except Exception as e:
        logger.warning(f"Failed to delete test {test_id}: {e}")
