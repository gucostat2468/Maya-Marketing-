from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch) -> Iterator[TestClient]:
    """Cada teste usa uma pasta de dados temporária e um banco novo."""
    monkeypatch.setenv("MAYA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("MAYA_WORKSPACE", "real")
    from app.core.config import get_settings
    from app.db.session import dispose_engine

    get_settings.cache_clear()
    dispose_engine()
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
    dispose_engine()
    get_settings.cache_clear()
