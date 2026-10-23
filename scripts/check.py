"""Führt lokal dieselben Prüfungen aus wie die GitHub Actions.

Aufruf (macOS, Linux, Windows):
    uv run python scripts/check.py           # alles
    uv run python scripts/check.py --fix     # Linting/Format automatisch korrigieren
    uv run python scripts/check.py --tests   # nur Tests + Smoke-Test
"""

from __future__ import annotations

import subprocess  # noqa: S404
import sys

QUALITY = [
    ("Linting (ruff)", ["ruff", "check", "."]),
    ("Formatierung (ruff format)", ["ruff", "format", "--check", "."]),
    ("Typprüfung (mypy)", ["mypy", "src"]),
]

QUALITY_FIX = [
    ("Linting + Autofix (ruff)", ["ruff", "check", ".", "--fix"]),
    ("Formatieren (ruff format)", ["ruff", "format", "."]),
]

TESTS = [
    ("Tests (pytest)", ["pytest", "--cov=hot_wallet", "--cov-report=term-missing"]),
    ("Smoke-Test", [sys.executable, "-m", "hot_wallet", "--version"]),
]


def run(steps: list[tuple[str, list[str]]]) -> list[str]:
    failed = []
    for name, cmd in steps:
        print(f"\n▶ {name}\n  $ {' '.join(cmd)}", flush=True)
        if subprocess.run(cmd, check=False).returncode != 0:  # noqa: S603
            failed.append(name)
    return failed


def main() -> int:
    args = set(sys.argv[1:])
    steps: list[tuple[str, list[str]]] = []

    if "--tests" not in args:
        steps += QUALITY_FIX if "--fix" in args else QUALITY
    steps += TESTS

    failed = run(steps)

    print("\n" + "─" * 50)
    if failed:
        print("❌ Fehlgeschlagen:")
        for name in failed:
            print(f"   - {name}")
        return 1
    print("✅ Alle Prüfungen bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
