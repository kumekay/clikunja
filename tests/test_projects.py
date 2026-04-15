from __future__ import annotations

import json

from typer.testing import CliRunner

from clikunja import config
from clikunja.cli import app

runner = CliRunner()


def _logged_in():
    config.save(config.Config(url="https://todo.example.com", token="tk_1"))


def test_projects_list_renders_table(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects",
        json=[
            {"id": 1, "title": "Inbox", "parent_project_id": 0},
            {"id": 2, "title": "Work", "parent_project_id": 1},
        ],
    )
    result = runner.invoke(app, ["projects", "list"])
    assert result.exit_code == 0, result.output
    assert "Inbox" in result.output
    assert "Work" in result.output
    assert "1" in result.output


def test_projects_list_json(httpx_mock):
    _logged_in()
    payload = [{"id": 1, "title": "Inbox"}]
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects",
        json=payload,
    )
    result = runner.invoke(app, ["projects", "list", "--json"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output) == payload


def test_projects_create(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects",
        json={"id": 7, "title": "New"},
    )
    result = runner.invoke(app, ["projects", "create", "--title", "New"])
    assert result.exit_code == 0, result.output
    req = httpx_mock.get_requests()[0]
    assert req.method == "PUT"
    assert json.loads(req.content) == {"title": "New"}
    assert "7" in result.output


def test_projects_view(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects/3",
        json={"id": 3, "title": "Work", "description": "stuff"},
    )
    result = runner.invoke(app, ["projects", "view", "3"])
    assert result.exit_code == 0, result.output
    assert "Work" in result.output


def test_projects_delete(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects/3",
        json={},
    )
    result = runner.invoke(app, ["projects", "delete", "3"])
    assert result.exit_code == 0, result.output
    assert httpx_mock.get_requests()[0].method == "DELETE"
