"""Armazenamento seguro de credenciais.

Usa a biblioteca ``keyring``, que no Windows grava no **Gerenciador de Credenciais do
Windows** (Windows Credential Manager). Tokens NUNCA vão para o banco, para o código-fonte,
para os logs ou para o frontend: a API só informa se uma credencial existe.
"""

from __future__ import annotations

import logging
from contextlib import suppress

import keyring
from keyring.errors import KeyringError

SERVICE = "maya-marketing"
log = logging.getLogger(__name__)


def _key(integration: str, name: str) -> str:
    return f"{integration}:{name}"


def set_secret(integration: str, name: str, value: str) -> None:
    keyring.set_password(SERVICE, _key(integration, name), value)
    log.info("Credencial gravada para integração %s (%s)", integration, name)


def get_secret(integration: str, name: str) -> str | None:
    """Uso exclusivo do backend (conectores). Nunca retornar em resposta HTTP."""
    try:
        return keyring.get_password(SERVICE, _key(integration, name))
    except KeyringError:
        log.warning("Cofre de credenciais indisponível ao ler %s", integration)
        return None


def has_secret(integration: str, name: str) -> bool:
    return get_secret(integration, name) is not None


def delete_secret(integration: str, name: str) -> None:
    with suppress(KeyringError):
        keyring.delete_password(SERVICE, _key(integration, name))
