from __future__ import annotations

import sys
from contextlib import ExitStack
from datetime import datetime
from unittest.mock import patch

import pytest

from wallet.domain.address import Address
from wallet.domain.amount import Amount
from wallet.domain.enums import Network, TxStatus
from wallet.domain.transaction import Transaction
from wallet.domain.user import User
from wallet.domain.wallet import Wallet


@pytest.fixture
def create_user() -> User:
    return User(
        "Name",
        "a20d638ea51815fb7c9617d758fc6c97d65b4da30ae0a3ea100f2ad005b19032",
        bytes(
            [
                0xFF,
                0xEE,
                0xDD,
                0xCC,
                0xBB,
                0xAA,
                0x99,
                0x88,
                0x77,
                0x66,
                0x55,
                0x44,
                0x33,
                0x22,
                0x11,
                0x00,
            ],
        ),
        None,
    )


@pytest.fixture
def create_wallet() -> Wallet:
    return Wallet(
        "Wallet 1",
        Network.TESTNET,
        "024a04740cd7a449c8aec3c8f44ae9919451774c56ee53e3573b742dfd2deb5b6d",
        "cQky5U1euiNUcdjTrtFNzrnvSU8dVLikAYx4UhzCTdhx2VemVGFK",
    )


@pytest.fixture
def create_address() -> Address:
    return Address(
        "bc1qfc26xzrm4s6grnsmdawk9efwe2j7f96za39h75",
        Amount.from_int(100),
        datetime.strptime("2024-06-15 10:30:00", "%Y-%m-%d %H:%M:%S"),
        "cQF9SNKk8RANH6tgJGsddDoy9DC5h4qUwh9wmo5NSjJbQu8H6ZMZ",
        False,
    )


@pytest.fixture
def create_transaction(create_address) -> Transaction:
    change = Address(
        "bc1qfc26xzrm4s6grnsmdawk9efwe2j7f96za39h75",
        Amount.from_int(5),
        datetime.strptime("2024-06-15 10:30:00", "%Y-%m-%d %H:%M:%S"),
        "cQF9SNKk8RANH6tgJGsddDoy9DC5h4qUwh9wmo5NSjJbQu8H6ZMZ",
        True,
    )
    return Transaction(
        Amount.from_int(1),
        TxStatus.DRAFT,
        datetime.strptime("2024-06-15 10:30:00", "%Y-%m-%d %H:%M:%S"),
        change,
        "bla bla bla",
    )


# Looks if all parameters are correctly saved after object creation
def test_user_creation(create_user) -> None:
    user = create_user

    assert user.get_username() == "Name"
    assert (
        user.get_password_hash()
        == "a20d638ea51815fb7c9617d758fc6c97d65b4da30ae0a3ea100f2ad005b19032"
    )
    assert user.get_salt() == bytes(
        [
            0xFF,
            0xEE,
            0xDD,
            0xCC,
            0xBB,
            0xAA,
            0x99,
            0x88,
            0x77,
            0x66,
            0x55,
            0x44,
            0x33,
            0x22,
            0x11,
            0x00,
        ],
    )
    assert user.get_id() is None
    assert user.get_wallet("Hallo") is None


# Looks if all setters work
def test_user_setters(create_user) -> None:
    user = create_user

    user.set_id(10)
    assert user.get_id() == 10

    user.set_username("Hallo")
    assert user.get_username() == "Hallo"

    user.set_password_hash("09ed2884cc4a60852a5cabd468b59ae45b624cc9c8a492491a5133c2a8ef0598")
    assert (
        user.get_password_hash()
        == "09ed2884cc4a60852a5cabd468b59ae45b624cc9c8a492491a5133c2a8ef0598"
    )


def test_wallet_creation(create_wallet) -> None:
    wallet = create_wallet

    assert wallet.get_id() is None
    assert wallet.get_name() == "Wallet 1"
    assert wallet.get_prkey() == "cQky5U1euiNUcdjTrtFNzrnvSU8dVLikAYx4UhzCTdhx2VemVGFK"
    assert wallet.get_xpub() == "024a04740cd7a449c8aec3c8f44ae9919451774c56ee53e3573b742dfd2deb5b6d"
    assert wallet.get_index() == 0
    assert wallet.get_network() == Network.TESTNET


