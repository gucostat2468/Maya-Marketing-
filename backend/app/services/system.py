from __future__ import annotations

import sqlite3
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import APP_VERSION, Settings


def fts5_available() -> bool:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE VIRTUAL TABLE t USING fts5(x)")
        return True
    except sqlite3.OperationalError:
        return False
    finally:
        conn.close()


def system_info(db: Session, settings: Settings) -> dict[str, Any]:
    revision = db.execute(text("SELECT version_num FROM alembic_version")).scalar()
    return {
        "version": APP_VERSION,
        "workspace": settings.workspace.value,
        "data_dir": str(settings.data_dir),
        "db_path": str(settings.db_path),
        "db_size_bytes": settings.db_path.stat().st_size if settings.db_path.exists() else 0,
        "log_dir": str(settings.log_dir),
        "backup_dir": str(settings.backup_dir),
        "sqlite_version": sqlite3.sqlite_version,
        "fts5_available": fts5_available(),
        "schema_revision": revision,
    }
