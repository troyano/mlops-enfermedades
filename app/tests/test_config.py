import pytest

from diagnostico_ui.config import DEFAULT_API_URL, get_api_url


def test_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("API_URL", raising=False)
    assert get_api_url() == DEFAULT_API_URL


def test_env_strips_trailing_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_URL", "http://localhost:8000/")
    assert get_api_url() == "http://localhost:8000"
