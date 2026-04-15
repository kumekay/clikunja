from __future__ import annotations

import json

from typer.testing import CliRunner

from clikunja import config
from clikunja.cli import app

runner = CliRunner()


def _logged_in():
    config.save(config.Config(url="https://todo.example.com", token="tk_1"))


def test_tasks_list_all(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks",
        json=[{"id": 42, "title": "Buy milk", "done": False, "project_id": 1}],
    )
    result = runner.invoke(app, ["tasks", "list"])
    assert result.exit_code == 0, result.output
    assert "Buy milk" in result.output


def test_tasks_list_with_project_filter(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects/3/tasks",
        json=[{"id": 9, "title": "Under 3", "done": False}],
    )
    result = runner.invoke(app, ["tasks", "list", "--project", "3"])
    assert result.exit_code == 0, result.output
    assert "Under 3" in result.output


def test_tasks_view(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks/42",
        json={"id": 42, "title": "Buy milk", "done": False},
    )
    result = runner.invoke(app, ["tasks", "view", "42"])
    assert result.exit_code == 0, result.output
    assert "Buy milk" in result.output


def test_tasks_create_under_project(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects/3/tasks",
        json={"id": 50, "title": "Write tests"},
    )
    result = runner.invoke(
        app,
        ["tasks", "create", "--project", "3", "--title", "Write tests"],
    )
    assert result.exit_code == 0, result.output
    req = httpx_mock.get_requests()[0]
    assert req.method == "PUT"
    body = json.loads(req.content)
    assert body["title"] == "Write tests"
    assert "50" in result.output


def test_tasks_done_toggles(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks/42",
        json={"id": 42, "done": True},
    )
    result = runner.invoke(app, ["tasks", "done", "42"])
    assert result.exit_code == 0, result.output
    req = httpx_mock.get_requests()[0]
    assert req.method == "POST"
    assert json.loads(req.content) == {"done": True}


def test_tasks_undone(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks/42",
        json={"id": 42, "done": False},
    )
    result = runner.invoke(app, ["tasks", "undone", "42"])
    assert result.exit_code == 0, result.output
    assert json.loads(httpx_mock.get_requests()[0].content) == {"done": False}


def test_tasks_delete(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks/42",
        json={},
    )
    result = runner.invoke(app, ["tasks", "delete", "42"])
    assert result.exit_code == 0, result.output
    assert httpx_mock.get_requests()[0].method == "DELETE"


def test_tasks_create_with_description_and_priority(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects/1/tasks",
        json={"id": 100, "title": "X"},
    )
    result = runner.invoke(
        app,
        [
            "tasks",
            "create",
            "--project",
            "1",
            "--title",
            "X",
            "--description",
            "body",
            "--priority",
            "3",
        ],
    )
    assert result.exit_code == 0, result.output
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert body == {"title": "X", "description": "body", "priority": 3}
