from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any, Protocol

import requests
from bitcoinlib.services.services import Service, ServiceError

from wallet.domain import Amount, Network, Utxo
from wallet.infrastructure.blockchain_errors import NetworkUnavailableError

DEFAULT_TIMEOUT_S = 10
"""Timeout pro HTTP-Anfrage an einen Provider (Sekunden)."""

DEFAULT_MAX_ERRORS = 3
"""Anzahl fehlerhafter Provider, nach der eine Anfrage abgebrochen wird."""

# bitcoinlib loggt jeden ServiceError auf ERROR-Level; das würde die CLI überfluten
# Die Fehler kommen stattdessen als NetworkUnavailableError beim Aufrufer an
logging.getLogger("bitcoinlib.services.services").setLevel(logging.CRITICAL)


class ChainService(Protocol):
    # Schnittstellenbeschreibung damit die Typisierung weiß welche Response sie erhält
    # --> auch für tests mit MagicMock notwendig

    def getutxos(self, address: str) -> list[dict[str, Any]]: ...

    def gettransactions(self, address: str, *, limit: int) -> list[Any]: ...


@contextmanager
def _network_errors() -> Iterator[None]:
    """Bildet alle Netzwerk-/Provider-Fehler auf NetworkUnavailableError ab."""
    try:
        yield
    except (ServiceError, requests.RequestException, OSError) as e:
        raise NetworkUnavailableError(
            "Blockchain nicht erreichbar. Bitte Internetverbindung prüfen."
        ) from e


class BlockchainClient:

    def __init__(
        self,
        network: Network,
        *,
        timeout: int = DEFAULT_TIMEOUT_S,
        service_factory: Callable[[], ChainService] | None = None,
    ) -> None:
        self._network: Network = network
        self._timeout: int = timeout
        self._service_factory: Callable[[], ChainService] = service_factory or self._default_service
        self._service: ChainService | None = None

    def _default_service(self) -> ChainService:
        service: ChainService = Service(
            network=self._network.value,
            timeout=self._timeout,
            max_errors=DEFAULT_MAX_ERRORS,
        )
        return service

    def _get_service(self) -> ChainService:
        """Erzeugt den Service beim ersten Zugriff. Schlägt das fehl, wird es beim
        nächsten Aufruf erneut versucht."""
        if self._service is None:
            with _network_errors():
                self._service = self._service_factory()
        return self._service

    def get_utxos(self, addresses: list[str]) -> list[Utxo]:
        # Liefert alle UTXOs (bestätigt und unbestätigt) der übergebenen Adressen
        service = self._get_service()
        utxos: list[Utxo] = []
        with _network_errors():
            for address in dict.fromkeys(addresses):  # Duplikate entfernen, Reihenfolge halten
                for raw in service.getutxos(address):
                    utxos.append(
                        Utxo(
                            txid=str(raw["txid"]),
                            output_n=int(raw["output_n"]),
                            address=address,
                            value=Amount(int(raw["value"])),
                            confirmations=int(raw.get("confirmations") or 0),
                        )
                    )
        return utxos

    def get_balances(self, addresses: list[str]) -> dict[str, Amount]:
        """Liefert den Saldo je Adresse in Satoshi, gebündelt über eine UTXO-Abfrage.

        Der Saldo enthält bestätigte und unbestätigte Beträge. Jede angefragte Adresse
        ist im Ergebnis enthalten (Amount(0), wenn keine UTXOs vorhanden sind).
        """
        balances: dict[str, Amount] = {address: Amount(0) for address in addresses}
        if not balances:
            return balances
        for utxo in self.get_utxos(addresses):
            balances[utxo.address] = balances[utxo.address] + utxo.value
        return balances

    def has_history(self, address: str) -> bool:
        """True, wenn die Adresse mindestens eine Transaktion hat (auch bei Saldo 0).

        Wird für die Adresssuche (Gap Limit) benötigt, um genutzte Adressen zu erkennen.
        """
        service = self._get_service()
        with _network_errors():
            return len(service.gettransactions(address, limit=1)) > 0

    def broadcast(self, raw_hex: str) -> str:
        raise NotImplementedError
