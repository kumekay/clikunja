from __future__ import annotations

import stat
from pathlib import Path

import pytest
import yaml

from clikunja import config
from clikunja.errors import ConfigError


def test_load_from_xdg_file(monkeypatch, tmp_path):
    cfg_dir = tmp_path / "xdg" / "clikunja"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "config.yml").write_text(
        yaml.safe_dump({"url": "https://todo.example.com", "token": "tk_abc"})
    )

    loaded = config.load()

    assert loaded.url == "https://todo.example.com"
    assert loaded.token == "tk_abc"


def test_load_missing_returns_empty_config(tmp_path):
    loaded = config.load()
    assert loaded.url is None
    assert loaded.token is None


def test_env_overrides_file(monkeypatch, tmp_path):
    cfg_dir = tmp_path / "xdg" / "clikunja"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "config.yml").write_text(
        yaml.safe_dump({"url": "https://file.example.com", "token": "file_tok"})
    )
    monkeypatch.setenv("CLIKUNJA_URL", "https://env.example.com")
    monkeypatch.setenv("CLIKUNJA_TOKEN", "env_tok")

    loaded = config.load()

    assert loaded.url == "https://env.example.com"
    assert loaded.token == "env_tok"


def test_save_creates_dir_and_0600_perms(tmp_path):
    config.save(config.Config(url="https://x.example.com", token="tk_1"))

    path = config.path()
    assert path.exists()
    assert yaml.safe_load(path.read_text()) == {
        "url": "https://x.example.com",
        "token": "tk_1",
    }
    mode = stat.S_IMODE(path.stat().st_mode)
    assert mode == 0o600


def test_save_strips_none_values(tmp_path):
    config.save(config.Config(url="https://x.example.com", token=None))
    data = yaml.safe_load(config.path().read_text())
    assert "token" not in data
    assert data["url"] == "https://x.example.com"


def test_path_uses_xdg_config_home(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "custom"))
    assert config.path() == tmp_path / "custom" / "clikunja" / "config.yml"


def test_load_raises_on_malformed_yaml(tmp_path):
    cfg_dir = tmp_path / "xdg" / "clikunja"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "config.yml").write_text("{ not valid yaml: :")

    with pytest.raises(ConfigError):
        config.load()


def test_delete_token_preserves_url(tmp_path):
    config.save(config.Config(url="https://x.example.com", token="tk_1"))
    config.save(config.Config(url="https://x.example.com", token=None))

    loaded = config.load()
    assert loaded.url == "https://x.example.com"
    assert loaded.token is None


# silence unused param warnings in test files that rely on conftest fixtures
_ = Path
