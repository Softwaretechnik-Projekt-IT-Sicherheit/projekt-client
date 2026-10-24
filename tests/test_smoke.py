"""Smoke-Tests: Lässt sich die Anwendung überhaupt starten?"""

import subprocess  # noqa: S404
import sys

from wallet.__main__ import main


def test_main_returns_zero() -> None:
    assert main([]) == 0


def test_module_starts_without_error() -> None:
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "wallet", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "wallet" in result.stdout
