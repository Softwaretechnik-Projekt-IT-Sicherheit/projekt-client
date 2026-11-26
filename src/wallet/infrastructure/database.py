from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

from wallet.domain.address import Address
from wallet.domain.amount import Amount
from wallet.domain.enums import Network, TxStatus
from wallet.domain.transaction import Transaction
from wallet.domain.user import User
from wallet.domain.wallet import Wallet
from wallet.infrastructure.crypto_service import CryptoService


class Database:
    # Init Database Connection
    def __init__(self, path: str, crypto: CryptoService) -> None:
        self._path: str = path
        self._conn: sqlite3.Connection = sqlite3.connect(self._path)
        self._crypto: CryptoService = crypto

    # Close Database Connection
    def __del__(self) -> None:
        if self._conn is not None:
            self._conn.close()

    #########################
    # Loead Data
    #########################

    # Request User by name (needed for prove of Hash, because Hash Needs Salt)
    def get_user(self, name: str) -> User | None:
        cursor = self._conn.cursor()

        # Requesting all Users with given name
        cursor.execute(
            "SELECT id, username, password_hash, salt FROM User WHERE username = ?", (name,)
        )
        rows = cursor.fetchall()
        user = None
        if len(rows) == 1:  # User is in Database
            row = rows[0]
            user = User(row[1], row[2], row[3], id=row[0])
        elif len(rows) == 2:  # Multiple User with the same in in Database
            raise Exception("Too Many Users")

        cursor.close()
        return user

    # Load all Wallets for a user
    def load_wallets(self, user: User) -> None:
        cursor = self._conn.cursor()

        if user.get_id() is None:
            return

        # Get all Wallets of User
        cursor.execute(
            "SELECT id, name, network, prkey, xpub, add_num FROM Wallet WHERE user = ?",
            (user.get_id(),),
        )

        for row in cursor:
            wallet = Wallet(
                self._crypto.decrypt(row[1], self._crypto.derive_encryption_key()).decode(),
                Network(row[2]),
                self._crypto.decrypt(row[4], self._crypto.derive_encryption_key()).decode(),
                self._crypto.decrypt(row[3], self._crypto.derive_encryption_key()).decode(),
                int(row[5]),
                id=int(row[0]),
            )
            user.add_wallet(wallet)

        cursor.close()

    # Load all Addresses and Transactions for a Wallet
    def load_addresses_transactions(self, wallet: Wallet) -> None:
        cursor = self._conn.cursor()
        id_to_address: dict[int, Address] = dict()  # Used for connecting Transactions with Address
        id_to_transaction: dict[int, Transaction] = dict()  # Used for adding to_addresses

        if wallet.get_id() is None:
            return

        # Get all Adresses of Wallet
        cursor.execute(
            """SELECT id, address, prkey, balance, updated_at,
            refund_address FROM Address WHERE wallet = ?""",
            (wallet.get_id(),),
        )

        for row in cursor:
            address = Address(
                self._crypto.decrypt(row[1], self._crypto.derive_encryption_key()).decode(),
                Amount.from_str(
                    self._crypto.decrypt(row[3], self._crypto.derive_encryption_key()).decode()
                ),
                datetime.fromtimestamp(row[4], UTC).astimezone(),
                self._crypto.decrypt(row[2], self._crypto.derive_encryption_key()).decode(),
                bool(row[5]),
                row[0],
            )
            wallet.add_address(address)
            temp_id = address.get_id()
            if temp_id is not None:
                id_to_address[temp_id] = address

        # Get all Transactions for all Addresses in Wallet
        cursor.execute(
            """SELECT t.id, t.txid, t.fee, t.status, t.created_at, at.add_id,
            t.change_address FROM Transactions t INNER JOIN Address_Transaction at ON
            at.trans_id = t.id WHERE at.add_id IN (SELECT id FROM Address WHERE wallet = ?)""",
            (wallet.get_id(),),
        )

        for row in cursor:
            transaction = Transaction(
                Amount.from_str(
                    self._crypto.decrypt(row[2], self._crypto.derive_encryption_key()).decode()
                ),
                TxStatus(row[3]),
                datetime.fromtimestamp(row[4], UTC).astimezone(),
                id_to_address[row[6]],
                txid=None
                if row[1] is None
                else self._crypto.decrypt(row[1], self._crypto.derive_encryption_key()).decode(),
                id=row[0],
            )
            id_to_address[row[5]].add_transaction(transaction)
            id = transaction.get_id()
            if id is not None:
                id_to_transaction[id] = transaction

        # Get all to_address
        cursor.execute(
            """SELECT trans_id, address, amount FROM Target_Addresses
            WHERE trans_id IN (SELECT value FROM json_each(?))""",
            (json.dumps(list(id_to_transaction.keys())),),
        )

        for row in cursor:
            id_to_transaction[int(row[0])].add_to_address(
                self._crypto.decrypt(row[1], self._crypto.derive_encryption_key()).decode(),
                Amount.from_str(
                    self._crypto.decrypt(row[2], self._crypto.derive_encryption_key()).decode(),
                ),
            )

        cursor.close()

    # Saving all Transactions of an Address
    def save_transaction(self, address: Address) -> None:

        cursor = self._conn.cursor()

        for transaction in address.get_transactions():
            # Look if Transaction is already in Database
            if transaction.get_id() is None:
                # Add Transaction
                txid_temp = transaction.get_txid()
                change_address_temp = transaction.get_change_address()
                if txid_temp is not None and change_address_temp is not None:
                    cursor.execute(
                        """INSERT INTO Transactions (txid, fee, status, created_at, change_address)
                         VALUES (?, ?, ?, ?, ?)""",
                        (
                            None
                            if transaction.get_txid() is None
                            else self._crypto.encrypt(
                                txid_temp.encode(), self._crypto.derive_encryption_key()
                            ),
                            self._crypto.encrypt(
                                transaction.get_fee().to_btc().encode(),
                                self._crypto.derive_encryption_key(),
                            ),
                            transaction.get_status().value,
                            transaction.get_created_at().timestamp(),
                            None
                            if transaction.get_change_address() is None
                            else change_address_temp.get_id(),
                        ),
                    )

                    self._conn.commit()
                    cursor.execute("SELECT id FROM Transactions ORDER BY id DESC LIMIT 1")
                    id = cursor.fetchall()[0][0]
                    transaction.set_id(id)

                    # Add connection between Address and Transaction
                    cursor.execute(
                        "INSERT INTO Address_Transaction (add_id, trans_id) VALUES (?, ?)",
                        (
                            address.get_id(),
                            id,
                        ),
                    )

                    # Add all to_addresses
                    for to_address, amount in zip(
                        transaction.get_to_address(), transaction.get_amount(), strict=True
                    ):
                        cursor.execute(
                            """INSERT INTO Target_Addresses (address, amount, trans_id)
                             VALUES (?, ?, ?)""",
                            (
                                self._crypto.encrypt(
                                    to_address.encode(), self._crypto.derive_encryption_key()
                                ),
                                self._crypto.encrypt(
                                    amount.to_btc().encode(), self._crypto.derive_encryption_key()
                                ),
                                id,
                            ),
                        )
                    self._conn.commit()

            # Transaction already in Database
            else:
                # Save direct Changes
                txid_temp = transaction.get_txid()
                change_temp = transaction.get_change_address()
                if txid_temp is not None and change_temp is not None:
                    cursor.execute(
                        """UPDATE Transactions SET txid = ?, fee = ?, status = ?, created_at = ?,
                         change_address = ? WHERE id = ?""",
                        (
                            self._crypto.encrypt(
                                txid_temp.encode(), self._crypto.derive_encryption_key()
                            ),
                            self._crypto.encrypt(
                                transaction.get_fee().to_btc().encode(),
                                self._crypto.derive_encryption_key(),
                            ),
                            transaction.get_status().value,
                            transaction.get_created_at().timestamp(),
                            change_temp.get_id(),
                            transaction.get_id(),
                        ),
                    )

                    # Get all saved to_addresses of Transaction
                    cursor.execute(
                        "SELECT id, address, amount FROM Target_Addresses WHERE trans_id = ?",
                        (transaction.get_id(),),
                    )
                    # Used to find out which to_addresses are new and old
                    targets_in_database = set()

                    for row in cursor.fetchall():
                        try:
                            location = transaction.get_to_address().index(row[1])
                            if transaction.get_amount()[location].to_btc() != row[2]:
                                cursor.execute(
                                    "UPDATE Target_Addresses SET amount = ? WHERE id = ?",
                                    (
                                        transaction.get_amount()[location].to_btc(),
                                        row[0],
                                    ),
                                )
                                self._conn.commit()
                            targets_in_database.add(transaction.get_to_address()[location])
                        except ValueError:
                            cursor.execute(
                                "DELETE FROM Target_Addresses WHERE id = ?",
                                (row[0],),
                            )
                            self._conn.commit()

                    for to_address in set(transaction.get_to_address()) - targets_in_database:
                        cursor.execute(
                            """INSERT INTO Target_Addresses (trans_id, address, amount)
                             VALUES (?, ?, ?)""",
                            (
                                transaction.get_id(),
                                self._crypto.encrypt(
                                    to_address.encode(), self._crypto.derive_encryption_key()
                                ),
                                self._crypto.encrypt(
                                    transaction.get_amount()[
                                        transaction.get_to_address().index(to_address)
                                    ]
                                    .to_btc()
                                    .encode(),
                                    self._crypto.derive_encryption_key(),
                                ),
                            ),
                        )
                        self._conn.commit()

        cursor.close()

    # Save all Addresses of Wallet
    def save_addresses(self, wallet: Wallet) -> None:

        cursor = self._conn.cursor()

        for address in wallet.get_addresses():
            # Look if Address is new
            if address.get_id() is None:
                cursor.execute(
                    """INSERT INTO Address (address, prkey, balance, updated_at, refund_address,
                     wallet) VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        self._crypto.encrypt(
                            address.get_address().encode(), self._crypto.derive_encryption_key()
                        ),
                        self._crypto.encrypt(
                            address.get_prkey().encode(), self._crypto.derive_encryption_key()
                        ),
                        self._crypto.encrypt(
                            address.get_balance().to_btc().encode(),
                            self._crypto.derive_encryption_key(),
                        ),
                        address.get_updated_at().timestamp(),
                        int(address.is_refund_address()),
                        wallet.get_id(),
                    ),
                )
                self._conn.commit()
                cursor.execute("SELECT id FROM Address ORDER BY id DESC LIMIT 1")
                address.set_id(cursor.fetchall()[0][0])

            else:
                cursor.execute(
                    """UPDATE Address SET address = ?, prkey = ?, balance = ?,
                     updated_at = ?, refund_address = ?, wallet = ? WHERE id = ?""",
                    (
                        self._crypto.encrypt(
                            address.get_address().encode(), self._crypto.derive_encryption_key()
                        ),
                        self._crypto.encrypt(
                            address.get_prkey().encode(), self._crypto.derive_encryption_key()
                        ),
                        self._crypto.encrypt(
                            address.get_balance().to_btc().encode(),
                            self._crypto.derive_encryption_key(),
                        ),
                        address.get_updated_at().timestamp(),
                        int(address.is_refund_address()),
                        wallet.get_id(),
                        address.get_id(),
                    ),
                )
                self._conn.commit()

        # needed to be shure that all addresses has an id
        for address in wallet.get_addresses():
            self.save_transaction(address)

        cursor.close()

    # Save alle Wallets of User
    def save_wallet(self, user: User) -> None:

        cursor = self._conn.cursor()

        for wallet in user.get_wallets():
            # Look if Wallet is New
            if wallet.get_id() is None:
                cursor.execute(
                    """INSERT INTO Wallet (name, network, prkey, xpub, add_num, user)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        self._crypto.encrypt(
                            wallet.get_name().encode(), self._crypto.derive_encryption_key()
                        ),
                        wallet.get_network().value,
                        self._crypto.encrypt(
                            wallet.get_prkey().encode(), self._crypto.derive_encryption_key()
                        ),
                        self._crypto.encrypt(
                            wallet.get_xpub().encode(), self._crypto.derive_encryption_key()
                        ),
                        wallet.get_index(),
                        user.get_id(),
                    ),
                )
                self._conn.commit()
                cursor.execute("SELECT id FROM Wallet ORDER BY id DESC LIMIT 1")
                wallet.set_id(cursor.fetchall()[0][0])
                self.save_addresses(wallet)

            else:
                cursor.execute(
                    """UPDATE Wallet SET name = ?, network = ?, prkey = ?,
                     xpub = ?, user = ? WHERE id = ?""",
                    (
                        self._crypto.encrypt(
                            wallet.get_name().encode(), self._crypto.derive_encryption_key()
                        ),
                        wallet.get_network().value,
                        self._crypto.encrypt(
                            wallet.get_prkey().encode(), self._crypto.derive_encryption_key()
                        ),
                        self._crypto.encrypt(
                            wallet.get_xpub().encode(), self._crypto.derive_encryption_key()
                        ),
                        user.get_id(),
                        wallet.get_id(),
                    ),
                )
                self._conn.commit()
                self.save_addresses(wallet)

        cursor.close()

    # Save User
    def save_user(self, user: User) -> None:

        cursor = self._conn.cursor()

        # Look if User is new
        if user.get_id() is None:
            cursor.execute(
                "INSERT INTO User (username, password_hash, salt) VALUES (?, ?, ?)",
                (
                    user.get_username(),
                    user.get_password_hash(),
                    user.get_salt(),
                ),
            )
            self._conn.commit()
            cursor.execute("SELECT id FROM User ORDER BY id DESC LIMIT 1")
            user.set_id(cursor.fetchall()[0][0])
            self.save_wallet(user)

        else:
            cursor.execute(
                "UPDATE User SET username = ?, password_hash = ?, salt = ? WHERE id = ?",
                (
                    user.get_username(),
                    user.get_password_hash(),
                    user.get_salt(),
                    user.get_id(),
                ),
            )
            self._conn.commit()
            self.save_wallet(user)
