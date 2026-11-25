from __future__ import annotations

from enum import Enum


class Network(Enum):
    TESTNET = "testnet4"
    MAINNET = "bitcoin"


class TxStatus(Enum):
    DRAFT = "DRAFT"
    BROADCAST = "BROADCAST"
    CONFIRMED = "CONFIRMED"
