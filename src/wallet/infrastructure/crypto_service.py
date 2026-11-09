from __future__ import annotations

from wallet.domain import User


class CryptoService:
    def derive_key(self, password: str, salt: bytes) -> bytes:
        raise NotImplementedError

    def encrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError

    def decrypt(self, data: bytes, key: bytes) -> bytes:
        raise NotImplementedError

    def verify_password(self, password: str, user: User) -> bool:
        raise NotImplementedError
