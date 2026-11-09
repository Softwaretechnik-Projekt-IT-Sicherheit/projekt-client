from __future__ import annotations

from dataclasses import dataclass

from wallet.domain import User


@dataclass
class Session:
    """Hinweis: im Diagramm nicht modelliert, wird aber von den Services verwendet."""

    user: User
