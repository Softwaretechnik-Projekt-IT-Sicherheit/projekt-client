from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from wallet.domain.amount_errors import InvalidAmountError, NegativeAmountError

COIN_IN_SATS = 100_000_000
MAX_BTC = 21_000_000
MAX_SATS = MAX_BTC * COIN_IN_SATS


@dataclass(frozen=True)
class Amount:
    sats: int

    def __post_init__(self) -> None:
        # ist Übergabe wirklich int(bool erbt von int)?
        if not isinstance(self.sats, int) or isinstance(self.sats, bool):
            raise InvalidAmountError("Satoshi-Betrag muss eine ganze Zahl sein.")
        # Invariante >= 0
        if self.sats < 0:
            raise NegativeAmountError(f"Satoshi-Betrag darf nicht negativ sein: '{self.sats}'")
        # Obergrenze Sats
        if self.sats > MAX_SATS:
            raise InvalidAmountError(f"Betrag übersteigt das Bitcoin-Limit: '{self.sats}'")

    @classmethod
    def from_str(cls, text: str) -> Amount:
        """
        Erzeugt ein Amount-Objekt aus einem String wie bspw. '1.5' oder '0,0002'.
        Wandelt den Wert exakt in Satoshi um (deswegen ohne floats).
        """
        if not isinstance(text, str):
            raise InvalidAmountError(
                f"Eingabe muss ein String sein, nicht '{type(text).__name__}'."
            )
        cleaned_text = text.strip().replace(",", ".")
        if not cleaned_text:
            raise InvalidAmountError("Eingabe darf nicht leer sein.")
        # parsen ohne float
        try:
            decimal = Decimal(cleaned_text)
        except InvalidOperation:
            raise InvalidAmountError(f"Ungültiges Zahlenformat: '{text}'") from None
        # Endlichkeitsprüfung
        if not decimal.is_finite():
            raise InvalidAmountError(f"Ungültiges Zahlenformat: '{text}'")
        # Negativprüfung
        if decimal < 0:
            raise NegativeAmountError(f"Betrag darf nicht negativ sein: '{text}'")
        # Obergrenzenprüfung
        if decimal > MAX_BTC:
            raise InvalidAmountError(f"Betrag übersteigt das Bitcoin-Limit: '{text}'")
        # max 8 Nachkommastellen
        exp = decimal.as_tuple().exponent
        if isinstance(exp, int) and exp < -8:
            raise InvalidAmountError(f"Maximal 8 Nachkommastellen erlaubt: '{text}'")
        # in Satoshis
        sats_decimal = decimal * Decimal(COIN_IN_SATS)
        # Überprüfung ob richtig abgebildet
        if sats_decimal != sats_decimal.to_integral_value():
            raise InvalidAmountError(
                f"Betrag konnte nicht exakt in Satoshis umgewandelt werden: '{text}'."
            )

        return cls(sats=int(sats_decimal))

    @classmethod
    def from_int(cls, value: int) -> Amount:
        raise NotImplementedError

    def to_btc(self) -> str:
        """Liefert den Betrag formatiert als BTC mit exakt 8 Nachkommastellen als String"""
        decimal = Decimal(self.sats) / Decimal(COIN_IN_SATS)
        return f"{decimal:.8f}"

    def __add__(self, other: object) -> Amount:
        if not isinstance(other, Amount):
            return NotImplemented
        return Amount(self.sats + other.sats)

    def __sub__(self, other: object) -> Amount:
        if not isinstance(other, Amount):
            return NotImplemented
        if self.sats - other.sats < 0:
            raise NegativeAmountError(
                f"Subtraktion führt zu einem negativen Betrag: '{self.sats} - {other.sats}'"
            )
        return Amount(self.sats - other.sats)
