from __future__ import annotations

import sqlite3

from wallet.infrastructure.crypto_service import CryptoService
from wallet.domain.user import User
from wallet.domain.wallet import Wallet
from wallet.domain.enums import Network
from wallet.domain.address import Address
from wallet.domain.transaction import Transaction


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

    # Load all Addresses and Transactions for a Wallet
    def load_addresses_transactions(self, wallet: Wallet) -> None:
        cursor = self._conn.cursor()
        id_to_address = dict() # Used for connecting Transactions with Address
        id_to_transaction dict() # Used for adding to_addresses to Transactions

        if wallet.get_id() == None:
            return

        # Get all Adresses of Wallet
        cursor.execute("SELECT id, address, prkey, balance, updated_at, refund_address FROM Address WHERE wallet = ?", (wallet.get_id(), ))

        for row in cursor:
            address = Address(row[1], Amount.from_int(int(row[3])), datetime.utcfromtimestamp(int(row[4])), self._crypto.decrypt(row[2]), bool(int(row[5])), int(row[0]))
            wallet.append(address)

        # Get all Transactions for all Addresses in Wallet
        cursor.execute("SELECT t.id, t.txid, t.amount, t.fee, t.status, t.created_at, at.add_id, t.change_address FROM Transactions t INNER JOIN Address_Transaction at ON at.trans_id = t.id WHERE at.add_id IN (SELECT id FROM Address WHERE wallet = ?)", (wallet.get_id(), ))
        
        for row in cursor:
            transaction = Transaction(Amount.from_int(int(row[2])), Amount.from_int(int(row[3])), TxStatus(row[4]), datetime.utcfromtimestamp(int(row[5])), id_to_address[int(row[9])], txid = None if row[1] == None else self._crypto.decrypt(row[1]), id = row[0])
            id_to_address[int(row[7])].add_transaction(transaction)
            id_to_transaction[transaction.get_id()] = transaction

        # Get all to_address
        cursor.execute("SELECT trans_id, address, amount FROM Target_Addresses WHERE trans_id IN ("+ ", ".join(list(id_to_transaction.keys())) +")")

        for row in cursor:
            id_to_transaction[int(row[0])].add_to_address(row[1], Amount.from_int(int(row[2])))

        cursor.close()

    # Safing all Transactions of an Address
    def safe_transaction(self, address: Address) -> None:

        cursor = self._conn.cursor()

        for transaction in address.get_transactions():

            # Look if Transaction is already in Database
            if transaction.get_id() == None:
                
                # Add Transaction
                cursor.execute("INSERT INTO Transactions (txid, fee, status, created_at, change_address) VALUES (?, ?, ?, ?, ?)", (self._crypto.encrypt(transaction.get_txid()), transaction.get_fee().to_sats(), transaction.get_status(), transaction.get_created_at().timestamp(), transaction.get_change_address().get_id(), ))
                self._conn.commit()
                cursor.execute("SELECT id FROM Transactions ORDER BY id DESC LIMIT 1")
                id = cursor.fetchall[0][0]
                transaction.set_id(id)

                # Add connection between Address and Transaction
                cursor.execute("INSERT INTO Address_Transaction (add_id, trans_id) VALUES (?, ?)", (address.get_id(), id, ))


                
                # Add all to_addresses
                for to_address, amount in zip(transaction.get_to_address(), transaction.get_amount):
                    cursor.execute("INSET INTO Target_Addresses (address, amount, trans_id) VALUES (?, ?)", (to_address, amount.to_sats(), id))
                self._conn.commit()
            
            #Transaction already in Database
            else:
                # Safe direct Changes
                cursor.execute("UPDATE Transactions SET txid = ?, fee = ?, status = ?, created_ad = ?, change_address = ? WHERE id = ?", (self._crypto.encrypt(transaction.get_txid()), transaction.get_fee().to_sats(), transaction.get_status(), transaction.get_created_at().timestamp(), transaction.get_change_address().get_id(), transaction.get_id(), ))
                
                # Get all saved to_addresses of Transaction
                cursor.execute("SELECT id, address, amount FROM Target_Addresses WHERE trans_id = ?", (transaction.get_id(), ))
                targets_in_database = set() # Used to find out which to_addresses are new and need to be saved to the database

                for row in cursor.fetchall():
                    try:
                        location = transaction.get_to_address().index(row[1])
                        if transaction.get_amount()[location].to_sats() != int(row[2]): # Value of Address have changed
                            cursor.execute("UPDATE Target_Addresses SET amount = ? WHERE id = ?", (transaction.get_amount[location].to_sats(), row[0], ))
                            self._conn.commit()
                        targets_in_database.add(transaction.get_to_address()[location])
                    except ValueError:
                        cursor.excecute("DELETE FROM Target_Addresses WHERE id = ?", (row[0], ))
                        self._conn.commit()
                
                for to_address in transaction.get_to_address() - targets_in_database:
                    cursor.execute("INSERT INTO Target_Addresses (trans_id, address, amount) VALUES (?, ?, ?)", (transaction.get_id(), to_address, transaction.get_amount()[transaction.get_address().index(to_address)].to_sats()))
                    self._conn.commit()

        cursor.close()

    # Safe all Addresses of Wallet
    def safe_addresses(self, wallet: Wallet) -> None:
        
        cursor = self._conn.cursor()

        for address in wallet.get_addresses():
            # Look if Address is new
            if address.get_id() == None:
                cursor.execute("INSERT INTO Address (address, prkey, balance, updated_at, refund_address, wallet) VALUES (?, ?, ?, ?, ?, ?)", (address.get_address(), self._crypto.encrypt(address.get_prkey()), transaction.get_balance().to_sats(), address.get_updated_at().timestamp(), int(address.is_refund_address()), wallet.get_id(), ))
                self._conn.commit()
                cursor.execute("SELECT id FROM Address ORDER BY id DESC LIMIT 1")
                address.set_id(cursor.fetchall()[0][0])
                self.safe_transaction(address)

            else:
                cursor.execute("UPDATE Address SET address = ?, prkey = ?, balance = ?, updated_at = ?, refund_address = ?, wallet = ? WHERE id = ?", (address.get_address(), self._crypto.encrypt(address.get_prkey), address.get_balance().to_sats(), address.get_updated_at().timestamp(), int(addres.is_refund_address()), wallet.get_id(), address.get_id(), ))
                self._conn.commit()
                self.safe_transaction(address)

        cursor.close()

    # Safe alle Wallets of User
    def safe_wallet(self, user: User) -> None:

        cursor = self._conn.cursor()

        for wallet in user.get_wallets():

            # Look if Wallet is New
            if wallet.get_id() == None:
                cursor.execute("INSERT INTO Wallet (name, network, prkey, xpub, user) VALUES (?, ?, ?, ?, ?)", (wallet.get_name(), wallet.get_network(), self._crypto.encrypt(wallet.get_prkey()), wallet.get_xpub(), user.get_id()))
                self._conn.commit()
                cursor.execute("SELECT id FROM Wallet ORDER BY DESC LIMIT 1")
                wallet.set_id(cursor.fetchall()[0][0])
                self.safe_addresses(wallet)

            else:
                cursor.execute("UPDATE Wallet SET name = ?, network = ?, prkey = ?, xpub = ?, user = ? WHERE id = ?", (wallet.get_name(), wallet.get_network(), self._crypto.encrypt(wallet.get_prkey()), wallet.get_xpub, user.get_id(), wallet.get_id()))
                self._conn.commit()
                self.safe_addresses(wallet)

        cursor.close()

    # Safe User
    def safe_user(self, user: User) -> None:

        cursor = self._conn.cursor()

        # Look if User is new
        if user.get_id() == None:
            cursor.execute("INSERT INTO User (username, password, salt) VALUES (?, ?, ?)", (user.get_name(), user.get_password_hash().encode(), user.get_salt().encode(), ))
            self._conn.commit()
            cursor.execute("SELECT id FROM User ORDER BY id DESC LIMIT 1")
            user.set_id(cursor.fetchall()[0][0])
            self.safe_wallet(user)

        else:
            cursor.execute("UPDATE User SET username = ?, password = ?, salt = ? WHERE id = ?", (user.get_name(), user.get_password_hash().encode(), user.get_salt().encode(), user.get_id(), ))
            self._conn.commit()
            self.safe_wallet(user)
        
