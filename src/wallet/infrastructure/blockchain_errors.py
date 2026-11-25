from __future__ import annotations


class BlockchainError(Exception):
    """Basis-Fehler für alle Fehler beim Blockchain-Zugriff."""

    pass


class NetworkUnavailableError(BlockchainError):
    """Kein Blockchain-Provider erreichbar (kein Netz, Timeout, Provider-Fehler)."""

    pass
