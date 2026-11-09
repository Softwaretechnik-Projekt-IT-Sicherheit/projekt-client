"""Prozess-Einstieg und Composition Root (Konsole, `python -m wallet`, Exe).

Nicht zu verwechseln mit `wallet.presentation.cli.CLI` – dieses Modul baut die
Objekte nur zusammen und reicht konkrete Befehle an die Presentation-Schicht weiter.
"""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from platformdirs import user_data_dir

from wallet.application import AuthService, TransactionValidator, WalletService
from wallet.domain import Network
from wallet.infrastructure import BlockchainClient, CryptoService, Database, KeyManager
from wallet.presentation import CLI, Locale


def _version() -> str:
    try:
        return version("wallet")
    except PackageNotFoundError:  # z. B. in einer Exe ohne mitkopierte Metadaten
        return "unbekannt"


def build_app(network: Network = Network.TESTNET) -> CLI:
    """Composition Root: erzeugt alle Objekte einmalig und verbindet sie miteinander."""
    data_dir = Path(user_data_dir("wallet", appauthor=False))
    data_dir.mkdir(parents=True, exist_ok=True)

    # Infrastructure
    crypto = CryptoService()
    db = Database(str(data_dir / "wallet.db"), crypto)
    keys = KeyManager()
    chain = BlockchainClient(network)

    # Application
    validator = TransactionValidator()
    auth = AuthService(db, crypto)
    wallets = WalletService(db, keys, chain, validator)

    # Presentation
    return CLI(Locale(), auth, wallets)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wallet", description="Bitcoin Hot Wallet")
    parser.add_argument("--version", action="version", version=f"%(prog)s {_version()}")
    _, rest = parser.parse_known_args(argv)

    # Ohne Befehl nur Hilfe zeigen – Services werden erst für einen konkreten Befehl verdrahtet
    if not rest:
        parser.print_help()
        return 0

    cli = build_app()
    return cli.main(rest)
