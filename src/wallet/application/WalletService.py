from wallet.application.Session import Session
from wallet.application.TransactionValidator import TransactionValidator
from wallet.domain.Address import Address
from wallet.domain.Amount import Amount
from wallet.domain.Transaction import Transaction
from wallet.domain.Type import Network
from wallet.domain.Wallet import Wallet
from wallet.infrastructure.BlockchainClient import BlockchainClient
from wallet.infrastructure.Database import Database
from wallet.infrastructure.KeyManager import KeyManager


class WalletService:
    def __init__(
        self,
        db: Database,
        keys: KeyManager,
        chain: BlockchainClient,
        validator: TransactionValidator,
    ) -> None:
        self._db: Database = db
        self._keys: KeyManager = keys
        self._chain: BlockchainClient = chain
        self._validator: TransactionValidator = validator

    def create_wallet(
        self, session: Session, name: str, network: Network, words: int = 12
    ) -> tuple[Wallet, str]:
        raise NotImplementedError

    def restore_wallet(
        self, session: Session, name: str, mnemonic: str, network: Network
    ) -> Wallet:
        raise NotImplementedError

    def new_address(self, session: Session, wallet: Wallet, change: bool = False) -> Address:
        raise NotImplementedError

    def discover_addresses(
        self, session: Session, wallet: Wallet, gap_limit: int = 20
    ) -> list[Address]:
        raise NotImplementedError

    def get_balance(self, session: Session, wallet: Wallet) -> Amount:
        raise NotImplementedError

    def build_transaction(
        self, session: Session, wallet: Wallet, to: str, amount: Amount
    ) -> Transaction:
        raise NotImplementedError

    def broadcast(self, session: Session, wallet: Wallet, tx: Transaction) -> str:
        raise NotImplementedError
