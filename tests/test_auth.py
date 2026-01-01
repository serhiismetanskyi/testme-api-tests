"""Authentication API tests."""

import pytest

from api.auth_client import AuthClient
from config import settings
from models.error import ErrorMessage, ErrorResponse
from utils.assertions import assert_status_code


@pytest.mark.auth
@pytest.mark.smoke
@pytest.mark.positive
class TestAuthenticationPositive:
    """Positive authentication test scenarios."""

    def test_get_csrf_token(self, auth_client: AuthClient):
        """Test that /api/auth/token returns a valid CSRF token."""
        token = auth_client.get_csrf_token()

        assert token is not None, "CSRF token endpoint should return a token"
        assert isinstance(token, str), "Token should be a string"
        assert len(token) > 0, "Token should not be empty"

    def test_login_with_valid_credentials(self, auth_client: AuthClient):
        """Test successful login with valid credentials and CSRF extraction."""
        username = settings.test_username
        password = settings.test_password

        response = auth_client.login(username, password)

        assert_status_code(response, 200)
        # API returns empty HttpResponse('', status=200) on success
        assert response.text().strip() == "", "Response body should be empty"
        assert auth_client.csrf_token is not None, "CSRF token should be extracted"
        assert isinstance(auth_client.csrf_token, str), "CSRF token should be a string"
        assert len(auth_client.csrf_token) > 0, "CSRF token should not be empty"

    def test_logout_after_login(self, authenticated_client: AuthClient):
        """Test successful logout after login."""
        response = authenticated_client.logout()

        # API returns empty HttpResponse('', status=200) on success
        assert_status_code(response, 200)
        assert response.text().strip() == "", "Response body should be empty"


@pytest.mark.auth
@pytest.mark.negative
class TestAuthenticationNegative:
    """Negative authentication test scenarios."""

    def test_login_with_invalid_username(self, auth_client: AuthClient):
        """Test login with invalid username."""
        username = "invalid_user_12345"
        password = "somepassword"

        response = auth_client.login(username, password)

        assert_status_code(response, 401)

    def test_login_with_invalid_password(self, auth_client: AuthClient):
        """Test login with invalid password."""
        username = settings.test_username
        password = "invalid_password_12345"

        response = auth_client.login(username, password)

        assert_status_code(response, 401)

    def test_login_with_empty_username(self, auth_client: AuthClient):
        """Test login with empty username."""
        username = ""
        password = "somepassword"

        response = auth_client.login(username, password)

        assert_status_code(response, 401)

    def test_login_with_empty_password(self, auth_client: AuthClient):
        """Test login with empty password."""
        username = settings.test_username
        password = ""

        response = auth_client.login(username, password)

        assert_status_code(response, 401)

    def test_login_with_empty_credentials(self, auth_client: AuthClient):
        """Test login with both empty username and password."""
        username = ""
        password = ""

        response = auth_client.login(username, password)

        assert_status_code(response, 401)

    def test_login_missing_username(self, auth_client: AuthClient):
        """Test login request missing username returns 400 with error message."""
        response = auth_client.post(
            url=settings.auth_login_url,
            data={"password": "somepassword"},
        )

        assert_status_code(response, 400)
        try:
            response_data = response.json()
            error_response = ErrorResponse.parse_error_response(response_data)
            assert error_response.error == ErrorMessage.BAD_INPUT_DATA.value
        except (ValueError, TypeError) as e:
            pytest.fail(f"Failed to parse error response: {e}")

    def test_login_missing_password(self, auth_client: AuthClient):
        """Test login request missing password returns 400 with error message."""
        response = auth_client.post(
            url=settings.auth_login_url,
            data={"username": "someuser"},
        )

        assert_status_code(response, 400)
        try:
            response_data = response.json()
            error_response = ErrorResponse.parse_error_response(response_data)
            assert error_response.error == ErrorMessage.BAD_INPUT_DATA.value
        except (ValueError, TypeError) as e:
            pytest.fail(f"Failed to parse error response: {e}")
