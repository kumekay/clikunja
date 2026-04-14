from __future__ import annotations

import json

from typer.testing import CliRunner

from clikunja import config
from clikunja.cli import app

runner = CliRunner()


def _logged_in():
    config.save(config.Config(url="https://todo.example.com", token="tk_1"))


def test_get_passthrough_prints_json(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects",
        json=[{"id": 1, "title": "Inbox"}],
    )
    result = runner.invoke(app, ["api", "GET", "projects"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == [{"id": 1, "title": "Inbox"}]


def test_api_leading_slash_ok(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects/3",
        json={"id": 3, "title": "Work"},
    )
    result = runner.invoke(app, ["api", "GET", "/projects/3"])
    assert result.exit_code == 0, result.output


def test_api_method_defaults_to_get(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects",
        json=[],
    )
    result = runner.invoke(app, ["api", "projects"])
    assert result.exit_code == 0, result.output
    assert httpx_mock.get_requests()[0].method == "GET"


def test_f_string_fields_become_json_body(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects",
        json={"id": 1, "title": "New"},
    )
    result = runner.invoke(
        app,
        ["api", "PUT", "projects", "-f", "title=New", "-f", "description=hi"],
    )
    assert result.exit_code == 0, result.output
    req = httpx_mock.get_requests()[0]
    assert req.method == "PUT"
    assert json.loads(req.content) == {"title": "New", "description": "hi"}


def test_F_file_fields_read_from_disk(httpx_mock, tmp_path):
    _logged_in()
    body_file = tmp_path / "body.md"
    body_file.write_text("# hello\n\nmulti-line\n")
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/tasks/42/comments",
        json={"id": 9, "comment": "# hello\n\nmulti-line\n"},
    )
    result = runner.invoke(
        app,
        [
            "api",
            "PUT",
            "tasks/42/comments",
            "-F",
            f"comment=@{body_file}",
        ],
    )
    assert result.exit_code == 0, result.output
    req = httpx_mock.get_requests()[0]
    assert json.loads(req.content) == {"comment": "# hello\n\nmulti-line\n"}


def test_api_raw_passes_body_unparsed(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/projects/3",
        content=b"literal-bytes-not-json",
        headers={"content-type": "text/plain"},
    )
    result = runner.invoke(app, ["api", "GET", "/projects/3", "--raw"])
    assert result.exit_code == 0, result.output
    assert "literal-bytes-not-json" in result.output


def test_api_surfaces_api_error(httpx_mock):
    _logged_in()
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/nope",
        status_code=404,
        json={"message": "not found"},
    )
    result = runner.invoke(app, ["api", "GET", "nope"])
    assert result.exit_code != 0


def test_api_requires_login():
    result = runner.invoke(app, ["api", "GET", "projects"])
    assert result.exit_code != 0
