from __future__ import annotations


class Locale:
    def __init__(self, lang: str = "de") -> None:
        self._lang: str = lang
        self._catalog: dict[str, str] = {}

    def get(self, key: str, **kwargs: object) -> str:
        raise NotImplementedError

    def help(self, command: str) -> str:
        raise NotImplementedError
