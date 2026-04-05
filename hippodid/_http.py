"""Low-level HTTP transport with retry logic."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from hippodid.exceptions import (
    AuthenticationError,
    HippoDidError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

_DEFAULT_TIMEOUT = 30.0
_MAX_RETRIES = 3
_RETRY_BACKOFF = 1.0  # seconds, doubles each retry
_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def _raise_for_status(response: httpx.Response) -> None:
    if response.status_code < 400:
        return

    body = response.text
    msg = f"HTTP {response.status_code}"

    # Try to extract error message from JSON body
    try:
        data = response.json()
        if isinstance(data, dict):
            msg = data.get("message", data.get("error", msg))
    except Exception:
        pass

    if response.status_code == 401:
        raise AuthenticationError(msg, response.status_code, body)
    if response.status_code == 404:
        raise NotFoundError(msg, response.status_code, body)
    if response.status_code == 429:
        retry_after = None
        ra = response.headers.get("Retry-After")
        if ra:
            try:
                retry_after = float(ra)
            except ValueError:
                pass
        raise RateLimitError(msg, response.status_code, body, retry_after)
    if response.status_code in (400, 422):
        raise ValidationError(msg, response.status_code, body)

    raise HippoDidError(msg, response.status_code, body)


class SyncTransport:
    """Synchronous HTTP transport with retry + backoff."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        tenant_id: Optional[str] = None,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _MAX_RETRIES,
    ):
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "hippodid-python/0.1.0",
        }
        if tenant_id:
            headers["X-Tenant-Id"] = tenant_id

        self._client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )
        self._max_retries = max_retries

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
        content: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        attempt = 0
        backoff = _RETRY_BACKOFF

        while True:
            try:
                response = self._client.request(
                    method,
                    path,
                    json=json,
                    params=_clean_params(params),
                    content=content,
                    headers=headers,
                )
                if response.status_code in _RETRYABLE_STATUS and attempt < self._max_retries:
                    wait = backoff
                    if response.status_code == 429:
                        ra = response.headers.get("Retry-After")
                        if ra:
                            try:
                                wait = float(ra)
                            except ValueError:
                                pass
                    time.sleep(wait)
                    attempt += 1
                    backoff *= 2
                    continue

                _raise_for_status(response)
                return response

            except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                if attempt >= self._max_retries:
                    raise HippoDidError(f"Connection failed after {self._max_retries} retries: {exc}")
                time.sleep(backoff)
                attempt += 1
                backoff *= 2

    def request_multipart(
        self,
        path: str,
        *,
        files: Dict[str, Any],
        data: Dict[str, str],
    ) -> httpx.Response:
        """Multipart upload with the same retry/backoff as request()."""
        attempt = 0
        backoff = _RETRY_BACKOFF

        while True:
            try:
                response = self._client.post(path, files=files, data=data)
                if response.status_code in _RETRYABLE_STATUS and attempt < self._max_retries:
                    wait = backoff
                    if response.status_code == 429:
                        ra = response.headers.get("Retry-After")
                        if ra:
                            try:
                                wait = float(ra)
                            except ValueError:
                                pass
                    time.sleep(wait)
                    attempt += 1
                    backoff *= 2
                    continue

                _raise_for_status(response)
                return response

            except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                if attempt >= self._max_retries:
                    raise HippoDidError(f"Connection failed after {self._max_retries} retries: {exc}")
                time.sleep(backoff)
                attempt += 1
                backoff *= 2

    def close(self) -> None:
        self._client.close()


class AsyncTransport:
    """Asynchronous HTTP transport with retry + backoff."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        tenant_id: Optional[str] = None,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _MAX_RETRIES,
    ):
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "hippodid-python/0.1.0",
        }
        if tenant_id:
            headers["X-Tenant-Id"] = tenant_id

        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )
        self._max_retries = max_retries

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
        content: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        import asyncio

        attempt = 0
        backoff = _RETRY_BACKOFF

        while True:
            try:
                response = await self._client.request(
                    method,
                    path,
                    json=json,
                    params=_clean_params(params),
                    content=content,
                    headers=headers,
                )
                if response.status_code in _RETRYABLE_STATUS and attempt < self._max_retries:
                    wait = backoff
                    if response.status_code == 429:
                        ra = response.headers.get("Retry-After")
                        if ra:
                            try:
                                wait = float(ra)
                            except ValueError:
                                pass
                    await asyncio.sleep(wait)
                    attempt += 1
                    backoff *= 2
                    continue

                _raise_for_status(response)
                return response

            except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                if attempt >= self._max_retries:
                    raise HippoDidError(
                        f"Connection failed after {self._max_retries} retries: {exc}"
                    )
                await asyncio.sleep(backoff)
                attempt += 1
                backoff *= 2

    async def request_multipart(
        self,
        path: str,
        *,
        files: Dict[str, Any],
        data: Dict[str, str],
    ) -> httpx.Response:
        """Multipart upload with the same retry/backoff as request()."""
        import asyncio

        attempt = 0
        backoff = _RETRY_BACKOFF

        while True:
            try:
                response = await self._client.post(path, files=files, data=data)
                if response.status_code in _RETRYABLE_STATUS and attempt < self._max_retries:
                    wait = backoff
                    if response.status_code == 429:
                        ra = response.headers.get("Retry-After")
                        if ra:
                            try:
                                wait = float(ra)
                            except ValueError:
                                pass
                    await asyncio.sleep(wait)
                    attempt += 1
                    backoff *= 2
                    continue

                _raise_for_status(response)
                return response

            except (httpx.ConnectError, httpx.ReadTimeout) as exc:
                if attempt >= self._max_retries:
                    raise HippoDidError(
                        f"Connection failed after {self._max_retries} retries: {exc}"
                    )
                await asyncio.sleep(backoff)
                attempt += 1
                backoff *= 2

    async def close(self) -> None:
        await self._client.aclose()


def _clean_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Remove None values from query params."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}
