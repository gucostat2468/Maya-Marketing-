"""Modelos ORM. Importar aqui garante que o Alembic enxergue todas as tabelas."""

from app.models.core import AppSetting, AuditLog, ImportBatch, Integration, Platform

__all__ = ["AppSetting", "AuditLog", "ImportBatch", "Integration", "Platform"]
