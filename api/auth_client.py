"""Authentication API client."""

import logging

from playwright.sync_api import APIResponse

from api.base_client import BaseClient
from config import settings
from utils.logger import Logger


class AuthClient(BaseClient):
    """Client for authentication endpoints."""

    def login(self, username: str, password: str) -> APIResponse:
        """Login user and extract CSRF token.

        Steps:
        1. Get CSRF token if not already set
        2. Send POST request to /api/auth/login with username and password
        3. Extract and save CSRF token from response for future requests
        """
        # Get CSRF token if not already available
        if not self.csrf_token:
            self.csrf_token = self.get_csrf_token()

        # Send login request
        response = self.post(
            url=settings.auth_login_url,
            data={"username": username, "password": password},
        )
        Logger.log(f"Auth login response status: {response.status}", level=logging.DEBUG)

        # Extract and save CSRF token from response (may be in cookies)
        token = self.extract_csrf_token(response)
        if token:
            self.csrf_token = token

        return response

    def logout(self) -> APIResponse:
        """Logout current user."""
        response = self.get(url=settings.auth_logout_url)
        Logger.log(f"Auth logout response status: {response.status}", level=logging.DEBUG)
        return response
