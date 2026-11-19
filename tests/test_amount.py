from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Decimal
from typing import Any

import pytest

from wallet.domain.amount import (
    MAX_SATS,
    Amount,
)
from wallet.domain.amount_errors import AmountError, InvalidAmountError, NegativeAmountError


def test_error_hierarchy() -> None:
    assert issubclass(AmountError, ValueError)
    assert issubclass(InvalidAmountError, AmountError)
    assert issubclass(NegativeAmountError, AmountError)


@pytest.mark.parametrize("sats", [0, 1, 150_000_000, MAX_SATS])
def test_amount_init_valid(sats: int) -> None:
    amount = Amount(sats)
    assert amount.sats == sats


@pytest.mark.parametrize("bad_sats", [True, False, 1.5, "100", None, Decimal("1")])
def test_amount_init_rejects_non_int_and_bool(bad_sats: Any) -> None:
    with pytest.raises(InvalidAmountError):
        Amount(bad_sats)


@pytest.mark.parametrize("sats", [-1, -100_000_000])
def test_amount_init_rejects_negative(sats: int) -> None:
    with pytest.raises(NegativeAmountError):
        Amount(sats)


def test_amount_init_rejects_above_max_sats() -> None:
    with pytest.raises(InvalidAmountError):
        Amount(MAX_SATS + 1)


def test_amount_is_immutable() -> None:
    amount = Amount(100)
    with pytest.raises(FrozenInstanceError):
        amount.sats = 200  # type: ignore[misc]


@pytest.mark.parametrize(
    ("text", "expected_sats"),
    [
        ("0", 0),
        ("0.00000000", 0),
        ("0.00000001", 1),
        ("1.5", 150_000_000),
        ("0,0002", 20_000),
        ("  0,50  ", 50_000_000),
        ("1e-8", 1),
        ("21000000", MAX_SATS),
        ("21000000.00000000", MAX_SATS),
    ],
)
def test_from_str_valid(text: str, expected_sats: int) -> None:
    assert Amount.from_str(text) == Amount(expected_sats)


@pytest.mark.parametrize("bad_input", [123, 1.5, None, Decimal("1.0")])
def test_from_str_rejects_non_string(bad_input: Any) -> None:
    with pytest.raises(InvalidAmountError):
        Amount.from_str(bad_input)


@pytest.mark.parametrize(
    "invalid_text",
    [
        "",
        "   ",
        "abc",
        "1.2.3",
        "1,2,3",
        "NaN",
        "Infinity",
        "-Infinity",
        "inf",
        "0.000000001",
        "1.123456789",
        "1e-9",
        "21000000.00000001",
        "21000001",
    ],
)
def test_from_str_rejects_invalid_formats_and_limits(invalid_text: str) -> None:
    with pytest.raises(InvalidAmountError):
        Amount.from_str(invalid_text)


@pytest.mark.parametrize("negative_text", ["-0.00000001", "-1", "-0,5"])
def test_from_str_rejects_negative(negative_text: str) -> None:
    with pytest.raises(NegativeAmountError):
        Amount.from_str(negative_text)


@pytest.mark.parametrize(
    ("sats", "expected_btc"),
    [
        (0, "0.00000000"),
        (1, "0.00000001"),
        (20_000, "0.00020000"),
        (150_000_000, "1.50000000"),
        (MAX_SATS, "21000000.00000000"),
    ],
)
def test_to_btc_and_roundtrip(sats: int, expected_btc: str) -> None:
    amount = Amount(sats)
    btc_str = amount.to_btc()
    assert btc_str == expected_btc
    assert Amount.from_str(btc_str) == amount


def test_add_valid() -> None:
    assert Amount(100) + Amount(250) == Amount(350)
    assert Amount(MAX_SATS) + Amount(0) == Amount(MAX_SATS)


def test_add_overflow_raises() -> None:
    with pytest.raises(InvalidAmountError):
        _ = Amount(MAX_SATS) + Amount(1)


@pytest.mark.parametrize("other", [50, "100", None])
def test_add_incompatible_type_raises_type_error(other: Any) -> None:
    with pytest.raises(TypeError):
        _ = Amount(100) + other


def test_sub_valid() -> None:
    assert Amount(350) - Amount(100) == Amount(250)
    assert Amount(100) - Amount(100) == Amount(0)


def test_sub_negative_result_raises() -> None:
    with pytest.raises(NegativeAmountError):
        _ = Amount(100) - Amount(101)


@pytest.mark.parametrize("other", [50, "100", None])
def test_sub_incompatible_type_raises_type_error(other: Any) -> None:
    with pytest.raises(TypeError):
        _ = Amount(100) - other
