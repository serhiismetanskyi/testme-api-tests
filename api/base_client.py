"""Base API client with common functionality."""

import logging
import re
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from config import settings
from utils.logger import Logger


class BaseClient:
    """Base API client with common HTTP methods."""

    def __init__(self, request_context: APIRequestContext):
        """Initialize base client."""
        self.request_context = request_context
        self.base_url = settings.api_base_url
        self._csrf_token: str | None = None

    @property
    def csrf_token(self) -> str | None:
        """Get current CSRF token."""
        return self._csrf_token

    @csrf_token.setter
    def csrf_token(self, token: str) -> None:
        """Set CSRF token."""
        self._csrf_token = token

    def get_base_headers(self) -> dict[str, str]:
        """Get base HTTP headers."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Connection": "keep-alive",
        }

    def get_headers_with_token(self) -> dict[str, str]:
        """Get headers with CSRF token."""
        headers = self.get_base_headers()
        if self._csrf_token:
            headers["X-CSRFToken"] = self._csrf_token
        return headers

    def get_csrf_token(self) -> str | None:
        """Get CSRF token from /api/auth/token endpoint.

        The endpoint returns the token directly in the response body as plain text.
        """
        try:
            # GET to /api/auth/token returns token as plain text in response body
            response = self.get(url=settings.auth_token_url, skip_logging=True)
            if response.status == 200:
                token = response.text().strip()
                return token if token else None
            return None
        except Exception as e:
            Logger.log(f"Failed to fetch CSRF token: {e}", level=logging.DEBUG)
            return None

    def extract_csrf_token(self, response: APIResponse) -> str | None:
        """Extract CSRF token from response headers."""
        try:
            headers = response.headers
            set_cookie = headers.get("set-cookie", "")
            if not set_cookie:
                all_headers = dict(response.headers)
                set_cookie = all_headers.get("set-cookie", "")
            token_pattern = r"csrftoken=([a-zA-Z0-9]+)"
            match = re.search(token_pattern, set_cookie)
            if match:
                return match.group(1)
        except (AttributeError, KeyError, TypeError) as e:
            Logger.log(f"Failed to extract CSRF token: {e}", level=logging.DEBUG)
        return None

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        skip_logging: bool = False,
    ) -> APIResponse:
        """Perform GET request."""
        headers = headers or self.get_headers_with_token()
        if not skip_logging:
            Logger.add_request(url=url, method="GET", headers=headers, body=params)
        response = self.request_context.get(url, headers=headers, params=params)
        if not skip_logging:
            Logger.add_response(response)
        return response

    def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Perform POST request."""
        headers = headers or self.get_headers_with_token()
        Logger.add_request(url=url, method="POST", headers=headers, body=data)
        response = self.request_context.post(url, data=data, headers=headers)
        Logger.add_response(response)
        return response

    def put(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Perform PUT request."""
        headers = headers or self.get_headers_with_token()
        Logger.add_request(url=url, method="PUT", headers=headers, body=data)
        response = self.request_context.put(url, data=data, headers=headers)
        Logger.add_response(response)
        return response

    def patch(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Perform PATCH request."""
        headers = headers or self.get_headers_with_token()
        Logger.add_request(url=url, method="PATCH", headers=headers, body=data)
        response = self.request_context.patch(url, data=data, headers=headers)
        Logger.add_response(response)
        return response

    def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> APIResponse:
        """Perform DELETE request."""
        headers = headers or self.get_headers_with_token()
        Logger.add_request(url=url, method="DELETE", headers=headers)
        response = self.request_context.delete(url, headers=headers)
        Logger.add_response(response)
        return response
