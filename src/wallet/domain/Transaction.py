from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from wallet.domain.Amount import Amount
from wallet.domain.Type import TxStatus

if TYPE_CHECKING:
    from wallet.domain.Address import Address


@dataclass
class Transaction:

    txid: str | None = None
    to_address: list[str] = field(default_factory=list)
    amount: list[Amount] = field(default_factory=list)
    fee: Amount = field(default_factory=lambda: Amount(0))
    change_address: Address | None = None
    status: TxStatus = TxStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
