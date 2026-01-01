"""Statistics API tests."""

import pytest

from api.stats_client import StatsClient
from utils.assertions import assert_status_code


@pytest.mark.stats
@pytest.mark.smoke
@pytest.mark.positive
class TestStatisticsPositive:
    """Positive statistics test scenarios."""

    def test_statistics_response_structure(self, authenticated_stats_client: StatsClient):
        """Test getting statistics, validating structure, and parsing model."""
        response = authenticated_stats_client.get_statistics()

        assert_status_code(response, 200)
        try:
            stats = StatsClient.parse_statistics(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse statistics response: {e}")

        stats_dict = stats.model_dump()
        expected_keys = ["total", "passed", "failed", "norun"]
        missing_keys = [key for key in expected_keys if key not in stats_dict]
        assert not missing_keys, f"Response missing keys: {missing_keys}"

    def test_statistics_total_equals_sum_of_statuses(self, authenticated_stats_client: StatsClient):
        """Test that total equals the sum of passed, failed, and norun."""
        response = authenticated_stats_client.get_statistics()

        assert_status_code(response, 200)
        try:
            stats = StatsClient.parse_statistics(response)
        except ValueError as e:
            pytest.fail(f"Failed to parse statistics response: {e}")

        # Calculate sum of statuses
        sum_of_statuses = stats.passed + stats.failed + stats.norun

        # Total should equal sum of all statuses
        assert stats.total == sum_of_statuses, (
            f"Total ({stats.total}) should equal sum of statuses "
            f"(passed={stats.passed} + failed={stats.failed} + norun={stats.norun} = {sum_of_statuses})"
        )


@pytest.mark.stats
@pytest.mark.negative
class TestStatisticsNegative:
    """Negative statistics test scenarios."""

    def test_get_statistics_without_authentication(self, stats_client: StatsClient):
        """Test getting statistics without authentication."""
        response = stats_client.get_statistics()

        assert_status_code(response, 403)
