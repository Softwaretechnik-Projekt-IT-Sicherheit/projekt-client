from __future__ import annotations

from wallet.application import AuthService, Session, WalletService
from wallet.presentation.Locale import Locale


class CLI:

    def __init__(self, locator: Locale, auth: AuthService, wallets: WalletService) -> None:
        self._locator: Locale = locator
        self._auth: AuthService = auth
        self._wallets: WalletService = wallets
        self._session: Session | None = None

    def main(self, argv: list[str]) -> int:
        raise NotImplementedError

    def register(self, username: str) -> None:
        raise NotImplementedError

    def login(self, username: str) -> None:
        raise NotImplementedError

    def create_wallet(self, name: str, words: int = 12) -> None:
        raise NotImplementedError

    def restore_wallet(self, name: str) -> None:
        raise NotImplementedError

    def show_address(self, name: str, new: bool = False) -> None:
        raise NotImplementedError

    def show_balance(self, name: str) -> None:
        raise NotImplementedError

    def show_transactions(self, transaction: str) -> None:
        raise NotImplementedError

    def create_transactions(self) -> None:
        raise NotImplementedError

    def send(self, name: str, to: str, amount: str) -> None:
        raise NotImplementedError

    def _confirm(self, prompt: str) -> bool:
        raise NotImplementedError

    def _ask_password(self) -> str:
        raise NotImplementedError
