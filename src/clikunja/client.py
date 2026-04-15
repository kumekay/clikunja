from __future__ import annotations

import json
import os
from typing import Any

import httpx

from clikunja.errors import APIError, AuthError

API_PREFIX = "/api/v1"


class Client:
    def __init__(self, url: str | None, token: str | None):
        if not url:
            raise AuthError("No Vikunja URL configured. Run `clikunja login` first.")
        if not token:
            raise AuthError("No API token configured. Run `clikunja login` first.")
        self.base_url = _normalize_base_url(url)
        self._token = token
        self.timeout = float(os.environ.get("CLIKUNJA_TIMEOUT", "30"))

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = self._url(path)
        try:
            resp = httpx.request(
                method.upper(),
                url,
                headers=self._headers(),
                timeout=self.timeout,
                **kwargs,
            )
        except httpx.HTTPError as e:
            raise APIError(0, str(e), f"HTTP request failed: {e}") from e

        if resp.status_code == 401:
            raise AuthError(f"Unauthorized: {_short_body(resp)}")
        if resp.status_code >= 400:
            raise APIError(resp.status_code, _short_body(resp))

        if not resp.content:
            return None
        try:
            return resp.json()
        except ValueError:
            return resp.text

    def get(self, path: str, **kw: Any) -> Any:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw: Any) -> Any:
        return self.request("POST", path, **kw)

    def put(self, path: str, **kw: Any) -> Any:
        return self.request("PUT", path, **kw)

    def delete(self, path: str, **kw: Any) -> Any:
        return self.request("DELETE", path, **kw)


def _normalize_base_url(url: str) -> str:
    url = url.rstrip("/")
    if not url.endswith(API_PREFIX):
        url = url + API_PREFIX
    return url


def _short_body(resp: httpx.Response) -> str:
    try:
        data = resp.json()
    except ValueError:
        return resp.text[:500]
    if isinstance(data, dict):
        for key in ("message", "error", "detail"):
            if key in data:
                return str(data[key])
    return json.dumps(data)[:500]
