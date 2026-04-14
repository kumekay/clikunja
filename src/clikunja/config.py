from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import platformdirs
import yaml

from clikunja.errors import ConfigError

APP_NAME = "clikunja"
CONFIG_FILENAME = "config.yml"


@dataclass(frozen=True)
class Config:
    url: str | None = None
    token: str | None = None


def path() -> Path:
    return Path(platformdirs.user_config_dir(APP_NAME)) / CONFIG_FILENAME


def _load_file() -> dict:
    p = path()
    if not p.exists():
        return {}
    try:
        data = yaml.safe_load(p.read_text()) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"Malformed config at {p}: {e}") from e
    if not isinstance(data, dict):
        raise ConfigError(f"Expected mapping in {p}, got {type(data).__name__}")
    return data


def load() -> Config:
    data = _load_file()
    url = os.environ.get("CLIKUNJA_URL") or data.get("url")
    token = os.environ.get("CLIKUNJA_TOKEN") or data.get("token")
    return Config(url=url, token=token)


def save(cfg: Config) -> Path:
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, str] = {}
    if cfg.url is not None:
        data["url"] = cfg.url
    if cfg.token is not None:
        data["token"] = cfg.token
    p.write_text(yaml.safe_dump(data, sort_keys=True))
    p.chmod(0o600)
    return p
