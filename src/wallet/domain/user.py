from __future__ import annotations

from dataclasses import dataclass, field

from wallet.domain.wallet import Wallet


@dataclass
class User:
    id: int
    username: str
    password_hash: bytes
    salt: bytes
    wallets: list[Wallet] = field(default_factory=list)
