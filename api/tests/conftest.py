from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from diagnostico_api.config import Settings
from diagnostico_api.main import create_app


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(Settings(data_dir=tmp_path)))
