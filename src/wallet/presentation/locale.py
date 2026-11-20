"""Zentrale, lokalisierbare Nutzertexte: Katalog und Hilfetexte je Befehl."""

from __future__ import annotations

import json
from importlib.resources import files


class Locale:
    def __init__(self, lang: str = "de") -> None:
        self._lang: str = lang
        # Texte liegen in locales/<lang>.json; keine Seeds, Schlüssel oder Passwörter (/PND 020/)
        path = files("wallet.presentation").joinpath("locales", f"{lang}.json")
        try:
            self._catalog: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self._catalog = {}  # unbekannte Sprache: jeder Text zeigt den sichtbaren Fallback

    def get(self, key: str, **kwargs: object) -> str:
        # "help.send" -> catalog["help"]["send"]
        node: object = self._catalog
        for part in key.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if not isinstance(node, str):
            return f"[{key}]"  # sichtbarer Fallback statt Absturz
        try:
            return node.format(**kwargs)
        except KeyError, IndexError:
            return node  # fehlender Platzhalter-Wert: Rohtext statt Absturz

    def help(self, command: str) -> str:
        return self.get(f"help.{command}")
