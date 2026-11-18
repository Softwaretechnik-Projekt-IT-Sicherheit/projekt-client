"""Zentrale, lokalisierbare Nutzertexte: Katalog und Hilfetexte je Befehl."""

from __future__ import annotations

_CATALOGS: dict[str, dict[str, str]] = {
    "de": {
        "error.unknown_command": "Unbekannter Befehl: {command}",
        "help.register": "Registriert einen neuen Benutzer. Das Passwort wird verdeckt abgefragt.",
        "help.login": "Meldet einen Benutzer an. Das Passwort wird verdeckt abgefragt.",
        "help.create_wallet": (
            "Erstellt ein neues Wallet mit dem angegebenen Namen. "
            "Optional: Anzahl der Wörter der Wiederherstellungsphrase (Standard: 12)."
        ),
        "help.restore_wallet": (
            "Stellt ein Wallet aus seiner Wiederherstellungsphrase wieder her."
        ),
        "help.show_address": (
            "Zeigt die Empfangsadresse eines Wallets an. Optional wird eine neue Adresse erzeugt."
        ),
        "help.show_balance": "Zeigt den Kontostand eines Wallets an.",
        "help.show_transactions": "Zeigt Transaktionen an.",
        "help.create_transactions": "Erstellt eine neue Transaktion.",
        "help.send": (
            "Sendet einen Betrag von einem Wallet an eine Bitcoin-Adresse. "
            "Vor dem Senden wird eine Bestätigung abgefragt."
        ),
    },
}


class Locale:
    def __init__(self, lang: str = "de") -> None:
        self._lang: str = lang
        self._catalog: dict[str, str] = _CATALOGS.get(lang, {})

    def get(self, key: str, **kwargs: object) -> str:
        text = self._catalog.get(key)
        if text is None:
            return f"[{key}]"  # sichtbarer Fallback statt Absturz
        try:
            return text.format(**kwargs)
        except KeyError, IndexError:
            return text  # fehlender Platzhalter-Wert: Rohtext statt Absturz

    def help(self, command: str) -> str:
        return self.get(f"help.{command}")
