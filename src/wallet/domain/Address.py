from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from wallet.domain.Amount import Amount

if TYPE_CHECKING:
    from wallet.domain.Transaction import Transaction


@dataclass
class Address:
    address: str
    balance: Amount = field(default_factory=lambda: Amount(0))
    updated_at: datetime = field(default_factory=datetime.now)
    transactions: list[Transaction] = field(default_factory=list)
    refund_address: bool = False

    def is_refund_address(self) -> bool:
        raise NotImplementedError
