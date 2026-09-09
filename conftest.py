"""
Root Pytest Configuration for Swarajya Staging Automation.
Provides session-wide test collection, Playwright HTML report generation,
and executive test reporting.
"""

import os
import re
import sys
from datetime import datetime

# Ensure workspace root is in sys.path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from shared.reporter import PytestReporterPlugin
from shared.utils.popup import show_summary_popup

_reporter_plugin = None
_session_start_time = None
_session_stats = {"passed": 0, "failed": 0, "skipped": 0, "failed_tests": []}


def pytest_addoption(parser):
    """Add CLI flags for reporting options."""
    group = parser.getgroup("swarajya_reporting", "Swarajya Playwright HTML Reporting")
    group.addoption(
        "--open-report",
        action="store_true",
        default=False,
        help="Automatically open the generated HTML report in browser after test run",
    )
    group.addoption(
        "--report-title",
        action="store",
        default="Swarajya Master Automation",
        help="Custom title for the generated HTML report",
    )


def pytest_sessionstart(session):
    global _reporter_plugin, _session_start_time
    _session_start_time = datetime.now()
    title = getattr(session.config.option, "report_title", "Swarajya Master Automation")
    _reporter_plugin = PytestReporterPlugin(suite_title=title)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" and not (report.when == "setup" and report.skipped):
        return

    status = "PASS" if report.passed else "FAIL" if report.failed else "SKIPPED"

    # Identify TC ID
    tc_id = "UNKNOWN"
    m = re.search(r"(TC_[A-Z0-9_]+)", item.name)
    if m:
        tc_id = m.group(1)

    # Search for associated screenshot if captured
    screenshot_path = None
    possible_dirs = [
        os.path.join(ROOT, "screenshots"),
        os.path.join(os.path.dirname(str(item.fspath)), "screenshots"),
        os.path.join(os.path.dirname(os.path.dirname(str(item.fspath))), "screenshots"),
    ]
    for pdir in possible_dirs:
        if os.path.exists(pdir):
            for fname in sorted(os.listdir(pdir), reverse=True):
                if fname.lower().endswith(".png") and (tc_id in fname or item.name in fname):
                    screenshot_path = os.path.join(pdir, fname)
                    break
        if screenshot_path:
            break

    # Extract remarks if attached to item
    remarks = getattr(item, "_report_remark", "")
    auto_id = getattr(item, "_report_auto_id", "")

    if _reporter_plugin:
        _reporter_plugin.record_test(
            item=item,
            report=report,
            status=status,
            remarks=remarks,
            auto_id=auto_id,
            screenshot_path=screenshot_path,
        )

    # Track session stats
    if report.passed:
        _session_stats["passed"] += 1
    elif report.failed:
        _session_stats["failed"] += 1
        _session_stats["failed_tests"].append(f"{tc_id} ({item.name})")
    elif report.skipped:
        _session_stats["skipped"] += 1


def pytest_sessionfinish(session, exitstatus):
    if getattr(session.config.option, "collectonly", False):
        return

    if not _reporter_plugin:
        return

    # Check if any tests were executed in root session
    total = _session_stats["passed"] + _session_stats["failed"] + _session_stats["skipped"]
    if total == 0:
        return

    report_path = _reporter_plugin.finalize_report(filename_prefix="master_run")

    if getattr(session.config.option, "open_report", False) or os.environ.get("OPEN_REPORT") == "1":
        _reporter_plugin.reporter.open_in_browser(report_path)

    # Calculate duration
    dur_sec = (datetime.now() - _session_start_time).total_seconds() if _session_start_time else 0
    dur_str = f"{int(dur_sec // 60)}m {int(dur_sec % 60)}s"

    try:
        show_summary_popup(
            total=total,
            passed=_session_stats["passed"],
            failed=_session_stats["failed"],
            skipped=_session_stats["skipped"],
            duration_str=dur_str,
            failed_tests=_session_stats["failed_tests"],
            suite_title=getattr(session.config.option, "report_title", "Swarajya Master Automation"),
            report_path=report_path,
        )
    except Exception as exc:
        print(f"[REPORTER] Popup notification notice: {exc}")
