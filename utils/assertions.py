"""Custom assertions for API testing."""

from typing import Any

from playwright.sync_api import APIResponse


def assert_response(
    response: APIResponse,
    expected_status: int,
    expected_keys: list[str] | None = None,
    error_message: str | None = None,
) -> dict[str, Any]:
    """Assert API response status and optionally check for expected keys in JSON."""
    actual_status = response.status
    message = error_message or f"Expected status {expected_status}, got {actual_status}"

    try:
        response_text = response.text()
    except Exception:
        response_text = "<unable to get response text>"

    assert actual_status == expected_status, f"{message}. Response: {response_text}"

    try:
        response_text_content = response_text.strip() if response_text else ""
        if not response_text_content:
            # Empty response is OK for status 200 (e.g., login/logout endpoints)
            # and for status 404 (e.g., GET/PUT/PATCH/DELETE when resource not found)
            if expected_status in [200, 404]:
                return {}
            raise AssertionError(f"Empty response body. Response: {response_text}")

        # Parse JSON from already retrieved text to avoid reading body twice
        import json as json_module

        response_json = json_module.loads(response_text_content)
    except (ValueError, TypeError, AttributeError) as e:
        # Not JSON - could be plain text (e.g., /api/auth/token) or invalid JSON
        raise AssertionError(f"Failed to parse response as JSON: {e}. Response: {response_text[:200]}") from e

    if expected_keys:
        for key in expected_keys:
            assert key in response_json, f"Expected key '{key}' not found in response: {response_json}"

    return response_json


def assert_status_code(response: APIResponse, expected_status: int) -> None:
    """Assert only the status code of API response."""
    actual_status = response.status
    try:
        response_text = response.text()
    except Exception:
        response_text = "<unable to get response text>"

    assert actual_status == expected_status, (
        f"Expected status {expected_status}, got {actual_status}. Response: {response_text}"
    )


def assert_json_contains(response_json: dict[str, Any], expected_data: dict[str, Any]) -> None:
    """Assert that response JSON contains all expected key-value pairs."""
    for key, expected_value in expected_data.items():
        assert key in response_json, f"Expected key '{key}' not found in response"
        actual_value = response_json[key]
        assert actual_value == expected_value, f"For key '{key}': expected '{expected_value}', got '{actual_value}'"
