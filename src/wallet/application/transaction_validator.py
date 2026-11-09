from wallet.domain.amount import Amount
from wallet.domain.enums import Network
from wallet.domain.wallet import Wallet


class TransactionValidator:
    def validate_address(self, address: str, network: Network) -> None:
        raise NotImplementedError

    def validate_funds(self, wallet: Wallet, amount: Amount, fee: Amount) -> None:
        raise NotImplementedError
