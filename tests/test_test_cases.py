"""Test cases CRUD API tests."""

import pytest

from api.test_cases_client import TestCasesClient
from config import settings
from data.factories import TestDataFactory
from models.error import ErrorMessage, ErrorResponse
from models.test_case import TestStatus
from utils.assertions import assert_status_code


@pytest.mark.tests
@pytest.mark.smoke
@pytest.mark.positive
class TestCreateTestCasePositive:
    """Test case creation scenarios."""

    def test_create_test_case_with_valid_data(self, authenticated_test_client: TestCasesClient):
        """Test creating a test case with valid data."""
        test_data = TestDataFactory.generate_random_test_data()

        response = authenticated_test_client.create_test(test_data["name"], test_data["description"])

        assert_status_code(response, 201)
        try:
            create_response = TestCasesClient.parse_create_response(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse create response: {e}")

        assert create_response.test_id is not None, "Test ID should be returned"
        assert isinstance(create_response.test_id, int), "Test ID should be an integer"

        authenticated_test_client.delete_test(create_response.test_id)

    def test_create_test_case_with_long_name(self, authenticated_test_client: TestCasesClient):
        """Test creating a test case with long name (max_length=100)."""
        long_name = "A" * 100
        description = "Test description"

        response = authenticated_test_client.create_test(long_name, description)

        assert_status_code(response, 201)
        try:
            create_response = TestCasesClient.parse_create_response(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse create response: {e}")

        authenticated_test_client.delete_test(create_response.test_id)

    def test_create_test_case_with_long_description(self, authenticated_test_client: TestCasesClient):
        """Test creating a test case with long description."""
        name = TestDataFactory.generate_test_name()
        # Use maximum allowed length (1000 characters) to stay within model constraints
        long_description = "D" * 1000

        response = authenticated_test_client.create_test(name, long_description)

        assert_status_code(response, 201)
        try:
            create_response = TestCasesClient.parse_create_response(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse create response: {e}")

        authenticated_test_client.delete_test(create_response.test_id)


@pytest.mark.tests
@pytest.mark.negative
class TestCreateTestCaseNegative:
    """Negative test case creation scenarios."""

    def test_create_test_without_authentication(self, test_cases_client: TestCasesClient):
        """Test creating a test case without authentication."""
        test_data = TestDataFactory.generate_random_test_data()

        response = test_cases_client.create_test(test_data["name"], test_data["description"])

        assert_status_code(response, 403)

    def test_create_test_with_empty_name(self, authenticated_test_client: TestCasesClient):
        """Test creating a test case with empty name."""
        name = ""
        description = "Valid description"

        # Bypass Pydantic validation by calling API directly with empty name
        response = authenticated_test_client.post(
            url=settings.tests_new_url,
            data={"name": name, "description": description},
        )
        assert_status_code(response, 400)
        try:
            response_data = response.json()
            error_response = ErrorResponse.parse_error_response(response_data)
            assert error_response.error == ErrorMessage.BAD_INPUT_DATA.value
        except (ValueError, TypeError) as e:
            pytest.fail(f"Failed to parse error response: {e}")

    def test_create_test_with_empty_description(self, authenticated_test_client: TestCasesClient):
        """Test creating a test case with empty description."""
        name = TestDataFactory.generate_test_name()
        description = ""

        # Bypass Pydantic validation by calling API directly with empty description
        response = authenticated_test_client.post(
            url=settings.tests_new_url,
            data={"name": name, "description": description},
        )
        assert_status_code(response, 400)
        try:
            response_data = response.json()
            error_response = ErrorResponse.parse_error_response(response_data)
            assert error_response.error == ErrorMessage.BAD_INPUT_DATA.value
        except (ValueError, TypeError) as e:
            pytest.fail(f"Failed to parse error response: {e}")


@pytest.mark.tests
@pytest.mark.smoke
@pytest.mark.positive
class TestGetTestCasePositive:
    """Test case retrieval scenarios."""

    def test_get_test_case_by_id(self, authenticated_test_client: TestCasesClient, created_test_id: int):
        """Test getting a test case by ID."""
        response = authenticated_test_client.get_test_by_id(created_test_id)

        assert_status_code(response, 200)
        try:
            test_case = TestCasesClient.parse_test_case(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse test case response: {e}")

        assert test_case.id == created_test_id, "Returned test should match requested ID"


@pytest.mark.tests
@pytest.mark.negative
class TestGetTestCaseNegative:
    """Negative test case retrieval scenarios."""

    def test_get_test_case_without_authentication(self, test_cases_client: TestCasesClient):
        """Test getting a test case without authentication."""
        test_id = 999999

        response = test_cases_client.get_test_by_id(test_id)

        assert_status_code(response, 403)

    def test_get_non_existent_test_case(self, authenticated_test_client: TestCasesClient):
        """Test getting a non-existent test case."""
        non_existent_test_id = 999999

        response = authenticated_test_client.get_test_by_id(non_existent_test_id)

        assert_status_code(response, 404)

    def test_get_test_with_invalid_id_format(self, authenticated_test_client: TestCasesClient):
        """Test getting a test case with invalid ID format."""
        invalid_test_id = "INVALID_TEST_ID"

        response = authenticated_test_client.get_test_by_id(invalid_test_id)

        assert_status_code(response, 404)


@pytest.mark.tests
@pytest.mark.smoke
@pytest.mark.positive
class TestUpdateTestCasePositive:
    """Test case update scenarios."""

    def test_full_update_test_case(self, authenticated_test_client: TestCasesClient, created_test_id: int):
        """Test full update (PUT) of a test case."""
        new_name = TestDataFactory.generate_test_name("Updated Test")
        new_description = "Updated description"

        response = authenticated_test_client.update_test(created_test_id, new_name, new_description)

        assert_status_code(response, 200)
        try:
            updated_test = TestCasesClient.parse_update_response(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse update response: {e}")

        assert updated_test.id == created_test_id, f"ID should match: {created_test_id}"
        assert updated_test.name == new_name, f"Name should be updated to {new_name}"
        assert updated_test.description == new_description, f"Description should be updated to {new_description}"
        assert updated_test.author is not None, "Author should be present"

        get_response = authenticated_test_client.get_test_by_id(created_test_id)
        assert_status_code(get_response, 200)
        try:
            persisted_test = TestCasesClient.parse_test_case(get_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse persisted test response: {e}")

        assert persisted_test.name == new_name, "Persisted name should match updated value"
        assert persisted_test.description == new_description, "Persisted description should match updated value"

    def test_partial_update_test_description(self, authenticated_test_client: TestCasesClient, created_test_id: int):
        """Test partial update (PATCH) of test description only."""
        new_description = "Partially updated description"

        response = authenticated_test_client.partial_update_test(created_test_id, description=new_description)

        assert_status_code(response, 200)
        try:
            updated_test = TestCasesClient.parse_update_response(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse update response: {e}")

        assert updated_test.id == created_test_id, f"ID should match: {created_test_id}"
        assert updated_test.description == new_description, "Description should be updated"
        assert updated_test.author is not None, "Author should be present"

        get_response = authenticated_test_client.get_test_by_id(created_test_id)
        assert_status_code(get_response, 200)
        try:
            persisted_test = TestCasesClient.parse_test_case(get_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse persisted test response: {e}")

        assert persisted_test.description == new_description, "Persisted description should match updated value"

    def test_partial_update_test_name(self, authenticated_test_client: TestCasesClient, created_test_id: int):
        """Test partial update (PATCH) of test name only."""
        new_name = TestDataFactory.generate_test_name("Patched Test")

        response = authenticated_test_client.partial_update_test(created_test_id, name=new_name)

        assert_status_code(response, 200)
        try:
            updated_test = TestCasesClient.parse_update_response(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse update response: {e}")

        assert updated_test.id == created_test_id, f"ID should match: {created_test_id}"
        assert updated_test.name == new_name, "Name should be updated"
        assert updated_test.author is not None, "Author should be present"

        get_response = authenticated_test_client.get_test_by_id(created_test_id)
        assert_status_code(get_response, 200)
        try:
            persisted_test = TestCasesClient.parse_test_case(get_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse persisted test response: {e}")

        assert persisted_test.name == new_name, "Persisted name should match updated value"


@pytest.mark.tests
@pytest.mark.negative
class TestUpdateTestCaseNegative:
    """Negative test case update scenarios."""

    def test_update_test_without_authentication(self, test_cases_client: TestCasesClient):
        """Test updating a test case without authentication."""
        test_id = 999999
        new_name = "Updated name"
        new_description = "Updated description"

        response = test_cases_client.update_test(test_id, new_name, new_description)

        assert_status_code(response, 403)

    def test_update_non_existent_test(self, authenticated_test_client: TestCasesClient):
        """Test updating a non-existent test case."""
        non_existent_test_id = 999999
        new_name = "Updated name"
        new_description = "Updated description"

        response = authenticated_test_client.update_test(non_existent_test_id, new_name, new_description)

        assert_status_code(response, 404)


@pytest.mark.tests
@pytest.mark.smoke
@pytest.mark.positive
class TestSetTestStatusPositive:
    """Test status setting scenarios."""

    @pytest.mark.parametrize(
        "status",
        [TestStatus.PASS.value, TestStatus.FAIL.value],
    )
    def test_set_test_status(self, authenticated_test_client: TestCasesClient, created_test_id: int, status: str):
        """Test setting various test statuses."""
        response = authenticated_test_client.set_test_status(created_test_id, status)

        assert_status_code(response, 200)
        try:
            status_response = TestCasesClient.parse_set_status_response(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse set status response: {e}")

        assert status_response.runId is not None, "Response should contain runId"
        assert isinstance(status_response.runId, int), "runId should be an integer"

        get_response = authenticated_test_client.get_test_by_id(created_test_id)
        assert_status_code(get_response, 200)
        try:
            persisted_test = TestCasesClient.parse_test_case(get_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse persisted test response after status update: {e}")

        assert persisted_test.status == status, "Persisted status should match updated value"


@pytest.mark.tests
@pytest.mark.negative
class TestSetTestStatusNegative:
    """Negative test status setting scenarios."""

    def test_set_test_status_without_authentication(self, test_cases_client: TestCasesClient):
        """Test setting test status without authentication."""
        test_id = 999999
        status = TestStatus.PASS.value

        response = test_cases_client.set_test_status(test_id, status)

        assert_status_code(response, 403)

    def test_set_invalid_test_status(self, authenticated_test_client: TestCasesClient, created_test_id: int):
        """Test setting invalid test status."""
        invalid_status = "INVALID_STATUS"

        response = authenticated_test_client.set_test_status(created_test_id, invalid_status)

        assert_status_code(response, 200)


@pytest.mark.tests
@pytest.mark.smoke
@pytest.mark.positive
class TestDeleteTestCasePositive:
    """Positive test case deletion scenarios."""

    def test_delete_test_case(self, authenticated_test_client: TestCasesClient):
        """Test deleting a test case."""
        test_data = TestDataFactory.generate_random_test_data()
        create_response = authenticated_test_client.create_test(test_data["name"], test_data["description"])

        assert_status_code(create_response, 201)
        try:
            create_response_data = TestCasesClient.parse_create_response(create_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse create response: {e}")

        test_id = create_response_data.test_id

        delete_response = authenticated_test_client.delete_test(test_id)

        assert_status_code(delete_response, 200)
        try:
            delete_response_data = delete_response.json()
            assert delete_response_data.get("status") == "deleted", "Response should indicate deletion"
        except ValueError as e:
            pytest.fail(f"Failed to parse delete response JSON: {e}")

        get_response = authenticated_test_client.get_test_by_id(test_id)
        assert_status_code(get_response, 404)


@pytest.mark.tests
@pytest.mark.negative
class TestDeleteTestCaseNegative:
    """Negative test case deletion scenarios."""

    def test_delete_test_without_authentication(self, test_cases_client: TestCasesClient):
        """Test deleting a test case without authentication."""
        test_id = 999999

        response = test_cases_client.delete_test(test_id)

        assert_status_code(response, 403)

    def test_delete_non_existent_test(self, authenticated_test_client: TestCasesClient):
        """Test deleting a non-existent test case."""
        non_existent_test_id = 999999

        response = authenticated_test_client.delete_test(non_existent_test_id)

        assert_status_code(response, 404)

    def test_delete_already_deleted_test(self, authenticated_test_client: TestCasesClient):
        """Test deleting an already deleted test case."""
        test_data = TestDataFactory.generate_random_test_data()

        create_response = authenticated_test_client.create_test(test_data["name"], test_data["description"])

        assert_status_code(create_response, 201)
        try:
            create_response_data = TestCasesClient.parse_create_response(create_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse create response: {e}")

        test_id = create_response_data.test_id

        first_delete_response = authenticated_test_client.delete_test(test_id)

        assert_status_code(first_delete_response, 200)

        second_delete_response = authenticated_test_client.delete_test(test_id)

        assert_status_code(second_delete_response, 404)


@pytest.mark.tests
@pytest.mark.regression
class TestTestCaseWorkflow:
    """Complete test case workflow scenarios."""

    def test_complete_crud_workflow(self, authenticated_test_client: TestCasesClient):
        """Test complete CRUD workflow: Create -> Read -> Update -> Delete."""
        test_data = TestDataFactory.generate_random_test_data()
        create_response = authenticated_test_client.create_test(test_data["name"], test_data["description"])
        assert_status_code(create_response, 201)
        try:
            create_response_data = TestCasesClient.parse_create_response(create_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse create response: {e}")
        test_id = create_response_data.test_id

        get_response = authenticated_test_client.get_test_by_id(test_id)
        assert_status_code(get_response, 200)
        try:
            created_test = TestCasesClient.parse_test_case(get_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse created test response: {e}")

        assert created_test.id == test_id, "Created test ID should match returned ID"
        assert created_test.name == test_data["name"], "Created test name should match input"
        assert created_test.description == test_data["description"], "Created test description should match input"

        new_name = TestDataFactory.generate_test_name("Updated")
        new_description = "Updated description"
        update_response = authenticated_test_client.update_test(test_id, new_name, new_description)
        assert_status_code(update_response, 200)
        try:
            updated_test = TestCasesClient.parse_update_response(update_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse update response: {e}")

        assert updated_test.id == test_id, f"ID should match: {test_id}"
        assert updated_test.name == new_name, f"Name should be updated to {new_name}"
        assert updated_test.description == new_description, f"Description should be updated to {new_description}"

        updated_get_response = authenticated_test_client.get_test_by_id(test_id)
        assert_status_code(updated_get_response, 200)
        try:
            persisted_updated_test = TestCasesClient.parse_test_case(updated_get_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse persisted updated test response: {e}")

        assert persisted_updated_test.name == new_name, "Persisted name should match updated value"
        assert persisted_updated_test.description == new_description, "Persisted description should match updated value"

        status_response = authenticated_test_client.set_test_status(test_id, TestStatus.PASS.value)
        assert_status_code(status_response, 200)
        try:
            status_data = TestCasesClient.parse_set_status_response(status_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse set status response: {e}")

        assert isinstance(status_data.runId, int), "Status change should return runId"

        status_get_response = authenticated_test_client.get_test_by_id(test_id)
        assert_status_code(status_get_response, 200)
        try:
            test_with_status = TestCasesClient.parse_test_case(status_get_response)
        except ValueError as e:
            pytest.fail(f"Failed to parse test with status response: {e}")

        assert test_with_status.status == TestStatus.PASS.value, "Persisted status should match last updated value"

        delete_response = authenticated_test_client.delete_test(test_id)
        assert_status_code(delete_response, 200)
        try:
            delete_response_data = delete_response.json()
            assert delete_response_data.get("status") == "deleted", "Response should indicate deletion"
        except ValueError as e:
            pytest.fail(f"Failed to parse delete response JSON: {e}")

        final_get = authenticated_test_client.get_test_by_id(test_id)
        assert_status_code(final_get, 404)
