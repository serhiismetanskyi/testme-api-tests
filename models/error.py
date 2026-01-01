"""Error response models based on Django API error structure."""

from enum import Enum

from pydantic import BaseModel, Field


class ErrorMessage(str, Enum):
    """Error messages returned by the API."""

    BAD_INPUT_DATA = "bad input data"
    USERNAME_OR_PASSWORD_NOT_CORRECT = "username or password not correct"
    TEST_NOT_FOUND = "test not found"
    TEST_NAME_ALREADY_EXISTS = "test with such name already exists"


class ErrorResponse(BaseModel):
    """Error response model.

    API returns: {"error": str} with status 400, 401, or 404
    """

    error: str = Field(..., description="Error message")

    @classmethod
    def parse_error_response(cls, response_data: dict) -> "ErrorResponse":
        """Parse error response from JSON data."""
        return cls(**response_data)
