from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Integration

router = APIRouter(tags=["integrações"])


@router.get("/integrations")
def list_integrations(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(Integration)
        .options(joinedload(Integration.platform))
        .order_by(Integration.planned_phase, Integration.name)
    )
    # Nenhum segredo é retornado: credenciais ficam no cofre do Windows.
    return [
        {
            "code": i.code,
            "name": i.name,
            "platform": i.platform.name if i.platform else None,
            "auth_type": i.auth_type,
            "status": i.status,
            "planned_phase": i.planned_phase,
            "supports_csv": i.supports_csv,
            "last_sync_at": i.last_sync_at.isoformat() if i.last_sync_at else None,
            "last_error": i.last_error,
            "notes": i.notes,
        }
        for i in rows
    ]
