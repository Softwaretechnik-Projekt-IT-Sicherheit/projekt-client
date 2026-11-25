from __future__ import annotations

import os
import re
from datetime import datetime

import pytest

from wallet.domain.address import Address
from wallet.domain.amount import Amount
from wallet.domain.enums import Network, TxStatus
from wallet.domain.transaction import Transaction
from wallet.domain.user import User
from wallet.domain.wallet import Wallet
from wallet.infrastructure.crypto_service import CryptoService
from wallet.infrastructure.database import Database


@pytest.fixture
def create_database() -> Database:
    crys = CryptoService()
    crys.set_masterkey("Ich bin dumm", crys.generate_salt())
    db = Database(":memory:", crys)

    cursor = db._conn.cursor()
    # create Databasestructor in memory
    files = []
    for i in os.scandir(f"{os.path.dirname(os.path.realpath(__file__))}/../databaseconf"):
        files.append(i.name)
    files = sorted(files, key=lambda w: int(re.findall(r"\d+", w)[0]))
    for file in files:
        with open(
            f"{os.path.dirname(os.path.realpath(__file__))}/../databaseconf/{file}"
        ) as sql_file:
            sql_script = sql_file.read()
            cursor.executescript(sql_script)
            db._conn.commit()

    return db


def test_saving_and_loading(create_database):
    db = create_database

    user = User(
        "test",
        "cced28c6dc3f99c2396a5eaad732bf6b28142335892b1cd0e6af6cdb53f5ccfa",
        "abcdefghijklmnop",
    )

    w1 = Wallet(
        "Wallet 1",
        Network.TESTNET,
        "024a04740cd7a449c8aec3c8f44ae9919451774c56ee53e3573b742dfd2deb5b6d",
        "cQky5U1euiNUcdjTrtFNzrnvSU8dVLikAYx4UhzCTdhx2VemVGFK",
    )

    w2 = Wallet(
        "Wallet 2",
        Network.MAINNET,
        "0259823c2b52595267b4fad4587e747ededa623fe9fd27a5c0a06bbd0a261d5230",
        "18wfie9udF5cjtoSwevaBq1wjXnbffDPrP",
    )

    user.add_wallet(w1)
    user.add_wallet(w2)

    a1 = Address(
        "1JNu6ZfjSUaGNC3STDE65Qi5KbTfrAwZnq",
        Amount.from_str("0,1"),
        datetime.strptime("2024-06-15 10:30:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        "KzednhSr14eYguFdE4gqEpiPm5s8KcP4zpAFhjcpopB1PwmPtc4P",
        False,
    )

    a2 = Address(
        "1PCXzsvUmfBG2gbwfmAUUyb4ioCpR4DBAw",
        Amount.from_str("0,010"),
        datetime.strptime("2025-06-15 10:30:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        "L5Fezj241uUwueSaMRAuQkEvvTGHLSganStwJ3YQUkYCTKLvgHmT",
        False,
    )

    a3 = Address(
        "1LGQawfD6MSNLczHXsRurrg293dYTbGNQB",
        Amount.from_str("0,004"),
        datetime.strptime("2024-06-15 12:30:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        "KxNb5M3gfzNa31qK1SuekvbwTNdYxjdWxThvktTCkiUdkfp8dNLA",
        True,
    )

    a4 = Address(
        "1NWwAoJL6iFHHjuKWG1gYiipMDcAsErXfL",
        Amount.from_str("0,001"),
        datetime.strptime("2024-06-15 12:32:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        "KzjGe1UxYbm9QHfjDUetoxXGbviutxZJRWQssAAztfn9sLXMXhtN",
        True,
    )

    a5 = Address(
        "1EVKSBgNVq1do2w29z5kzA3qQE8QG2poYB",
        Amount.from_str("0,002"),
        datetime.strptime("2024-09-15 10:30:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        "KzoiY64uovMggNP5EHyuBT9nMPfm5F76XguUKQVy7k2LWmD8uDXx",
        True,
    )

    a6 = Address(
        "1EuQPtszhgTX4dPxKMxpCXcfnMNxuFEaHQ",
        Amount.from_str("0,003"),
        datetime.strptime("2020-06-15 10:30:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        "L4xZPuoXLTHWtwpyk84Ro6UraBejoRDhFu3nL7s4MLoTBDbMyTGV",
        True,
    )

    w1.add_address(a1)
    w1.add_address(a3)
    w1.add_address(a5)
    w2.add_address(a2)
    w2.add_address(a4)
    w2.add_address(a6)

    t1 = Transaction(
        Amount.from_str("0,001"),
        TxStatus.CONFIRMED,
        datetime.strptime("2019-06-15 10:30:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        a3,
        "bla",
    )

    a1.add_transaction(t1)
    t1.add_to_address("1AUXNskqF3n3xmWNNQTLxa3WGDgXCekipg", Amount.from_str("0,10"))

    t2 = Transaction(
        Amount.from_str("0,002"),
        TxStatus.BROADCAST,
        datetime.strptime("2018-06-15 10:30:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        a5,
        "foo",
    )

    a1.add_transaction(t2)
    a3.add_transaction(t2)
    t2.add_to_address("189ucFbJhXth3r3hQyQ2heH5NxeN5qbtvH", Amount.from_str("0,12"))

    t3 = Transaction(
        Amount.from_str("0,003"),
        TxStatus.BROADCAST,
        datetime.strptime("2017-06-15 10:30:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        a4,
        "bar",
    )

    a2.add_transaction(t3)
    t3.add_to_address("18o4qdkMHFrN5Z7Nq5BRkUqo7oWkHWSAUP", Amount.from_str("0,20"))
    t3.add_to_address("1258Gyo9qUWdC3MP4sjxiTFWttPuqZmwm9", Amount.from_str("0,22"))

    t4 = Transaction(
        Amount.from_str("0,004"),
        TxStatus.DRAFT,
        datetime.strptime("2016-06-15 10:30:00", "%Y-%m-%d %H:%M:%S").astimezone(),
        a6,
        "bib",
    )

    a4.add_transaction(t4)
    t4.add_to_address("1612hpcx7xuBry5o3ydrC7P4Dccv1jM4hH", Amount.from_str("0,15"))

    for i in range(2):  # Two Times, because once without and once with id set
        db.save_user(user)
        assert user.get_id() == 1
        assert w1.get_id() is not None
        assert w2.get_id() is not None
        assert w1.get_id() != w2.get_id()

        # Look that no Address have the same id
        addresses = [a1, a2, a3, a4, a5, a6]

        for i in addresses:
            assert i.get_id() is not None

        for i in addresses:
            for j in addresses:
                if i == j:
                    continue
                assert i.get_id() != j.get_id()

        trans = [t1, t2, t3, t4]
        for i in trans:
            assert i is not None

        for i in trans:
            for j in trans:
                if i == j:
                    continue
                assert i.get_id() != j.get_id()
        # load Objects from Database

        luser = db.get_user("test")
        assert luser is not None
        assert luser._id == user._id
        assert luser._username == user._username
        assert luser._password_hash == user._password_hash
        assert luser._salt == user._salt

        db.load_wallets(luser)
        assert len(luser.get_wallets()) == 2
        assert luser.get_wallet("Wallet 1") is not None
        assert luser.get_wallet("Wallet 2") is not None
        lw1 = luser.get_wallet("Wallet 1")
        lw2 = luser.get_wallet("Wallet 2")
        for i in user.get_wallets():
            for j in luser.get_wallets():
                if i.get_id() == j.get_id():
                    assert i._name == j._name
                    assert i._network == j._network
                    assert i._xpub == j._xpub
                    assert i._prkey == j._prkey
                    assert i._index == j._index

        for lw, wa in zip([lw1, lw2], [w1, w2], strict=True):
            db.load_addresses_transactions(lw)

            for i in lw.get_addresses():
                assert (
                    i.get_id() == wa.get_addresses()[0].get_id()
                    or i.get_id() == wa.get_addresses()[1].get_id()
                    or i.get_id() == wa.get_addresses()[2].get_id()
                )

            for i in wa.get_addresses():
                for j in lw.get_addresses():
                    if i.get_id() == j.get_id():
                        assert i._address == j._address
                        assert i._prkey == j._prkey
                        assert i._balance.to_btc() == j._balance.to_btc()
                        assert i._updated_at == j._updated_at
                        assert i._refund_address == j._refund_address

                        # Counter to proov that alle transactions mathes
                        counter = 0
                        for first_transaction in i.get_transactions():
                            for second_transaction in j.get_transactions():
                                if first_transaction.get_id() == second_transaction.get_id():
                                    counter += 1
                                    assert first_transaction._txid == second_transaction._txid
                                    assert set(first_transaction._to_address) == set(
                                        second_transaction._to_address
                                    )

                                    for m in first_transaction.get_to_address():
                                        assert (
                                            first_transaction._amount[
                                                first_transaction._to_address.index(m)
                                            ].to_btc()
                                            == second_transaction._amount[
                                                second_transaction._to_address.index(m)
                                            ].to_btc()
                                        )
                                    assert (
                                        first_transaction._fee.to_btc()
                                        == second_transaction._fee.to_btc()
                                    )
                                    if first_transaction._change_address is None:
                                        assert second_transaction._change_address is None
                                    else:
                                        assert (
                                            first_transaction._change_address.get_id()
                                            == second_transaction._change_address.get_id()
                                        )
                                    assert second_transaction._status == first_transaction._status
                                    assert (
                                        second_transaction._created_at
                                        == first_transaction._created_at
                                    )

    del db
