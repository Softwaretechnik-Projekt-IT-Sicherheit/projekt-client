from __future__ import annotations

from dataclasses import dataclass

from wallet.domain.amount import Amount


@dataclass(frozen=True)
class Utxo:

    txid: str
    output_n: int
    address: str
    value: Amount
    confirmations: int
