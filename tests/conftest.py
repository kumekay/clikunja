from __future__ import annotations

import socket

import pytest


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch, tmp_path):
    """Per-test config isolation: fresh XDG dir, no CLIKUNJA_* bleed-in."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    for var in ("CLIKUNJA_URL", "CLIKUNJA_TOKEN", "CLIKUNJA_TIMEOUT"):
        monkeypatch.delenv(var, raising=False)
    yield


@pytest.fixture(autouse=True)
def _no_real_network(monkeypatch):
    """Fail loudly on any real socket connect. pytest-httpx intercepts httpx before sockets,
    so this only fires if a test bypasses mocking."""
    orig_connect = socket.socket.connect

    def guard(self, address):  # noqa: ANN001
        host = address[0] if isinstance(address, tuple) else str(address)
        if host in ("127.0.0.1", "::1", "localhost"):
            return orig_connect(self, address)
        raise RuntimeError(f"Real network access forbidden in tests: {address!r}")

    monkeypatch.setattr(socket.socket, "connect", guard)
    yield
