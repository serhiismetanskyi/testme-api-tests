"""Statistics data models."""

from pydantic import BaseModel, Field


class Statistics(BaseModel):
    """Test statistics model.

    API returns: {"total": int, "passed": int, "failed": int, "norun": int}
    """

    total: int = Field(..., description="Total number of tests")
    passed: int = Field(..., description="Number of passed tests")
    failed: int = Field(..., description="Number of failed tests")
    norun: int = Field(..., description="Number of tests that haven't been run")
