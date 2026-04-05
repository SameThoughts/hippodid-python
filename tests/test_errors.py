"""Tests for error handling and retries."""

import httpx
import pytest

from hippodid.exceptions import (
    AuthenticationError,
    HippoDidError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


CID = "c1000000-0000-0000-0000-000000000001"


def test_auth_error(client, mock_api):
    mock_api.get(f"/v1/characters/{CID}").mock(
        return_value=httpx.Response(401, json={"message": "Invalid API key"})
    )
    with pytest.raises(AuthenticationError, match="Invalid API key"):
        client.get_character(CID)


def test_not_found_error(client, mock_api):
    mock_api.get(f"/v1/characters/{CID}").mock(
        return_value=httpx.Response(404, json={"message": "Character not found"})
    )
    with pytest.raises(NotFoundError, match="Character not found"):
        client.get_character(CID)


def test_validation_error(client, mock_api):
    mock_api.post("/v1/characters").mock(
        return_value=httpx.Response(400, json={"message": "Name is required"})
    )
    with pytest.raises(ValidationError, match="Name is required"):
        client.create_character(name="")


def test_rate_limit_error(client, mock_api):
    mock_api.get(f"/v1/characters/{CID}").mock(
        return_value=httpx.Response(
            429,
            json={"message": "Rate limit exceeded"},
            headers={"Retry-After": "2.5"},
        )
    )
    with pytest.raises(RateLimitError) as exc_info:
        client.get_character(CID)
    assert exc_info.value.retry_after == 2.5


def test_server_error(client, mock_api):
    mock_api.get(f"/v1/characters/{CID}").mock(
        return_value=httpx.Response(500, json={"message": "Internal error"})
    )
    with pytest.raises(HippoDidError):
        client.get_character(CID)


def test_error_response_body_preserved(client, mock_api):
    mock_api.get(f"/v1/characters/{CID}").mock(
        return_value=httpx.Response(404, json={"message": "Not found", "code": "NOT_FOUND"})
    )
    with pytest.raises(NotFoundError) as exc_info:
        client.get_character(CID)
    assert exc_info.value.status_code == 404
    assert "NOT_FOUND" in exc_info.value.response_body


def test_422_raises_validation_error(client, mock_api):
    """Backend returns 422 for bean-validation and domain validation errors."""
    mock_api.post("/v1/characters").mock(
        return_value=httpx.Response(422, json={"message": "name: must not be blank"})
    )
    with pytest.raises(ValidationError, match="must not be blank") as exc_info:
        client.create_character(name="")
    assert exc_info.value.status_code == 422
