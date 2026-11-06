from __future__ import annotations

from alembic import context

import app.models  # noqa: F401  (registra as tabelas no metadata)
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_engine

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection = context.config.attributes.get("connection")
    if connection is not None:
        _run(connection)
        return
    with get_engine().connect() as conn:
        _run(conn)


def _run(connection) -> None:  # noqa: ANN001
    # render_as_batch: o SQLite não suporta ALTER COLUMN; o Alembic recria a tabela.
    context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
