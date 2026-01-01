"""Test cases API client."""

import logging
from typing import Any

from playwright.sync_api import APIResponse

from api.base_client import BaseClient
from config import settings
from models.test_case import (
    CreateTestRequest,
    CreateTestResponse,
    SetTestStatusResponse,
    TestCase,
    TestStatusRequest,
    UpdateTestRequest,
)
from utils.logger import Logger


class TestCasesClient(BaseClient):
    """Client for test case management endpoints."""

    __test__ = False

    def get_test_list(self, page: int | None = None, size: int | None = None) -> APIResponse:
        """Get list of test cases with optional pagination.

        API endpoint: GET /api/tests?page=<int>&size=<int>
        Query params: page (default: 0), size (default: 20)
        Response: {"page": int, "size": int, "total": int, "tests": [...]} with status 200
        """
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        response = self.get(url=settings.tests_url, params=params if params else None)
        Logger.log(
            f"Fetched test list status: {response.status}",
            level=logging.DEBUG,
        )
        return response

    def create_test(self, name: str, description: str) -> APIResponse:
        """Create a new test case.

        API endpoint: POST /api/tests/new
        Request: {"name": str, "description": str}
        Response: {"test_id": int} with status 201
        """
        test_data = CreateTestRequest(name=name, description=description)
        response = self.post(
            url=settings.tests_new_url,
            data=test_data.model_dump(),
        )
        Logger.log(
            f"Create test response status: {response.status}",
            level=logging.DEBUG,
        )
        return response

    def get_test_by_id(self, test_id: int | str) -> APIResponse:
        """Get test case by ID.

        API endpoint: GET /api/tests/<id>
        Response: {"id": int, "name": str, "description": str, "author": str, "status": str, "executor": str} with status 200
        Or empty response with status 404 if not found
        """
        response = self.get(url=settings.get_test_url(str(test_id)))
        Logger.log(
            f"Get test by ID {test_id} status: {response.status}",
            level=logging.DEBUG,
        )
        return response

    def update_test(
        self,
        test_id: int | str,
        name: str,
        description: str,
    ) -> APIResponse:
        """Fully update test case (PUT).

        API endpoint: PUT /api/tests/<id>
        Request: {"name": str, "description": str} - both fields required
        Response: {"id": int, "name": str, "description": str, "author": str} with status 200
        """
        update_data = UpdateTestRequest(name=name, description=description)
        response = self.put(url=settings.get_test_url(str(test_id)), data=update_data.model_dump())
        Logger.log(
            f"Full update test {test_id} status: {response.status}",
            level=logging.DEBUG,
        )
        return response

    def partial_update_test(
        self,
        test_id: int | str,
        name: str | None = None,
        description: str | None = None,
    ) -> APIResponse:
        """Partially update test case (PATCH).

        API endpoint: PATCH /api/tests/<id>
        Request: {"name": str} or {"description": str} or both (all fields optional)
        Response: {"id": int, "name": str, "description": str, "author": str} with status 200
        """
        update_data = UpdateTestRequest(name=name, description=description)
        data = {key: value for key, value in update_data.model_dump().items() if value is not None}
        response = self.patch(url=settings.get_test_url(str(test_id)), data=data)
        Logger.log(
            f"Partial update test {test_id} status: {response.status}",
            level=logging.DEBUG,
        )
        return response

    def set_test_status(self, test_id: int | str, status: str) -> APIResponse:
        """Set test execution status.

        API endpoint: POST /api/tests/<id>/status
        Request: {"status": str} where status is "PASS" or "FAIL"
        Response: {"runId": int} with status 200
        """
        status_data = TestStatusRequest(status=status)
        response = self.post(
            url=settings.get_test_status_url(str(test_id)),
            data=status_data.model_dump(),
        )
        Logger.log(
            f"Set status for test {test_id} -> {status}: {response.status}",
            level=logging.DEBUG,
        )
        return response

    def delete_test(self, test_id: int | str) -> APIResponse:
        """Delete test case by ID.

        API endpoint: DELETE /api/tests/<id>
        Response: {"status": "deleted"} with status 200
        """
        response = self.delete(url=settings.get_test_url(str(test_id)))
        Logger.log(
            f"Delete test {test_id} status: {response.status}",
            level=logging.DEBUG,
        )
        return response

    @staticmethod
    def parse_create_response(response: APIResponse) -> CreateTestResponse:
        """Parse create test response."""
        try:
            parsed = CreateTestResponse(**response.json())
            Logger.log("Parsed create test response", level=logging.DEBUG)
            return parsed
        except (ValueError, KeyError, TypeError) as e:
            Logger.log(f"Failed to parse create test response: {e}", level=logging.DEBUG)
            raise ValueError(f"Failed to parse create test response: {e}") from e

    @staticmethod
    def parse_test_case(response: APIResponse) -> TestCase:
        """Parse test case response (GET)."""
        try:
            parsed = TestCase(**response.json())
            Logger.log("Parsed test case response", level=logging.DEBUG)
            return parsed
        except (ValueError, KeyError, TypeError) as e:
            Logger.log(f"Failed to parse test case response: {e}", level=logging.DEBUG)
            raise ValueError(f"Failed to parse test case response: {e}") from e

    @staticmethod
    def parse_update_response(response: APIResponse) -> TestCase:
        """Parse update test response (PUT/PATCH).

        API returns: {"id": int, "name": str, "description": str, "author": str}
        """
        try:
            parsed = TestCase(**response.json())
            Logger.log("Parsed update test response", level=logging.DEBUG)
            return parsed
        except (ValueError, KeyError, TypeError) as e:
            Logger.log(f"Failed to parse update response: {e}", level=logging.DEBUG)
            raise ValueError(f"Failed to parse update response: {e}") from e

    @staticmethod
    def parse_set_status_response(response: APIResponse) -> SetTestStatusResponse:
        """Parse set test status response.

        API returns: {"runId": int}
        """
        try:
            parsed = SetTestStatusResponse(**response.json())
            Logger.log("Parsed set status response", level=logging.DEBUG)
            return parsed
        except (ValueError, KeyError, TypeError) as e:
            Logger.log(f"Failed to parse set status response: {e}", level=logging.DEBUG)
            raise ValueError(f"Failed to parse set status response: {e}") from e

    @staticmethod
    def parse_test_list(response: APIResponse) -> list[TestCase]:
        """Parse test case list response.

        API endpoint: GET /api/tests
        API returns: {'page': int, 'size': int, 'total': int, 'tests': [...]}
        Each test in 'tests' array has: {'id': int, 'name': str, 'description': str, 'author': str, 'status': str, 'executor': str or None}
        """
        try:
            data = response.json()
            if isinstance(data, dict) and "tests" in data:
                parsed_list = [TestCase(**item) for item in data["tests"]]
                Logger.log("Parsed test list response", level=logging.DEBUG)
                return parsed_list
            return []
        except (ValueError, KeyError, TypeError) as e:
            Logger.log(f"Failed to parse test list response: {e}", level=logging.DEBUG)
            raise ValueError(f"Failed to parse test list response: {e}") from e
