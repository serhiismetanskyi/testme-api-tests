"""Test case list API tests."""

import pytest

from api.test_cases_client import TestCasesClient
from utils.assertions import assert_status_code


@pytest.mark.tests
@pytest.mark.smoke
@pytest.mark.positive
class TestGetListsPositive:
    """Test case list retrieval scenarios."""

    def test_get_test_list_without_params(self, authenticated_test_client: TestCasesClient):
        """Test getting test list without pagination parameters."""
        response = authenticated_test_client.get_test_list()

        assert_status_code(response, 200)
        try:
            parsed_list = TestCasesClient.parse_test_list(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse test list response: {e}")

        assert isinstance(parsed_list, list), "Parsed tests should be a list"
        tests_count = len(parsed_list)

        response_data = response.json()
        page = response_data.get("page")
        size = response_data.get("size")
        total = response_data.get("total")

        assert page == 0, f"Expected default page 0, got {page}"
        assert size == 20, f"Expected default size 20, got {size}"
        assert isinstance(total, int), f"Total should be integer, got {total}"
        assert tests_count <= size, f"Number of tests should not exceed page size ({size})"

    def test_get_test_list_with_pagination(self, authenticated_test_client: TestCasesClient):
        """Test getting test list with pagination."""
        page = 1
        size = 5

        response = authenticated_test_client.get_test_list(page=page, size=size)

        assert_status_code(response, 200)
        try:
            parsed_list = TestCasesClient.parse_test_list(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse test list response: {e}")

        assert isinstance(parsed_list, list), "Parsed tests should be a list"
        tests_count = len(parsed_list)

        response_data = response.json()
        response_page = response_data.get("page")
        response_size = response_data.get("size")
        total = response_data.get("total")

        assert response_page == page, f"Expected page {page}, got {response_page}"
        assert response_size == size, f"Expected size {size}, got {response_size}"
        assert isinstance(total, int), f"Total should be integer, got {total}"
        assert tests_count <= size, f"Number of tests should not exceed page size ({size})"

    def test_get_test_list_with_small_page_size(self, authenticated_test_client: TestCasesClient):
        """Test getting test list with small page size."""
        page = 1
        size = 1

        response = authenticated_test_client.get_test_list(page=page, size=size)

        assert_status_code(response, 200)
        try:
            parsed_list = TestCasesClient.parse_test_list(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse test list response: {e}")

        assert isinstance(parsed_list, list), "Parsed tests should be a list"
        tests_count = len(parsed_list)

        response_data = response.json()
        response_page = response_data.get("page")
        response_size = response_data.get("size")
        total = response_data.get("total")

        assert response_page == page, f"Expected page {page}, got {response_page}"
        assert response_size == size, f"Expected size {size}, got {response_size}"
        assert isinstance(total, int), f"Total should be integer, got {total}"
        assert tests_count <= size, f"Number of tests should not exceed page size ({size})"

    @pytest.mark.parametrize(
        "page,size",
        [
            (1, 1),
            (1, 5),
            (1, 10),
            (2, 3),
            (2, 5),
            (3, 2),
        ],
    )
    def test_get_list_with_pagination_params(self, authenticated_test_client: TestCasesClient, page: int, size: int):
        """Test getting list with various pagination parameters."""
        response = authenticated_test_client.get_test_list(page=page, size=size)

        assert_status_code(response, 200)
        try:
            parsed_list = TestCasesClient.parse_test_list(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse test list response: {e}")

        assert isinstance(parsed_list, list), "Parsed tests should be a list"
        tests_count = len(parsed_list)

        response_data = response.json()
        response_page = response_data.get("page")
        response_size = response_data.get("size")
        total = response_data.get("total")

        assert response_page == page, f"Expected page {page}, got {response_page}"
        assert response_size == size, f"Expected size {size}, got {response_size}"
        assert isinstance(total, int), f"Total should be integer, got {total}"
        assert tests_count <= size, f"Number of tests should not exceed page size ({size})"


@pytest.mark.tests
@pytest.mark.negative
class TestGetListsNegative:
    """Negative test list retrieval scenarios."""

    def test_get_test_list_without_authentication(self, test_cases_client: TestCasesClient):
        """Test getting test list without authentication."""
        response = test_cases_client.get_test_list()

        assert_status_code(response, 403)
