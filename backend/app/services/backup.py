"""Backup e restauração do banco SQLite.

Usa a API nativa de backup do SQLite (``Connection.backup``), que gera uma cópia
consistente mesmo com o banco aberto, ao contrário de copiar o arquivo.
"""

from __future__ import annotations

import logging
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import Settings

log = logging.getLogger(__name__)
_NAME_RE = re.compile(r"^maya-(real|demo)-\d{8}-\d{6}(-\d+)?(-pre-restauracao)?\.db$")


class BackupError(Exception):
    pass


@dataclass
class BackupInfo:
    name: str
    size_bytes: int
    created_at: str


def _sqlite_copy(src: Path, dst: Path) -> None:
    with sqlite3.connect(src) as source, sqlite3.connect(dst) as target:
        source.backup(target)
    # Conexões do módulo sqlite3 não fecham com "with"; fechamos explicitamente.
    source.close()
    target.close()


def _integrity_ok(path: Path) -> bool:
    conn = sqlite3.connect(path)
    try:
        row = conn.execute("PRAGMA integrity_check").fetchone()
        has_schema = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE name='alembic_version'"
        ).fetchone()
        return row is not None and row[0] == "ok" and has_schema is not None
    except sqlite3.DatabaseError:
        return False
    finally:
        conn.close()


def create_backup(settings: Settings, suffix: str = "") -> BackupInfo:
    if not settings.db_path.exists():
        raise BackupError("O banco de dados ainda não existe.")
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    base = f"maya-{settings.workspace.value}-{stamp}"
    target = settings.backup_dir / f"{base}{suffix}.db"
    counter = 1
    while target.exists():
        target = settings.backup_dir / f"{base}-{counter}{suffix}.db"
        counter += 1
    _sqlite_copy(settings.db_path, target)
    log.info("Backup criado: %s", target.name)
    _prune(settings)
    return _info(target)


def _info(path: Path) -> BackupInfo:
    stat = path.stat()
    return BackupInfo(
        path.name, stat.st_size, datetime.fromtimestamp(stat.st_mtime, UTC).isoformat()
    )


def list_backups(settings: Settings) -> list[BackupInfo]:
    files = [p for p in settings.backup_dir.glob("maya-*.db") if _NAME_RE.match(p.name)]
    return [_info(p) for p in sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)]


def _prune(settings: Settings) -> None:
    regular = [b for b in list_backups(settings) if "pre-restauracao" not in b.name]
    for old in regular[settings.backup_keep :]:
        (settings.backup_dir / old.name).unlink(missing_ok=True)


def resolve_backup(settings: Settings, name: str) -> Path:
    # Validação estrita do nome: impede acesso a arquivos fora da pasta (path traversal).
    if not _NAME_RE.match(name):
        raise BackupError("Nome de backup inválido.")
    path = settings.backup_dir / name
    if not path.is_file():
        raise BackupError("Backup não encontrado.")
    return path


_AUDIT_COLS = "at, actor, action, entity, entity_id, detail"


def _carry_over_audit(previous_db: Path, restored_db: Path) -> int:
    """A trilha de auditoria não volta no tempo: registros do banco atual que não existem
    no backup restaurado são copiados para ele. Retorna quantos foram preservados."""
    old = sqlite3.connect(previous_db)
    try:
        rows = old.execute(f"SELECT {_AUDIT_COLS} FROM audit_log").fetchall()
    finally:
        old.close()
    new = sqlite3.connect(restored_db)
    try:
        existing = set(new.execute(f"SELECT {_AUDIT_COLS} FROM audit_log").fetchall())
        missing = [r for r in rows if r not in existing]
        new.executemany(f"INSERT INTO audit_log ({_AUDIT_COLS}) VALUES (?, ?, ?, ?, ?, ?)", missing)
        new.commit()
        return len(missing)
    finally:
        new.close()


def restore_backup(settings: Settings, name: str) -> BackupInfo:
    """Restaura um backup. Antes, cria automaticamente um backup do estado atual.

    O chamador deve fechar as conexões do engine antes (``dispose_engine``).
    """
    source = resolve_backup(settings, name)
    if not _integrity_ok(source):
        raise BackupError("O arquivo de backup falhou na verificação de integridade.")
    safety = create_backup(settings, suffix="-pre-restauracao")
    _sqlite_copy(source, settings.db_path)
    _carry_over_audit(settings.backup_dir / safety.name, settings.db_path)
    log.info("Backup restaurado: %s (estado anterior salvo em %s)", name, safety.name)
    return safety
