from __future__ import annotations

import json

from typer.testing import CliRunner

from clikunja import config
from clikunja.cli import app

runner = CliRunner()


def _logged_in():
    config.save(config.Config(url="https://todo.example.com", token="tk_1"))


def test_labels_list(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/labels",
        json=[{"id": 1, "title": "bug", "hex_color": "ff0000"}],
    )
    result = runner.invoke(app, ["labels", "list"])
    assert result.exit_code == 0, result.output
    assert "bug" in result.output


def test_labels_create(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/labels",
        json={"id": 2, "title": "feature"},
    )
    result = runner.invoke(app, ["labels", "create", "--title", "feature"])
    assert result.exit_code == 0, result.output
    req = httpx_mock.get_requests()[0]
    assert req.method == "PUT"
    assert json.loads(req.content)["title"] == "feature"


def test_labels_delete(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/labels/5",
        json={},
    )
    result = runner.invoke(app, ["labels", "delete", "5"])
    assert result.exit_code == 0, result.output
    assert httpx_mock.get_requests()[0].method == "DELETE"
