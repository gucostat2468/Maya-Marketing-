from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import APP_VERSION, get_settings
from app.db.session import get_db
from app.models import AuditLog
from app.services.modules import MODULES
from app.services.system import system_info

router = APIRouter(tags=["sistema"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, Any]:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "version": APP_VERSION, "workspace": get_settings().workspace.value}


@router.get("/system")
def system(db: Session = Depends(get_db)) -> dict[str, Any]:
    return system_info(db, get_settings())


@router.get("/modules")
def modules() -> list[dict[str, Any]]:
    return MODULES


@router.get("/audit")
def audit(limit: int = 50, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(select(AuditLog).order_by(AuditLog.at.desc()).limit(min(limit, 200)))
    return [
        {
            "id": r.id,
            "at": r.at.isoformat(),
            "actor": r.actor,
            "action": r.action,
            "entity": r.entity,
            "entity_id": r.entity_id,
            "detail": r.detail,
        }
        for r in rows
    ]
