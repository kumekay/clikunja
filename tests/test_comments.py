from __future__ import annotations

import json

from typer.testing import CliRunner

from clikunja import config
from clikunja.cli import app

runner = CliRunner()


def _logged_in():
    config.save(config.Config(url="https://todo.example.com", token="tk_1"))


def test_comments_list(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks/42/comments",
        json=[{"id": 1, "comment": "hello", "author": {"username": "alice"}}],
    )
    result = runner.invoke(app, ["comments", "list", "--task", "42"])
    assert result.exit_code == 0, result.output
    assert "hello" in result.output


def test_comments_add(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks/42/comments",
        json={"id": 9, "comment": "great"},
    )
    result = runner.invoke(app, ["comments", "add", "--task", "42", "great"])
    assert result.exit_code == 0, result.output
    req = httpx_mock.get_requests()[0]
    assert req.method == "PUT"
    assert json.loads(req.content) == {"comment": "great"}


def test_comments_delete(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks/42/comments/9",
        json={},
    )
    result = runner.invoke(app, ["comments", "delete", "--task", "42", "9"])
    assert result.exit_code == 0, result.output
    assert httpx_mock.get_requests()[0].method == "DELETE"
