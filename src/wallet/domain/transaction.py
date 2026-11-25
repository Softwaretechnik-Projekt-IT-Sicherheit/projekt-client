from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from wallet.domain.amount import Amount
from wallet.domain.enums import TxStatus

if TYPE_CHECKING:
    from wallet.domain.address import Address


@dataclass
class Transaction:
    _id: int | None = None
    _txid: str | None = None
    _to_address: list[str] = field(default_factory=list)
    _amount: list[Amount] = field(default_factory=list)
    _fee: Amount = field(default_factory=lambda: Amount(0))
    _change_address: Address | None = None
    _status: TxStatus = TxStatus.DRAFT
    _created_at: datetime = field(default_factory=datetime.now)

    def __init__(
        self,
        fee: Amount,
        status: TxStatus,
        created_at: datetime,
        change_address: Address,
        txid: str | None = None,
        id: int | None = None,
    ):
        self._fee = fee
        self._status = status
        self._created_at = created_at
        self._txid = txid
        self._id = id
        self._change_address = change_address
        self._to_address = list()
        self._amount = list()

    ###############################
    # Getter
    ###############################

    def get_id(self) -> int | None:
        return self._id

    def get_txid(self) -> str | None:
        return self._txid

    def get_to_address(self) -> list[str]:
        return self._to_address

    def get_amount(self) -> list[Amount]:
        return self._amount

    def get_fee(self) -> Amount:
        return self._fee

    def get_change_address(self) -> Address | None:
        return self._change_address

    def get_status(self) -> TxStatus:
        return self._status

    def get_created_at(self) -> datetime:
        return self._created_at

    #################################
    # Setter
    #################################

    def set_id(self, id: int) -> None:
        self._id = id

    def set_txid(self, txid: str) -> None:
        self._txid = txid

    def add_to_address(self, address: str, amount: Amount) -> None:
        self._to_address.append(address)
        self._amount.append(amount)

    def set_fee(self, fee: Amount) -> None:
        self._fee = fee

    def set_change_address(self, change_address: Address) -> None:
        self._change_address = change_address

    def set_status(self, status: TxStatus) -> None:
        self._status = status
