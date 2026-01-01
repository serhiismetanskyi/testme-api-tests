"""Application settings and configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    api_base_url: str = Field(description="Base URL for API")
    api_timeout: int = Field(description="API timeout in milliseconds")

    # Test User Credentials
    test_username: str = Field(description="Test user username")
    test_password: str = Field(description="Test user password")

    # Test Configuration
    headless: bool = Field(description="Run tests in headless mode")
    parallel_workers: int = Field(description="Number of parallel workers")
    log_level: str = Field(description="Logging level")

    @property
    def auth_token_url(self) -> str:
        """Get full CSRF token URL."""
        return f"{self.api_base_url}/api/auth/token"

    @property
    def auth_login_url(self) -> str:
        """Get full authentication login URL."""
        return f"{self.api_base_url}/api/auth/login"

    @property
    def auth_logout_url(self) -> str:
        """Get full authentication logout URL."""
        return f"{self.api_base_url}/api/auth/logout"

    @property
    def tests_url(self) -> str:
        """Get full tests list URL."""
        return f"{self.api_base_url}/api/tests"

    @property
    def tests_new_url(self) -> str:
        """Get full create test URL."""
        return f"{self.api_base_url}/api/tests/new"

    @property
    def stats_url(self) -> str:
        """Get full statistics URL."""
        return f"{self.api_base_url}/api/getstat"

    def get_test_url(self, test_id: str) -> str:
        """Get full test URL by ID."""
        return f"{self.api_base_url}/api/tests/{test_id}"

    def get_test_status_url(self, test_id: str) -> str:
        """Get full test status URL by ID."""
        return f"{self.api_base_url}/api/tests/{test_id}/status"


settings = Settings()
