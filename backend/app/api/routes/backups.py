from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.migrate import upgrade_to_head
from app.db.session import dispose_engine, get_db
from app.services import audit
from app.services.backup import BackupError, create_backup, list_backups, restore_backup

router = APIRouter(tags=["backups"])
CONFIRMATION = "RESTAURAR"


class RestoreRequest(BaseModel):
    confirmation: str


@router.get("/backups")
def backups() -> list[dict[str, Any]]:
    return [asdict(b) for b in list_backups(get_settings())]


@router.post("/backups", status_code=201)
def new_backup(db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        info = create_backup(get_settings())
    except BackupError as exc:
        raise HTTPException(409, str(exc)) from exc
    audit.record(db, "backup.created", "backup", info.name)
    return asdict(info)


@router.post("/backups/{name}/restore")
def restore(name: str, body: RestoreRequest) -> dict[str, Any]:
    if body.confirmation != CONFIRMATION:
        raise HTTPException(422, f"Digite {CONFIRMATION} para confirmar a restauração.")
    settings = get_settings()
    dispose_engine()
    try:
        safety = restore_backup(settings, name)
    except BackupError as exc:
        raise HTTPException(400, str(exc)) from exc
    upgrade_to_head()  # backup antigo pode estar numa versão anterior do esquema
    db = next(get_db())
    try:
        audit.record(db, "backup.restored", "backup", name, {"safety_backup": safety.name})
    finally:
        db.close()
    return {"restored": name, "safety_backup": safety.name}
