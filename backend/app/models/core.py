"""Tabelas da Fase 1 (fundação).

As entidades de marketing (Campaigns, Ads, MarketingMetrics, Leads...) entram nas
Fases 2 e 3 por migrations incrementais, sem reescrever estas tabelas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, utcnow


class Platform(TimestampMixin, Base):
    """Plataformas de origem de dados (Google Ads, Meta Ads, Instagram...)."""

    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(20))  # ads | social | analytics | crm
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    integrations: Mapped[list[Integration]] = relationship(back_populates="platform")


class Integration(TimestampMixin, Base):
    """Registro de conectores. NÃO armazena tokens (ficam no cofre do Windows)."""

    __tablename__ = "integrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    platform_id: Mapped[int | None] = mapped_column(
        ForeignKey("platforms.id", ondelete="SET NULL"), index=True
    )
    auth_type: Mapped[str] = mapped_column(String(30))  # oauth2 | csv | api_key | none
    # not_configured | configured | connected | error | planned
    status: Mapped[str] = mapped_column(String(20), default="not_configured")
    planned_phase: Mapped[int] = mapped_column(Integer)
    supports_csv: Mapped[bool] = mapped_column(Boolean, default=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    platform: Mapped[Platform | None] = relationship(back_populates="integrations")


class ImportBatch(Base):
    """Cada arquivo importado. O hash SHA-256 é único: reimportar o mesmo arquivo
    é bloqueado, impedindo que uma importação duplicada infle os resultados."""

    __tablename__ = "imports"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(60), index=True)  # ex.: google_ads_csv
    filename: Mapped[str] = mapped_column(String(255))
    file_sha256: Mapped[str] = mapped_column(String(64), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|completed|failed
    row_count: Mapped[int | None] = mapped_column(Integer)
    rows_rejected: Mapped[int | None] = mapped_column(Integer)
    period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditLog(Base):
    """Trilha de auditoria de ações relevantes (backup, restauração, alterações)."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    actor: Mapped[str] = mapped_column(String(60), default="usuario_local")
    action: Mapped[str] = mapped_column(String(60))
    entity: Mapped[str | None] = mapped_column(String(60))
    entity_id: Mapped[str | None] = mapped_column(String(60))
    detail: Mapped[dict[str, Any] | None] = mapped_column(JSON)


class AppSetting(TimestampMixin, Base):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[Any] = mapped_column(JSON)
