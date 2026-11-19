from __future__ import annotations


class AmountError(ValueError):
    """Basis-Fehler für alle Betragsfehler."""

    pass


class InvalidAmountError(AmountError):
    """Ungültiges Format. Zu viele Nachkommastellen oder über 21 Mio. BTC"""

    pass


class NegativeAmountError(AmountError):
    """Betrag wäre Negativ."""

    pass
