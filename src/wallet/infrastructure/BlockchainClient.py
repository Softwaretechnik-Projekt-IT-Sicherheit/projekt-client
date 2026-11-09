from __future__ import annotations

from wallet.domain import Amount, Network


class BlockchainClient:
    """PZ 040, PF 040, PF 100"""

    def __init__(self, network: Network) -> None:
        self._network: Network = network
        raise NotImplementedError

    def get_balances(self, addresses: list[str]) -> dict[str, Amount]:
        raise NotImplementedError

    def get_utxos(self, addresses: list[str]) -> list[dict]:
        raise NotImplementedError

    def broadcast(self, raw_hex: str) -> str:
        raise NotImplementedError
