"""Kryptografie-Service: Passwort-Prüfung und Verschlüsselung sensitiver Daten.

Es werden ausschließlich geprüfte Primitive aus `cryptography` verwendet
(scrypt, HKDF-SHA256, AES-256-GCM) – keine eigene Krypto-Implementierung.

/PND 020/: Weder Passwörter, Salts, Schlüssel noch Klartexte dürfen in Logs oder
Fehlermeldungen gelangen. Dieses Modul loggt nicht und wirft nur Exceptions mit
allgemeinen Meldungen, die keine geheimen Werte enthalten.
"""

from __future__ import annotations

import hmac
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from dotenv import load_dotenv

from wallet.domain import User

# Lade Environment-Variablen aus .env.crypto
load_dotenv(".env.crypto")

# --- KDF-Parameter (dokumentiert zu T0005) ------------------------------------
SCRYPT_N = 2**16
SCRYPT_R = 8
SCRYPT_P = 1

KEY_LENGTH = 32  # AES-256: 256 Bit = 32 Byte
SALT_LENGTH = 16  # 16 Byte aus os.urandom
NONCE_LENGTH = 12  # GCM-Standard-Nonce, zufällig, wird vor den Ciphertext gestellt
TAG_LENGTH = 16  # GCM-Authentifizierungs-Tag

# HKDF-Info-Strings: domain-getrennte Ableitung von Passwort-Hash und
# Verschlüsselungsschlüssel aus demselben scrypt-Masterkey (ein Salt pro User).
# Werden aus der Environment-Datei geladen
HKDF_INFO_PASSWORD_HASH = os.environ.get("HKDF_INFO_PASSWORD_HASH", "wallet/password-hash").encode()
HKDF_INFO_ENCRYPTION_KEY = os.environ.get(
    "HKDF_INFO_ENCRYPTION_KEY", "wallet/encryption-key"
).encode()


class CryptoService:
    """Passwort-Ableitung (scrypt + HKDF) und AES-256-GCM-Verschlüsselung."""

    def generate_salt(self) -> bytes:
        """Erzeugt ein neues 16-Byte-Salt aus `os.urandom`."""
        return os.urandom(SALT_LENGTH)

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Leitet mit scrypt einen 32-Byte-Masterkey aus Passwort + Salt ab."""
        if len(salt) != SALT_LENGTH:
            raise ValueError(f"Salt muss genau {SALT_LENGTH} Byte lang sein")
        kdf = Scrypt(salt=salt, length=KEY_LENGTH, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
        return kdf.derive(password.encode("utf-8"))

    def derive_password_hash(self, password: str, salt: bytes) -> bytes:
        """Passwort-Hash (32 Byte) zur Speicherung – getrennt vom Verschlüsselungsschlüssel."""
        return self._hkdf(self.derive_key(password, salt), HKDF_INFO_PASSWORD_HASH)

    def derive_encryption_key(self, password: str, salt: bytes) -> bytes:
        """Verschlüsselungsschlüssel (AES-256) – getrennt vom Passwort-Hash."""
        return self._hkdf(self.derive_key(password, salt), HKDF_INFO_ENCRYPTION_KEY)

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        """Verschlüsselt mit AES-256-GCM; die zufällige 12-Byte-Nonce steht vor dem Ciphertext.

        Rückgabe: Nonce (12 Byte) + Ciphertext + GCM-Tag (16 Byte).
        """
        self._check_key(key)
        nonce = os.urandom(NONCE_LENGTH)
        ciphertext = AESGCM(key).encrypt(nonce, data, None)
        return nonce + ciphertext

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        """Entschlüsselt `Nonce + Ciphertext + Tag` mit AES-256-GCM.

        Wirft `cryptography.exceptions.InvalidTag` bei manipuliertem Ciphertext oder
        falschem Schlüssel (dabei wird kein Klartext zurückgegeben) und `ValueError`,
        wenn die Daten kürzer als Nonce + Tag sind.
        """
        self._check_key(key)
        if len(data) < NONCE_LENGTH + TAG_LENGTH:
            raise ValueError("Daten zu kurz für Nonce + GCM-Tag")
        nonce, ciphertext = data[:NONCE_LENGTH], data[NONCE_LENGTH:]
        return AESGCM(key).decrypt(nonce, ciphertext, None)

    def verify_password(self, password: str, user: User) -> bool:
        """Prüft das Passwort konstantzeitlich gegen den gespeicherten Hash."""
        candidate = self.derive_password_hash(password, user.salt)
        return hmac.compare_digest(candidate, user.password_hash)

    @staticmethod
    def _hkdf(master_key: bytes, info: bytes) -> bytes:
        hkdf = HKDF(algorithm=hashes.SHA256(), length=KEY_LENGTH, salt=None, info=info)
        return hkdf.derive(master_key)

    @staticmethod
    def _check_key(key: bytes) -> None:
        if len(key) != KEY_LENGTH:
            raise ValueError(f"Schlüssel muss genau {KEY_LENGTH} Byte lang sein")
