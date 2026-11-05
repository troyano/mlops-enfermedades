import pytest

from diagnostico_ui.config import DEFAULT_BACKEND_URL, get_backend_url


def test_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BACKEND_URL", raising=False)
    assert get_backend_url() == DEFAULT_BACKEND_URL


def test_env_strips_trailing_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BACKEND_URL", "http://localhost:8000/")
    assert get_backend_url() == "http://localhost:8000"
