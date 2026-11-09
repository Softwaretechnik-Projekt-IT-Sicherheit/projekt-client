from __future__ import annotations

from enum import Enum


class Network(Enum):
    TESTNET = "testnet"
    MAINNET = "bitcoin"


class TxStatus(Enum):
    DRAFT = "DRAFT"
    BROADCAST = "BROADCAST"
    CONFIRMED = "CONFIRMED"
