from __future__ import annotations

from wallet.domain import Network, Transaction, Wallet


class KeyManager:
    def generate_mnemonic(self, words: int = 12) -> str:
        raise NotImplementedError

    def validate_mnemonic(self, mnemonic: str) -> bool:
        raise NotImplementedError

    def derive_xpub(self, mnemonic: str, network: Network) -> str:
        raise NotImplementedError

    def derive_address(self, xpub: str, chain: int, index: int) -> str:
        raise NotImplementedError

    def sign(self, tx: Transaction, mnemonic: str, wallet: Wallet) -> str:
        raise NotImplementedError
