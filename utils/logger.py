"""Logging utilities with file output and HTTP request/response logging."""

import datetime
import json
import logging
import os
from pathlib import Path

from playwright.sync_api import APIResponse


class Logger:
    """Logger with file output and HTTP request/response logging."""

    dir_path = Path(__file__).parent.parent
    file_name = f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    file_path = dir_path / "logs" / file_name

    _logger = None

    @classmethod
    def _get_logger(cls):
        """Get or create pytest logger instance for HTML reports."""
        if cls._logger is None:
            cls._logger = logging.getLogger("testme_api_tests")
            cls._logger.setLevel(logging.INFO)
            cls._logger.propagate = True
        return cls._logger

    @classmethod
    def _ensure_logs_dir(cls):
        """Ensure logs directory exists."""
        cls.file_path.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def write_log_to_file(cls, data: str):
        """Write log data to file."""
        try:
            cls._ensure_logs_dir()
            with open(cls.file_path, "a", encoding="utf-8") as logger_file:
                logger_file.write(data)
        except Exception:
            pass

    @classmethod
    def log(cls, message: str, level=logging.INFO):
        """Log message to both pytest report and file."""
        cls._get_logger().log(level, message)
        cls.write_log_to_file(message + "\n")

    @classmethod
    def add_request(cls, url: str, method: str, body=None, headers=None):
        """Log HTTP request details."""
        test_name = os.environ.get("PYTEST_CURRENT_TEST", "Unknown test")
        time_str = str(datetime.datetime.now())

        data_to_add = "\n-----\n"
        data_to_add += f"Test: {test_name}\n"
        data_to_add += f"Time: {time_str}\n"
        data_to_add += f"Request method: {method}\n"
        data_to_add += f"Request URL: {url}\n"

        if headers:
            data_to_add += f"Request headers: {json.dumps(headers, indent=2)}\n"

        if body:
            if isinstance(body, dict):
                data_to_add += f"Request body: {json.dumps(body, indent=2)}\n"
            else:
                data_to_add += f"Request body: {body}\n"

        data_to_add += "\n"

        cls.write_log_to_file(data_to_add)

        pytest_message = "━━━ REQUEST ━━━\n"
        pytest_message += f"Method: {method}\n"
        pytest_message += f"URL: {url}\n"

        if headers:
            important_headers = {
                k: v for k, v in headers.items() if k.lower() in ["content-type", "x-csrftoken", "authorization"]
            }
            if important_headers:
                pytest_message += f"Headers: {json.dumps(important_headers, indent=2)}\n"

        if body:
            body_str = json.dumps(body, indent=2, ensure_ascii=False) if isinstance(body, dict) else str(body)
            if len(body_str) > 1000:
                body_str = body_str[:1000] + "\n... (truncated)"
            pytest_message += f"Body:\n{body_str}"

        cls._get_logger().info(pytest_message)

    @classmethod
    def add_response(cls, response: APIResponse):
        """Log HTTP response details."""
        try:
            headers_dict = dict(response.headers) if response.headers else {}
            status = response.status
            status_text = response.status_text if hasattr(response, "status_text") else ""

            try:
                response_text = response.text()
            except Exception:
                response_text = "<unable to get response text>"

            data_to_add = f"Response code: {status}\n"
            data_to_add += f"Response text: {response_text}\n"
            data_to_add += f"Response headers: {headers_dict}\n"
            data_to_add += "\n-----\n"

            cls.write_log_to_file(data_to_add)

            pytest_message = "━━━ RESPONSE ━━━\n"
            pytest_message += f"Status: {status} {status_text}\n"

            important_headers = {
                k: v
                for k, v in headers_dict.items()
                if k.lower() in ["content-type", "content-length", "location", "set-cookie"]
            }
            if important_headers:
                pytest_message += f"Headers: {json.dumps(important_headers, indent=2)}\n"

            try:
                response_json = response.json()
                body_str = json.dumps(response_json, indent=2, ensure_ascii=False)
            except (ValueError, TypeError, AttributeError):
                # Not JSON - could be empty response, plain text, or invalid JSON
                # Empty responses: login/logout endpoints return empty HttpResponse('')
                # Plain text: /api/auth/token returns plain text CSRF token
                body_str = response_text if response_text else "<empty response>"

            if len(body_str) > 1000:
                body_str = body_str[:1000] + "\n... (truncated)"

            pytest_message += f"Body:\n{body_str}"

            cls._get_logger().info(pytest_message)
        except Exception:
            pass


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """Get or create a logger with file and console output."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        dir_path = Path(__file__).parent.parent
        logs_dir = dir_path / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        file_path = logs_dir / file_name

        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.propagate = True

    if level:
        logger.setLevel(getattr(logging, level.upper()))
    else:
        logger.setLevel(logging.INFO)

    return logger
