"""Statistics API client."""

import logging

from playwright.sync_api import APIResponse

from api.base_client import BaseClient
from config import settings
from models.stats import Statistics
from utils.logger import Logger


class StatsClient(BaseClient):
    """Client for statistics endpoints."""

    def get_statistics(self) -> APIResponse:
        """Get test statistics."""
        response = self.get(url=settings.stats_url)
        Logger.log(f"Stats response status: {response.status}", level=logging.DEBUG)
        return response

    @staticmethod
    def parse_statistics(response: APIResponse) -> Statistics:
        """Parse statistics response."""
        try:
            stats = Statistics(**response.json())
            Logger.log("Parsed statistics response successfully", level=logging.DEBUG)
            return stats
        except (ValueError, KeyError, TypeError) as e:
            Logger.log(f"Failed to parse statistics response: {e}", level=logging.DEBUG)
            raise ValueError(f"Failed to parse statistics response: {e}") from e
