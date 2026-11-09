"""Bitcoin Hot Wallet.

Beim Import werden alle Schichten geladen – damit sind sämtliche Klassen registriert
und werden auch von PyInstaller zuverlässig gefunden.
"""

from wallet import application, domain, infrastructure, presentation

__all__ = ["application", "domain", "infrastructure", "presentation"]
