"""Test case data models."""

from enum import Enum

from pydantic import BaseModel, Field


class TestStatus(str, Enum):
    """Test execution status enumeration.

    Matches API values: PASS, FAIL, Norun
    """

    __test__ = False

    PASS = "PASS"
    FAIL = "FAIL"
    NORUN = "Norun"  # API uses "Norun" (capital N, lowercase orun)


class CreateTestRequest(BaseModel):
    """Request model for creating a new test case.

    Django model: name max_length=100, description max_length=1000
    """

    name: str = Field(..., min_length=1, max_length=100, description="Test case name")
    description: str = Field(..., min_length=1, max_length=1000, description="Test case description")


class CreateTestResponse(BaseModel):
    """Response model after creating a test case.

    API returns only test_id as integer: {"test_id": 537}
    """

    test_id: int = Field(..., description="Unique identifier of created test")


class UpdateTestRequest(BaseModel):
    """Request model for updating a test case (PUT/PATCH).

    Django model: name max_length=100, description max_length=1000
    """

    name: str | None = Field(None, min_length=1, max_length=100, description="Test case name")
    description: str | None = Field(None, min_length=1, max_length=1000, description="Test case description")


class TestStatusRequest(BaseModel):
    """Request model for setting test execution status.

    API accepts status as string: "PASS", "FAIL"
    """

    status: str | TestStatus = Field(..., description="Test execution status")


class SetTestStatusResponse(BaseModel):
    """Response model after setting test execution status.

    API returns: {"runId": int}
    """

    runId: int = Field(..., description="ID of the created test run")  # noqa: N815


class TestCase(BaseModel):
    """Complete test case model.

    Used for GET, PUT, PATCH responses.
    GET returns: {"id": int, "name": str, "description": str, "author": str, "status": str, "executor": str or None}
    PUT/PATCH returns: {"id": int, "name": str, "description": str, "author": str}
    Status can be: "PASS", "FAIL", "Norun"
    Executor can be: username string or None
    Django model: name max_length=100, description max_length=1000
    """

    id: int = Field(..., description="Unique test identifier")
    name: str = Field(..., max_length=100, description="Test case name")
    description: str = Field(..., max_length=1000, description="Test case description")
    author: str = Field(..., description="Test author (username)")
    executor: str | None = Field(None, description="Test executor (username, can be None, only in GET response)")
    status: str | TestStatus | None = Field(
        None, description="Test execution status: PASS, FAIL, or Norun (only in GET response)"
    )
