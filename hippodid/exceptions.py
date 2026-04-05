"""HippoDid SDK exceptions."""

from __future__ import annotations


class HippoDidError(Exception):
    """Base exception for all HippoDid API errors."""

    def __init__(self, message: str, status_code: int = 0, response_body: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(HippoDidError):
    """Raised on 401 Unauthorized responses."""


class NotFoundError(HippoDidError):
    """Raised on 404 Not Found responses."""


class RateLimitError(HippoDidError):
    """Raised on 429 Too Many Requests responses."""

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        response_body: str = "",
        retry_after: float | None = None,
    ):
        super().__init__(message, status_code, response_body)
        self.retry_after = retry_after


class ValidationError(HippoDidError):
    """Raised on 400 Bad Request responses."""
