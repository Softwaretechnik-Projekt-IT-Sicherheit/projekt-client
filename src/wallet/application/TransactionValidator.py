from wallet.domain.Amount import Amount
from wallet.domain.Type import Network
from wallet.domain.Wallet import Wallet


class TransactionValidator:

    def validate_address(self, address: str, network: Network) -> None:
        raise NotImplementedError

    def validate_funds(self, wallet: Wallet, amount: Amount, fee: Amount) -> None:
        raise NotImplementedError
