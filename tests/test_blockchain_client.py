"""Unit-Tests für den BlockchainClient (T0010) mit gemocktem bitcoinlib-Service."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests
from bitcoinlib.services.services import ServiceError

from wallet.domain import Amount, Network, Utxo
from wallet.infrastructure import BlockchainClient, NetworkUnavailableError, blockchain_client

ADDR_A = "tb1qaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
ADDR_B = "tb1qbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
ADDR_EMPTY = "tb1qcccccccccccccccccccccccccccccccccccccc"


def raw_utxo(address: str, txid: str, output_n: int, value: int, conf: int = 3) -> dict[str, Any]:
    return {
        "address": address,
        "txid": txid,
        "output_n": output_n,
        "value": value,
        "confirmations": conf,
    }


UTXOS: dict[str, list[dict[str, Any]]] = {
    ADDR_A: [raw_utxo(ADDR_A, "aa" * 32, 0, 50_000), raw_utxo(ADDR_A, "ab" * 32, 1, 25_000, 0)],
    ADDR_B: [raw_utxo(ADDR_B, "bb" * 32, 2, 1_000)],
    ADDR_EMPTY: [],
}


@pytest.fixture
def service() -> MagicMock:
    mock = MagicMock()
    mock.getutxos.side_effect = lambda address: UTXOS[address]
    return mock


@pytest.fixture
def client(service: MagicMock) -> BlockchainClient:
    return BlockchainClient(Network.TESTNET, service_factory=lambda: service)


# Prüft, dass beim Erzeugen des Clients noch kein Netzwerkzugriff passiert
# (die Anwendung muss auch offline starten können)
def test_constructor_does_not_touch_network() -> None:
    factory = MagicMock()
    BlockchainClient(Network.TESTNET, service_factory=factory)
    factory.assert_not_called()


# Prüft, dass der Service nur einmal erzeugt und danach wiederverwendet wird
def test_service_is_created_lazily_once(service: MagicMock) -> None:
    factory = MagicMock(return_value=service)
    client = BlockchainClient(Network.TESTNET, service_factory=factory)
    client.get_balances([ADDR_A])
    client.get_balances([ADDR_B])
    factory.assert_called_once()


# Prüft, dass Salden als Amount in Satoshi geliefert und UTXOs je Adresse summiert werden
def test_get_balances_returns_amounts_in_sats(client: BlockchainClient) -> None:
    balances = client.get_balances([ADDR_A, ADDR_B, ADDR_EMPTY])
    assert balances == {
        ADDR_A: Amount(75_000),
        ADDR_B: Amount(1_000),
        ADDR_EMPTY: Amount(0),
    }
    assert all(isinstance(value, Amount) for value in balances.values())


# Prüft, dass eine leere Adressliste ohne Netzwerkzugriff ein leeres dict liefert
def test_get_balances_empty_list() -> None:
    factory = MagicMock()
    assert BlockchainClient(Network.TESTNET, service_factory=factory).get_balances([]) == {}
    factory.assert_not_called()


# Prüft die Abbildung der bitcoinlib-Dicts auf Utxo-Objekte
def test_get_utxos_maps_to_domain(client: BlockchainClient) -> None:
    utxos = client.get_utxos([ADDR_B])
    assert utxos == [
        Utxo(txid="bb" * 32, output_n=2, address=ADDR_B, value=Amount(1_000), confirmations=3)
    ]


# Prüft, dass doppelte Adressen nur einmal abgefragt werden
def test_get_utxos_deduplicates_addresses(client: BlockchainClient, service: MagicMock) -> None:
    utxos = client.get_utxos([ADDR_A, ADDR_A, ADDR_B])
    assert len(utxos) == 3
    assert service.getutxos.call_count == 2


# Prüft has_history für genutzte und ungenutzte Adressen
@pytest.mark.parametrize(("txs", "expected"), [([object()], True), ([], False)])
def test_has_history(
    client: BlockchainClient, service: MagicMock, txs: list[object], expected: bool
) -> None:
    service.gettransactions.return_value = txs
    assert client.has_history(ADDR_A) is expected
    service.gettransactions.assert_called_once_with(ADDR_A, limit=1)


NETWORK_ERRORS = [
    ServiceError("No successful response from any serviceprovider"),
    requests.ConnectionError("offline"),
    requests.Timeout("timeout"),
    OSError("network unreachable"),
]


# Prüft, dass Netzwerkfehler bei Abfragen als NetworkUnavailableError ankommen
@pytest.mark.parametrize("error", NETWORK_ERRORS)
def test_query_errors_map_to_network_unavailable(
    client: BlockchainClient, service: MagicMock, error: Exception
) -> None:
    service.getutxos.side_effect = error
    service.gettransactions.side_effect = error
    with pytest.raises(NetworkUnavailableError) as excinfo:
        client.get_balances([ADDR_A])
    assert excinfo.value.__cause__ is error
    with pytest.raises(NetworkUnavailableError):
        client.get_utxos([ADDR_A])
    with pytest.raises(NetworkUnavailableError):
        client.has_history(ADDR_A)


# Prüft, dass ein Fehler beim Erzeugen des Service (offline) definiert gemeldet
# und beim nächsten Aufruf erneut versucht wird
def test_offline_at_service_creation_then_recovers(service: MagicMock) -> None:
    factory = MagicMock(side_effect=[ServiceError("offline"), service])
    client = BlockchainClient(Network.TESTNET, service_factory=factory)
    with pytest.raises(NetworkUnavailableError):
        client.get_balances([ADDR_A])
    assert client.get_balances([ADDR_A]) == {ADDR_A: Amount(75_000)}
    assert factory.call_count == 2


# Prüft, dass der Standard-Service mit testnet4 und dem gesetzten Timeout erzeugt wird
def test_default_service_uses_testnet4_and_timeout() -> None:
    with patch.object(blockchain_client, "Service") as service_cls:
        service_cls.return_value.getutxos.return_value = []
        BlockchainClient(Network.TESTNET, timeout=7).get_balances([ADDR_A])
    service_cls.assert_called_once_with(
        network="testnet4", timeout=7, max_errors=blockchain_client.DEFAULT_MAX_ERRORS
    )
