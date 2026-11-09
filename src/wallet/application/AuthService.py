from __future__ import annotations

from wallet.application.Session import Session
from wallet.domain import User
from wallet.infrastructure import CryptoService, Database


class AuthService:

    def __init__(self, db: Database, crypto: CryptoService) -> None:
        self._db: Database = db
        self._crypto: CryptoService = crypto
        self._failed_attempts: dict[str, int] = {}

    def register(self, username: str, password: str) -> User:
        raise NotImplementedError

    def login(self, username: str, password: str) -> Session:
        raise NotImplementedError

    def _backoff(self, username: str) -> float:
        raise NotImplementedError
