from __future__ import annotations

import sqlite3

from wallet.infrastructure.crypto_service import CryptoService


class Database:
    def __init__(self, path: str, crypto: CryptoService) -> None:
        self._path: str = path
        self._conn: sqlite3.Connection = None  # type: ignore[assignment]
        self._crypto: CryptoService = crypto
        raise NotImplementedError
