from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from wallet.domain.amount import Amount

if TYPE_CHECKING:
    from wallet.domain.transaction import Transaction


@dataclass
class Address:
    _address: str
    _balance: Amount = field(default_factory=lambda: Amount(0))
    _updated_at: datetime = field(default_factory=datetime.now)
    _transactions: list[Transaction] = field(default_factory=list)
    _refund_address: bool = False
    _prkey: str

    def __init__(self, address: str, balance: Amount, updated_at: datetime, private_key: str, refund_address: bool = True):
        self._address = address
        self._balance = balance
        self._updated_at = updated_at
        self._refund_address = refund_address
        self._prkey = private_key

    ######################
    # Getter
    ######################

    def get_address(self) -> str:
        return self._address

    def get_balance(self) -> Amount:
        return self._balance

    def get_updated_at(self) -> datetime:
        return self._updated_at

    def get_transactions(self) -> list[Transaction]:
        return self._transactions

    def is_refund_address(self) -> bool:
        return is_refund_address

    ########################
    # Setter
    ########################

    def set_updated_at(self, utime: datetime):
        self._updated_at = utime

    def add_transaction(self, transaction: Transaction):
        self._transactions.append(transaction)