def test_wallet_setter(create_wallet) -> None:
    wallet = create_wallet

    wallet.set_id(10)
    assert wallet.get_id() == 10

    wallet.set_name("Wallet 2")
    assert wallet.get_name() == "Wallet 2"


def test_wallet_methods(create_wallet) -> None:
    wallet = create_wallet

    assert wallet.next_index() == 1
    wallet.increment_index()
    assert wallet.next_index() == 2
    assert wallet.total_balance().to_sats() == 0


def test_user_add_wallet(create_user, create_wallet) -> None:
    user = create_user

    user.add_wallet(create_wallet)

    assert user.get_wallets() == [create_wallet]
    assert user.get_wallet("Wallet 1") == create_wallet

    wallet = Wallet("Wallet 2", Network.MAINNET, "test", "test", 3, 10)

    user.add_wallet(wallet)
    assert user.get_wallet("Wallet 2") == wallet
    assert user.get_wallets() == [create_wallet, wallet]


def test_address_creation(create_address) -> None:
    address = create_address

    assert address.get_id() is None
    assert address.get_updated_at() == datetime.strptime("2024-06-15 10:30:00", "%Y-%m-%d %H:%M:%S")
    assert address.get_address() == "bc1qfc26xzrm4s6grnsmdawk9efwe2j7f96za39h75"
    assert address.get_balance().to_sats() == 100
    assert address.get_prkey() == "cQF9SNKk8RANH6tgJGsddDoy9DC5h4qUwh9wmo5NSjJbQu8H6ZMZ"
    assert address.is_refund_address() is False


def test_address_setters(create_address) -> None:
    address = create_address

    address.set_id(10)
    assert address.get_id() == 10

    address.set_updated_at(datetime.strptime("2025-06-15 10:30:00", "%Y-%m-%d %H:%M:%S"))
    assert address.get_updated_at() == datetime.strptime("2025-06-15 10:30:00", "%Y-%m-%d %H:%M:%S")


def test_wallet_add_address(create_wallet, create_address):
    wallet = create_wallet

    wallet.add_address(create_address)
    assert wallet.get_addresses() == [create_address]

    assert wallet.total_balance().to_sats() == 100


def test_transaction_creation(create_transaction) -> None:
    trans = create_transaction

    assert trans.get_id() is None
    assert trans.get_txid() == "bla bla bla"
    assert trans.get_fee().to_sats() == 1
    assert trans.get_change_address().get_address() == "bc1qfc26xzrm4s6grnsmdawk9efwe2j7f96za39h75"
    assert trans.get_status() == TxStatus.DRAFT
    assert trans.get_created_at() == datetime.strptime("2024-06-15 10:30:00", "%Y-%m-%d %H:%M:%S")


def test_transaction_setter(create_transaction, create_address) -> None:
    trans = create_transaction

    trans.set_id(11)
    assert trans.get_id() == 11
    trans.set_txid("test")
    assert trans.get_txid() == "test"
    trans.set_fee(Amount.from_str("1000"))
    assert trans.get_fee().to_sats() == 1000
    trans.set_change_address(create_address)
    assert trans.get_change_address() == create_address
    trans.set_status(TxStatus.BROADCAST)
    assert trans.get_status() == TxStatus.BROADCAST

    trans.add_to_address("Addresse 1", Amount.from_int(10))
    trans.add_to_address("Addresse 2", Amount.from_int(11))

    assert trans.get_to_address() == ["Addresse 1", "Addresse 2"]
    assert trans.get_amount()[0].to_sats() == 10
    assert trans.get_amount()[1].to_sats() == 11


def test_address_add_transaction(create_address, create_transaction) -> None:
    address = create_address

    address.add_transaction(create_transaction)
    assert address.get_transactions() == [create_transaction]
