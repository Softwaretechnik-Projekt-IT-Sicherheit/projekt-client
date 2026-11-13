from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Amount:
    sats: int

    @classmethod
    def from_str(cls, text: str) -> Amount:
        raise NotImplementedError

    def from_int(cls, value: int) -> Amount:
        raise NotImplementedError

    def to_btc(self) -> str:
        raise NotImplementedError

    def __add__(self, other: Amount) -> Amount:
        raise NotImplementedError

    def __sub__(self, other: Amount) -> Amount:
        raise NotImplementedError
