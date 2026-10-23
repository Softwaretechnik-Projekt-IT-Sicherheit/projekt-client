"""Einstiegspunkt: `python -m hot_wallet`."""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import version


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hot-wallet", description="Bitcoin Hot Wallet")
    parser.add_argument("--version", action="version", version=f"%(prog)s {version('hot-wallet')}")
    parser.parse_args(argv)

    print("Hot Wallet gestartet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
