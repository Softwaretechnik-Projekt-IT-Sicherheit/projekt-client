"""Tests für die zentralen Nutzertexte (T0019)."""

import pytest

from wallet.presentation import CLI, Locale

# Öffentliche CLI-Methoden außer dem Einstieg `main` sind die Befehle.
COMMANDS = [name for name in vars(CLI) if not name.startswith("_") and name != "main"]


def test_get_fills_placeholders() -> None:
    assert Locale().get("error.unknown_command", command="foo") == "Unbekannter Befehl: foo"


def test_get_missing_key_returns_visible_fallback() -> None:
    assert Locale().get("gibt.es.nicht") == "[gibt.es.nicht]"


def test_get_missing_placeholder_value_does_not_crash() -> None:
    assert Locale().get("error.unknown_command") == "Unbekannter Befehl: {command}"


def test_commands_found() -> None:
    assert COMMANDS


@pytest.mark.parametrize("command", COMMANDS)
def test_every_command_has_help(command: str) -> None:
    assert Locale().help(command) != f"[help.{command}]"
