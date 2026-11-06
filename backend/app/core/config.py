"""Configuração central da aplicação.

Todos os valores podem ser sobrescritos por variáveis de ambiente com prefixo ``MAYA_``
(ex.: ``MAYA_DATA_DIR``, ``MAYA_WORKSPACE``) ou por um arquivo ``backend/.env``.
"""

from __future__ import annotations

import os
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "Maya-marketing"
APP_VERSION = "0.1.0"


class Workspace(StrEnum):
    """Espaço de dados. Real e demonstração usam ARQUIVOS DE BANCO SEPARADOS,
    o que impede fisicamente a mistura de dados de demonstração com dados reais."""

    REAL = "real"
    DEMO = "demo"


def _default_data_dir() -> Path:
    # No Windows os dados ficam em %LOCALAPPDATA%\MayaMarketing (fora do repositório).
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "MayaMarketing"
    return Path.home() / ".maya-marketing"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MAYA_", env_file=".env", extra="ignore")

    data_dir: Path = Field(default_factory=_default_data_dir)
    workspace: Workspace = Workspace.REAL
    host: str = "127.0.0.1"  # nunca expor na rede local por padrão
    port: int = 8765
    log_level: str = "INFO"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "tauri://localhost",
        "http://tauri.localhost",
    ]
    backup_keep: int = 30  # quantidade de backups mantidos (os mais antigos são removidos)

    @property
    def db_path(self) -> Path:
        name = "maya.db" if self.workspace == Workspace.REAL else "maya-demo.db"
        return self.data_dir / name

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.db_path.as_posix()}"

    @property
    def log_dir(self) -> Path:
        return self.data_dir / "logs"

    @property
    def backup_dir(self) -> Path:
        return self.data_dir / "backups" / self.workspace.value

    def ensure_dirs(self) -> None:
        for path in (self.data_dir, self.log_dir, self.backup_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
