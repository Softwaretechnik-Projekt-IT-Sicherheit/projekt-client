"""Tests für den CryptoService (T0005): scrypt-Ableitung, AES-256-GCM, Passwort-Prüfung."""

from __future__ import annotations

import os
import time

import pytest
from cryptography.exceptions import InvalidTag

from wallet.domain import User
from wallet.infrastructure import CryptoService, crypto_service
from wallet.infrastructure.crypto_service import (
    HKDF_INFO_ENCRYPTION_KEY,
    HKDF_INFO_PASSWORD_HASH,
    KEY_LENGTH,
    NONCE_LENGTH,
    SALT_LENGTH,
    SCRYPT_N,
    SCRYPT_P,
    SCRYPT_R,
    TAG_LENGTH,
)

PASSWORD = "correct horse battery staple"  # noqa: S105  # nur ein Testwert, kein echtes Secret


@pytest.fixture
def fast_scrypt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Senkt die scrypt-Kosten für schnelle Tests (Real-Parameter-Test läuft ohne Fixture)."""
    monkeypatch.setattr(crypto_service, "SCRYPT_N", 2**14)


def make_user(crypto: CryptoService, password: str = PASSWORD) -> User:
    salt = crypto.generate_salt()
    password_hash = crypto.derive_password_hash(password, salt)
    return User(id=1, username="alice", password_hash=password_hash, salt=salt)


def test_kdf_parameters_documented_and_sane() -> None:
    # Ziel: ca. 0,2–0,5 s pro Ableitung -> scrypt N=2^16, r=8, p=1 (OWASP)
    assert SCRYPT_N >= 2**15
    assert SCRYPT_R >= 8
    assert SCRYPT_P >= 1
    assert KEY_LENGTH == 32  # AES-256
    assert SALT_LENGTH == 16
    assert NONCE_LENGTH == 12
    assert TAG_LENGTH == 16
    # getrennte Ableitung für Passwort-Hash und Verschlüsselungsschlüssel
    assert HKDF_INFO_PASSWORD_HASH != HKDF_INFO_ENCRYPTION_KEY


def test_derive_key_with_real_parameters() -> None:
    crypto = CryptoService()
    start = time.perf_counter()
    key = crypto.derive_key(PASSWORD, crypto.generate_salt())
    duration = time.perf_counter() - start
    assert len(key) == KEY_LENGTH
    # Zielbereich 0,2–0,5 s; großzügige Obergrenze, damit langsame CI-Runner nicht fehlschlagen
    assert duration < 3


def test_generate_salt() -> None:
    crypto = CryptoService()
    salt1, salt2 = crypto.generate_salt(), crypto.generate_salt()
    assert len(salt1) == SALT_LENGTH
    assert salt1 != salt2


def test_derive_key_deterministic_and_sensitive(fast_scrypt: None) -> None:
    crypto = CryptoService()
    salt = crypto.generate_salt()
    assert crypto.derive_key(PASSWORD, salt) == crypto.derive_key(PASSWORD, salt)
    assert crypto.derive_key(PASSWORD, salt) != crypto.derive_key("wrong", salt)
    assert crypto.derive_key(PASSWORD, salt) != crypto.derive_key(PASSWORD, crypto.generate_salt())


def test_derive_key_rejects_wrong_salt_length(fast_scrypt: None) -> None:
    with pytest.raises(ValueError, match="Salt"):
        CryptoService().derive_key(PASSWORD, b"zu-kurz")


def test_password_hash_and_encryption_key_are_separate(fast_scrypt: None) -> None:
    crypto = CryptoService()
    salt = crypto.generate_salt()
    password_hash = crypto.derive_password_hash(PASSWORD, salt)
    encryption_key = crypto.derive_encryption_key(PASSWORD, salt)
    assert len(password_hash) == KEY_LENGTH
    assert len(encryption_key) == KEY_LENGTH
    assert password_hash != encryption_key


def test_encrypt_decrypt_roundtrip(fast_scrypt: None) -> None:
    crypto = CryptoService()
    key = crypto.derive_encryption_key(PASSWORD, crypto.generate_salt())
    for data in (b"hello wallet", b"", bytes(range(256))):
        encrypted = crypto.encrypt(data, key)
        assert encrypted != data
        assert len(encrypted) == NONCE_LENGTH + len(data) + TAG_LENGTH
        assert crypto.decrypt(encrypted, key) == data


def test_encrypt_uses_random_nonce() -> None:
    crypto = CryptoService()
    key = os.urandom(KEY_LENGTH)
    data = b"gleiche Daten"
    assert crypto.encrypt(data, key) != crypto.encrypt(data, key)


def test_decrypt_tampered_ciphertext_raises() -> None:
    crypto = CryptoService()
    key = os.urandom(KEY_LENGTH)
    encrypted = bytearray(crypto.encrypt(b"secret", key))
    encrypted[-1] ^= 0x01  # ein Bit im Ciphertext/Tag kippen
    with pytest.raises(InvalidTag):
        crypto.decrypt(bytes(encrypted), key)


def test_decrypt_tampered_nonce_raises() -> None:
    crypto = CryptoService()
    key = os.urandom(KEY_LENGTH)
    encrypted = bytearray(crypto.encrypt(b"secret", key))
    encrypted[0] ^= 0x01  # ein Bit in der Nonce kippen
    with pytest.raises(InvalidTag):
        crypto.decrypt(bytes(encrypted), key)


def test_decrypt_with_wrong_key_raises() -> None:
    crypto = CryptoService()
    key = os.urandom(KEY_LENGTH)
    encrypted = crypto.encrypt(b"secret", key)
    with pytest.raises(InvalidTag):
        crypto.decrypt(encrypted, os.urandom(KEY_LENGTH))


def test_decrypt_too_short_raises() -> None:
    with pytest.raises(ValueError, match="zu kurz"):
        CryptoService().decrypt(b"kurz", os.urandom(KEY_LENGTH))


def test_encrypt_rejects_wrong_key_length() -> None:
    with pytest.raises(ValueError, match="Schlüssel"):
        CryptoService().encrypt(b"x", b"0" * 16)


def test_verify_password(fast_scrypt: None) -> None:
    crypto = CryptoService()
    user = make_user(crypto)
    assert crypto.verify_password(PASSWORD, user) is True
    assert crypto.verify_password("falsches passwort", user) is False


def test_verify_password_with_tampered_hash(fast_scrypt: None) -> None:
    crypto = CryptoService()
    user = make_user(crypto)
    tampered = bytearray(user.password_hash)
    tampered[0] ^= 0x01
    user.password_hash = bytes(tampered)
    assert crypto.verify_password(PASSWORD, user) is False


def test_error_messages_do_not_leak_secrets() -> None:
    # /PND 020/: keine Passwörter/Schlüssel in Fehlermeldungen
    crypto = CryptoService()
    key = os.urandom(KEY_LENGTH)
    wrong_key = os.urandom(KEY_LENGTH)
    encrypted = crypto.encrypt(PASSWORD.encode("utf-8"), key)
    with pytest.raises(InvalidTag) as excinfo:
        crypto.decrypt(encrypted, wrong_key)
    message = str(excinfo.value).encode("utf-8")
    assert PASSWORD.encode("utf-8") not in message
    assert key not in message
    assert wrong_key not in message
