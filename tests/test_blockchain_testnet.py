"""Integrationstests gegen das echte testnet4 (T0010).

Laufen nicht standardmäßig, nur mit: npm run test:testnet (bzw. uv run pytest -m testnet)
"""

from __future__ import annotations

import pytest
from bitcoinlib.keys import HDKey

from wallet.domain import Amount, Network
from wallet.infrastructure import BlockchainClient

pytestmark = pytest.mark.testnet

# Empfänger der Coinbase-Transaktion in testnet4-Block 1000, hat also garantiert Historie
USED_ADDRESS = "tb1q548z58kqvwyjqwy8vc2ntmg33d7s2wyfv7ukq4"


@pytest.fixture(scope="module")
def client() -> BlockchainClient:
    return BlockchainClient(Network.TESTNET)


@pytest.fixture(scope="module")
def fresh_address() -> str:
    address: str = HDKey(network="testnet4", witness_type="segwit").address()
    return address


# Prüft, dass eine bekannte genutzte Adresse Historie hat
def test_used_address_has_history(client: BlockchainClient) -> None:
    assert client.has_history(USED_ADDRESS) is True


# Prüft, dass eine frisch erzeugte Adresse keine Historie und Saldo 0 hat
def test_fresh_address_is_unused(client: BlockchainClient, fresh_address: str) -> None:
    assert client.has_history(fresh_address) is False
    assert client.get_balances([fresh_address]) == {fresh_address: Amount(0)}
    assert client.get_utxos([fresh_address]) == []


# Prüft, dass gebündelte Saldenabfragen für mehrere Adressen Amounts liefern
def test_get_balances_bundled(client: BlockchainClient, fresh_address: str) -> None:
    balances = client.get_balances([USED_ADDRESS, fresh_address])
    assert set(balances) == {USED_ADDRESS, fresh_address}
    assert all(isinstance(value, Amount) for value in balances.values())
