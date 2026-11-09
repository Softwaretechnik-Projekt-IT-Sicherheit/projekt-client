from __future__ import annotations

from dataclasses import dataclass, field

from wallet.domain.Address import Address
from wallet.domain.Amount import Amount
from wallet.domain.Type import Network


@dataclass
class Wallet:

    id: int
    name: str
    network: Network
    xpub: str
    addresses: list[Address] = field(default_factory=list)

    def next_index(self, chain: int) -> int:
        raise NotImplementedError

    def total_balance(self) -> Amount:
        raise NotImplementedError
