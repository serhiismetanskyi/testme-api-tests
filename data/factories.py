"""Test data factories using Faker."""

import time

from faker import Faker

fake = Faker()


class TestDataFactory:
    """Factory for generating test data."""

    @staticmethod
    def generate_test_name(prefix: str = "API Test") -> str:
        """
        Generate unique test name with timestamp.

        Args:
            prefix: Prefix for test name

        Returns:
            Generated test name
        """
        timestamp = int(time.time() * 1000)
        return f"{prefix} {timestamp}"

    @staticmethod
    def generate_test_description(action: str = "Testing API") -> str:
        """
        Generate test description.

        Args:
            action: Action being tested

        Returns:
            Generated description
        """
        return f"{action} - {fake.sentence()}"

    @staticmethod
    def generate_random_test_data() -> dict[str, str]:
        """
        Generate random test case data.

        Returns:
            Dictionary with name and description
        """
        return {
            "name": TestDataFactory.generate_test_name(),
            "description": TestDataFactory.generate_test_description(),
        }
