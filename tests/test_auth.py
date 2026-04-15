from __future__ import annotations

from typer.testing import CliRunner

from clikunja import config
from clikunja.cli import app

runner = CliRunner()


def test_login_writes_config_and_verifies_user(httpx_mock, tmp_path):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/user",
        json={"id": 1, "username": "alice"},
    )
    result = runner.invoke(
        app,
        ["login", "--url", "https://todo.example.com", "--token", "tk_abc"],
    )

    assert result.exit_code == 0, result.output + result.stderr
    assert "alice" in result.output
    saved = config.load()
    assert saved.url == "https://todo.example.com"
    assert saved.token == "tk_abc"


def test_login_fails_on_401(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/user",
        status_code=401,
        json={"message": "bad token"},
    )
    result = runner.invoke(
        app,
        ["login", "--url", "https://todo.example.com", "--token", "tk_bad"],
    )
    assert result.exit_code != 0
    assert (
        "bad token" in (result.output + result.stderr).lower()
        or "unauthor" in (result.output + result.stderr).lower()
    )
    saved = config.load()
    assert saved.token is None


def test_auth_status_masks_token(httpx_mock):
    config.save(config.Config(url="https://todo.example.com", token="tk_verysecret_12345"))
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/user",
        json={"id": 1, "username": "alice"},
    )
    result = runner.invoke(app, ["auth", "status"])

    assert result.exit_code == 0, result.output + result.stderr
    assert "tk_verysecret_12345" not in result.output
    assert "alice" in result.output
    assert "https://todo.example.com" in result.output


def test_auth_status_not_logged_in():
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code != 0
    combined = result.output + result.stderr
    assert "not" in combined.lower() or "login" in combined.lower()


def test_auth_logout_removes_token_keeps_url():
    config.save(config.Config(url="https://todo.example.com", token="tk_abc"))
    result = runner.invoke(app, ["auth", "logout"])
    assert result.exit_code == 0, result.output + result.stderr
    saved = config.load()
    assert saved.url == "https://todo.example.com"
    assert saved.token is None


def test_login_interactive_prompt(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/user",
        json={"id": 1, "username": "alice"},
    )
    result = runner.invoke(
        app,
        ["login", "--url", "https://todo.example.com"],
        input="tk_pasted\n",
    )
    assert result.exit_code == 0, result.output + result.stderr
    assert config.load().token == "tk_pasted"


def test_login_token_stdin(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/user",
        json={"id": 1, "username": "alice"},
    )
    result = runner.invoke(
        app,
        ["login", "--url", "https://todo.example.com", "--token-stdin"],
        input="tk_from_stdin\n",
    )
    assert result.exit_code == 0, result.output + result.stderr
    saved = config.load()
    assert saved.token == "tk_from_stdin"


def test_login_token_stdin_strips_trailing_whitespace(httpx_mock):
    httpx_mock.add_response(
        url="https://todo.example.com/api/v1/user",
        json={"id": 1, "username": "alice"},
    )
    result = runner.invoke(
        app,
        ["login", "--url", "https://todo.example.com", "--token-stdin"],
        input="  tk_padded  \n\n",
    )
    assert result.exit_code == 0, result.output + result.stderr
    assert config.load().token == "tk_padded"


def test_login_check_only_does_not_overwrite_config(httpx_mock):
    config.save(config.Config(url="https://old.example.com", token="old_tok"))
    httpx_mock.add_response(
        url="https://new.example.com/api/v1/user",
        json={"id": 2, "username": "bob"},
    )
    result = runner.invoke(
        app,
        [
            "login",
            "--url",
            "https://new.example.com",
            "--token",
            "new_tok",
            "--check",
        ],
    )
    assert result.exit_code == 0, result.output + result.stderr
    saved = config.load()
    assert saved.url == "https://old.example.com"
    assert saved.token == "old_tok"
