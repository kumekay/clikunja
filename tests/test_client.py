from __future__ import annotations

import pytest

from clikunja.client import Client
from clikunja.errors import APIError, AuthError


def test_base_url_appends_api_v1_when_missing():
    c = Client("https://todo.example.com", "tk_1")
    assert c.base_url == "https://todo.example.com/api/v1"


def test_base_url_strips_trailing_slash():
    c = Client("https://todo.example.com/", "tk_1")
    assert c.base_url == "https://todo.example.com/api/v1"


def test_base_url_keeps_api_v1_if_given():
    c = Client("https://todo.example.com/api/v1", "tk_1")
    assert c.base_url == "https://todo.example.com/api/v1"


def test_bearer_header_added(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/user",
        json={"id": 1, "username": "a"},
    )
    c = Client("https://todo.example.com", "tk_secret")
    c.get("/user")

    req = httpx_mock.get_requests()[0]
    assert req.headers["Authorization"] == "Bearer tk_secret"


def test_get_parses_json(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects",
        json=[{"id": 1, "title": "Inbox"}],
    )
    c = Client("https://todo.example.com", "tk_1")
    data = c.get("/projects")
    assert data == [{"id": 1, "title": "Inbox"}]


def test_post_sends_json_body(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects",
        json={"id": 7, "title": "New"},
    )
    c = Client("https://todo.example.com", "tk_1")
    c.post("/projects", json={"title": "New"})

    req = httpx_mock.get_requests()[0]
    assert req.method == "POST"
    import json as _json
    assert _json.loads(req.content) == {"title": "New"}


def test_path_without_leading_slash_still_joins(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/labels",
        json=[],
    )
    c = Client("https://todo.example.com", "tk_1")
    c.get("labels")


def test_raises_api_error_on_4xx(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects/999",
        status_code=404,
        json={"message": "not found"},
    )
    c = Client("https://todo.example.com", "tk_1")
    with pytest.raises(APIError) as exc:
        c.get("/projects/999")
    assert exc.value.status == 404
    assert "not found" in exc.value.body


def test_raises_auth_error_on_401(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/user",
        status_code=401,
        json={"message": "bad token"},
    )
    c = Client("https://todo.example.com", "tk_1")
    with pytest.raises(AuthError):
        c.get("/user")


def test_timeout_env_override(monkeypatch):
    monkeypatch.setenv("CLIKUNJA_TIMEOUT", "7")
    c = Client("https://todo.example.com", "tk_1")
    assert c.timeout == 7.0


def test_request_generic_method(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks/42",
        json={"id": 42, "done": True},
    )
    c = Client("https://todo.example.com", "tk_1")
    data = c.request("POST", "/tasks/42", json={"done": True})
    assert data == {"id": 42, "done": True}


def test_missing_url_or_token_raises():
    with pytest.raises(AuthError):
        Client(None, "tk_1")
    with pytest.raises(AuthError):
        Client("https://x.example.com", None)
