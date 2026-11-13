from __future__ import annotations

from dataclasses import dataclass, field

from wallet.domain.wallet import Wallet


@dataclass
class User:
    _id: int
    _username: str
    _password_hash: bytes
    _salt: bytes
    _wallets: list[Wallet] = field(default_factory=list)

    # creates Wallet object (if not from database: id not set yet)
    def __init__(self, username: str, password_hash: bytes, salt: bytes, id = None):
        self._id = id
        self._username = username
        self._password_hash = password_hash
        self._salt = salt
        self._wallets = []


    ####################################
    # Getters
    ####################################
    def get_id(self) -> int:
        return self._id

    def get_username(self) -> str:
        return self._username

    def get_password_hash(self) -> bytes:
        return self._password_hash

    def get_salt(self) -> bytes:
        return self._salt

    def get_wallets(self) -> list[Wallet]:
        return self._wallets

    # Get a singel Wallet by its name
    def get_wallet(self, walletname: str) -> Wallet:
        for wallet in self._wallets:
            if wallet.get_name() == walletname:
                return wallet
        return None

    
    #####################################
    # Setter
    #####################################

    # used when newly created User user first saved in Database
    def set_id(self, id: int):
        self._id = id

    # used when username is changed
    def set_username(self, username: str):
        self._username = username

    # used when password is changed
    def set_password_hash(self, password_hash: bytes):
        self._password_hash = password_hash

    # Salt can not be changed
    
    # to add a new Wallet
    def add_wallet(self, wallet: Wallet):
        self._wallets.append(wallet)

    # Wallet can not be removed, because it does not make sens in context of Blockchains

    
