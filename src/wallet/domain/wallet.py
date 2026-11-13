from __future__ import annotations

from dataclasses import dataclass, field

from wallet.domain.address import Address
from wallet.domain.amount import Amount
from wallet.domain.enums import Network


@dataclass
class Wallet:
    _id: int
    _name: str
    _network: Network
    _xpub: str
    _prkey: str # in WIF (Wallet import Format)
    _addresses: list[Address] = field(default_factory=list)

    def __init__(self, name: str, network: Network, xpub: str, prkey, id: int = None):
        self._name = name
        self._network = network
        self._id = id
        self._xpub = xpub
        self._prkey = prkey

    def next_index(self, chain: int) -> int:
        raise NotImplementedError

    def total_balance(self) -> Amount:
        amount = Amount.from_str("0")
        for address in self._addresses:
            amount += address.get_balance()
        return amount

    ###################################
    # Getter
    ###################################

    def get_id(self) -> int:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_network(self) -> Network:
        return self._network

    def get_xpub(self) -> str:
        return self._xpub

    def get_prkey(self) -> str:
        return self.prkey

    def get_addresses(self) -> list[Address]:
        return self._addresses

    ###################################
    # Setter
    ###################################

    # Used after saving newly created Wallet
    def set_id(self, id: int):
        self._id = id
    
    # Used by name change
    def set_name(self, name: str):
        self._name = name

    # Network and Keys can not be changed

    # add Address to Wallet
    def add_address(self, address: Address):
        self._addresses.append(address)