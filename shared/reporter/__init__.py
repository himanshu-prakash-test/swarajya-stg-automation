"""
Playwright HTML Reporter Package.
Provides modern, interactive HTML test dashboards for Playwright test automation.
"""

from .hooks import PytestReporterPlugin
from .html_reporter import PlaywrightHTMLReporter
from .models import SessionSummary, TestCaseResult

__all__ = [
    "PlaywrightHTMLReporter",
    "PytestReporterPlugin",
    "TestCaseResult",
    "SessionSummary",
]
