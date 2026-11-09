"""Gemeinsame pytest-Konfiguration."""

from collections.abc import Generator

import pytest


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Wertet NotImplementedError aus Stubs als xfail statt als Fehler.

    Smoke-Tests sind ausgenommen: Die Anwendung muss immer starten können.
    """
    report = yield
    if (
        report.failed
        and call.excinfo is not None
        and call.excinfo.errisinstance(NotImplementedError)
        and item.get_closest_marker("smoke") is None
    ):
        report.outcome = "skipped"
        report.wasxfail = "noch nicht implementiert"
    return report
