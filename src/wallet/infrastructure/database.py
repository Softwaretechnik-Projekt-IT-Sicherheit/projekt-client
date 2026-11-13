from __future__ import annotations

import sqlite3

from wallet.infrastructure.crypto_service import CryptoService
from wallet.domain.user import User
from wallet.domain.wallet import Wallet
from wallet.domain.enums import Network
from wallet.domain.address import Address


class Database:

    # Init Database Connection
    def __init__(self, path: str, crypto: CryptoService) -> None:
        self._path: str = path
        self._conn: sqlite3.Connection = sqlite3.connect(self._path)
        self._crypto: CryptoService = crypto

    # Close Database Connection
    def __del__(self):
        if self._conn != None:
            self._conn.close()

    #########################
    # Loead Data
    #########################

    # Request User by name (needed for prove of Hash, because Hash Needs Salt)
    def get_user(self, name: str) -> User:
        cursor = self._conn.cursor()

        # Requesting all Users with given name
        cursor.execute("SELECT id, username, password_hash, salt FROM User WHERE username = ?", (name, ))
        rows = cursor.fetchall()
        user = None
        if len(rows) == 1: # User is in Database
            user = User(row[1], row[2].encode(), row[3].encode(), id =int(rows[0]))
        elif len(rows) == 2: # Multiple User with the same in in Database
            raise Exception("Too Many Users")

        cursor.close()
        return user

    # Load all Wallets for a user 
    def load_wallets(self, user: User) -> None:
        cursor = self._conn.cursor()

        if user.get_id() == None:
            return

        # Get all Wallets of User
        cursor.execute("SELECT id, name, network, prkey, xpub FROM Wallet WHERE user = ?", (User.get_id(),))

        for row in cursor:
            wallet = Wallet(row[1], Network(row[2]), row[4], self._crypto.decrypt(row[3]), id=int(row[0]))
            user.add_wallet(wallet)

        cursor.close()

    # Load all Addresses for a Wallet
    def load_addresses_transactions(self, wallet: Wallet) -> None:
        cursor = self._conn.cursor()

        if wallet.get_id() == None:
            return

        # Get all Adresses of Wallet
        cursor.execute("SELECT id, address, prkey, balance, updated_at, refund_address FROM Address WHERE wallet = ?", (wallet.get_id(), ))

        for row in cursor:
            address = Address(row[1], row[3], datetime.utcfromtimestamp(int(row[4])), self._crypto.decrypt(row[3]), bool(int(row[5])), int(row[0]))
            wallet.append(address)

        cursor.close()
