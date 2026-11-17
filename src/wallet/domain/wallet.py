from __future__ import annotations

from dataclasses import dataclass, field

from wallet.domain.address import Address
from wallet.domain.amount import Amount
from wallet.domain.enums import Network


@dataclass
class Wallet:
    _name: str
    _network: Network
    _xpub: str
    _prkey: str  # in WIF (Wallet import Format)
    _id: int | None = None
    _addresses: list[Address] = field(default_factory=list)
    _index: int = 0

    def __init__(
        self,
        name: str,
        network: Network,
        xpub: str,
        prkey: str,
        index: int,
        id: int | None = None,
    ):
        self._name = name
        self._network = network
        self._id = id
        self._xpub = xpub
        self._prkey = prkey
        self._index = index

    def next_index(self) -> int:
        return self._index

    def increment_index(self) -> None:
        self._index += 1

    def total_balance(self) -> Amount:
        amount = Amount.from_str("0")
        for address in self._addresses:
            amount += address.get_balance()
        return amount

    ###################################
    # Getter
    ###################################

    def get_id(self) -> int | None:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_network(self) -> Network:
        return self._network

    def get_xpub(self) -> str:
        return self._xpub

    def get_prkey(self) -> str:
        return self._prkey

    def get_addresses(self) -> list[Address]:
        return self._addresses

    def get_index(self) -> int:
        return self._index

    ###################################
    # Setter
    ###################################

    # Used after saving newly created Wallet
    def set_id(self, id: int) -> None:
        self._id = id

    # Used by name change
    def set_name(self, name: str) -> None:
        self._name = name

    # Network and Keys can not be changed

    # add Address to Wallet
    def add_address(self, address: Address) -> None:
        self._addresses.append(address)
