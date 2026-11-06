import keyring
from keyring.backend import KeyringBackend

from app.core import secrets
from app.core.logging import redact


def test_redact_pii_in_logs():
    text = redact("lead maria@exemplo.com.br tel (11) 98765-4321 cpf 123.456.789-09 token=abc123")
    assert "maria@" not in text and "98765" not in text and "123.456" not in text
    assert "abc123" not in text
    assert "[email]" in text and "[telefone]" in text and "[cpf]" in text


class MemoryKeyring(KeyringBackend):
    priority = 1

    def __init__(self):
        super().__init__()
        self.store = {}

    def set_password(self, service, username, password):
        self.store[(service, username)] = password

    def get_password(self, service, username):
        return self.store.get((service, username))

    def delete_password(self, service, username):
        self.store.pop((service, username), None)


def test_secrets_roundtrip():
    previous = keyring.get_keyring()
    keyring.set_keyring(MemoryKeyring())
    try:
        assert not secrets.has_secret("google_ads_api", "refresh_token")
        secrets.set_secret("google_ads_api", "refresh_token", "valor")
        assert secrets.has_secret("google_ads_api", "refresh_token")
        secrets.delete_secret("google_ads_api", "refresh_token")
        assert not secrets.has_secret("google_ads_api", "refresh_token")
    finally:
        keyring.set_keyring(previous)
