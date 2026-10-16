"""
Pytest configuration and fixtures for Create Invoice Management Automation.

Strictly adheres to framework standards:
- Dynamic test data and test case loading from shared Excel workbooks
- 1-to-1 screenshot capture for every test execution
- Live updates to Swarajya-test-cases.xlsx [Sheet: createinvoice-mgmt]
- HTML report generation with full suite statistics
- macOS, Linux & Windows native summary popups (guarded for CI/CD)
"""

import os
import re
import sys
import logging
from datetime import datetime
import pytest

# Ensure module, create root, and workspace root are in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
CREATE_DIR = os.path.dirname(MODULE_DIR)
ROOT_DIR = os.path.dirname(CREATE_DIR)
for path_dir in (MODULE_DIR, CREATE_DIR, ROOT_DIR):
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

from playwright.sync_api import sync_playwright
from shared.pages.login_page import LoginPage
from shared.pages.tfa_page import TfaPage
from invoice_utils.excel_reader import (
    get_base_url,
    read_credentials,
    update_test_result,
    build_automation_id,
    SHEET_NAME,
)
from shared.reporter.hooks import PytestReporterPlugin
from shared.reporter.models import TestCaseResult
from shared.utils.popup import show_summary_popup

log = logging.getLogger("conftest")

BASE_URL = get_base_url(sheet_name=SHEET_NAME)

SCREENSHOTS_DIR = os.path.join(MODULE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


# --- CLI options ---

def pytest_addoption(parser):
    existing = set()
    for grp in getattr(parser, "_groups", []):
        for opt in getattr(grp, "options", []):
            existing.update(getattr(opt, "_short_opts", []))
            existing.update(getattr(opt, "_long_opts", []))
    for opt in getattr(getattr(parser, "_anonymous", None), "options", []):
        existing.update(getattr(opt, "_short_opts", []))
        existing.update(getattr(opt, "_long_opts", []))

    if "--headed" not in existing:
        try:
            parser.addoption("--headed", action="store_true", default=False, help="Run browser in headed mode.")
        except ValueError:
            pass
    if "--headless" not in existing:
        try:
            parser.addoption("--headless", action="store_true", default=False, help="Run browser headless.")
        except ValueError:
            pass
    if "--slowmo" not in existing:
        try:
            parser.addoption("--slowmo", action="store", default=0, type=int, help="Slowdown Playwright actions (ms).")
        except ValueError:
            pass


def _is_headless(config):
    try:
        if config.getoption("--headed"):
            return False
        if config.getoption("--headless"):
            return True
    except (ValueError, AttributeError):
        pass
    env = os.environ.get("HEADLESS")
    if env is not None:
        return env.lower() in ("true", "1", "yes")
    return True


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance, request):
    headless = _is_headless(request.config)
    log.info("Launching Chromium (headless=%s)", headless)
    args = (["--start-maximized"] if (not headless and sys.platform.startswith("win"))
            else ["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-gpu", "--window-size=1920,1080"])
    b = playwright_instance.chromium.launch(headless=headless, slow_mo=0, args=args)
    yield b
    b.close()


@pytest.fixture(scope="function")
def context(browser, request):
    headless = _is_headless(request.config)
    ctx = (browser.new_context(viewport={"width": 1920, "height": 1080})
           if headless else browser.new_context(no_viewport=True))
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context):
    p = context.new_page()
    yield p
    p.close()


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def admin_creds():
    return read_credentials(role="Admin", sheet_name=SHEET_NAME)


@pytest.fixture(scope="function")
def logged_in_page(page, base_url, admin_creds):
    """Fixture that logs in as Admin and yields page on Dashboard."""
    login = LoginPage(page, base_url)
    login.navigate()
    login.login(
        employee_id=admin_creds["employee_id"],
        password=admin_creds["password"],
        auth_code=admin_creds.get("auth_code", "111111"),
    )
    yield page


# --- Session Metrics & HTML Reporting Plugin ---

_results = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
_failed_tests = []
_start_time = None
_html_reporter = PytestReporterPlugin()


def _clean_old_screenshots(directory: str, max_age_hours: int = 24, max_files: int = 60):
    if not os.path.exists(directory):
        return
    import time
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    files = []
    for f in os.listdir(directory):
        if f.lower().endswith(".png"):
            full_path = os.path.join(directory, f)
            try:
                mtime = os.path.getmtime(full_path)
                if mtime < cutoff:
                    os.remove(full_path)
                else:
                    files.append((mtime, full_path))
            except Exception:
                pass
    if len(files) > max_files:
        files.sort(key=lambda x: x[0])
        for _, old_path in files[:len(files) - max_files]:
            try:
                os.remove(old_path)
            except Exception:
                pass


def pytest_sessionstart(session):
    global _start_time
    _start_time = datetime.now()
    _clean_old_screenshots(SCREENSHOTS_DIR, max_age_hours=24, max_files=60)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" or (report.when == "setup" and report.skipped):
        tc_id = "UNKNOWN"
        marker = item.get_closest_marker("tc_id")
        if marker and marker.args:
            tc_id = str(marker.args[0]).strip()
        else:
            match = re.search(r"(TC_[A-Za-z0-9_]+)", item.name) or re.search(r"(TC_[A-Za-z0-9_]+)", report.nodeid)
            if match:
                tc_id = match.group(1).strip()

        status = "PASS" if report.passed else "FAIL" if report.failed else "SKIPPED"

        if status == "PASS":
            _results["passed"] += 1
            remarks = "Execution Passed: Successfully verified invoice behavior."
        elif status == "FAIL":
            _results["failed"] += 1
            remarks = str(getattr(report, "longreprtext", ""))[:500] or str(report.longrepr)[:500]
            _failed_tests.append(f"{tc_id} ({item.name})")
        else:
            _results["skipped"] += 1
            remarks = "Execution Skipped"
        _results["total"] += 1

        shot_path = None
        pg = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
        if pg and status in ("PASS", "FAIL"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shot_filename = f"{status}_{tc_id}__{ts}.png"
            shot_path = os.path.join(SCREENSHOTS_DIR, shot_filename)
            try:
                pg.screenshot(path=shot_path, timeout=5000)
                log.info("Captured 1-to-1 test screenshot (%s): %s", status, shot_filename)
            except Exception as exc:
                log.warning("Screenshot capture failed for %s: %s", tc_id, exc)
                shot_path = None

        if tc_id != "UNKNOWN":
            try:
                update_test_result(
                    tc_id=tc_id,
                    status=status,
                    remarks=remarks,
                    auto_id=build_automation_id(tc_id),
                    sheet_name=SHEET_NAME,
                )
            except Exception as exc:
                log.warning("Excel update failed for %s: %s", tc_id, exc)

        _html_reporter.record_test(
            item=item,
            report=report,
            status=status,
            remarks=remarks,
            auto_id=build_automation_id(tc_id),
            screenshot_path=shot_path,
            duration=getattr(report, "duration", 0.0),
        )


def pytest_sessionfinish(session, exitstatus):
    duration = datetime.now() - _start_time if _start_time else None
    dur_str = str(duration).split(".")[0] if duration else "N/A"

    passed = _results["passed"]
    failed = _results["failed"]
    skipped = _results["skipped"]
    total = _results["total"]

    status = "ALL PASSED" if failed == 0 else f"{failed} FAILED"

    lines = [
        f"{'=' * 44}",
        f"  SWARAJYA CREATE INVOICE MANAGEMENT — {status}",
        f"{'=' * 44}",
        f"  Total: {total}  |  Passed: {passed}  |  Failed: {failed}  |  Skipped: {skipped}",
        f"  Duration: {dur_str}",
    ]
    if _failed_tests:
        lines.append("  Failed:")
        for ft in _failed_tests[:10]:
            lines.append(f"    - {ft}")
    lines.append(f"{'=' * 44}")

    try:
        print("\n" + "\n".join(lines) + "\n")
    except UnicodeEncodeError:
        print("\n" + "\n".join(lines).encode("ascii", "replace").decode() + "\n")

    if getattr(session.config.option, "collectonly", False):
        return

    report_path = None
    if total > 0:
        try:
            report_path = _html_reporter.finalize_report(filename_prefix="create_invoice_management")
        except Exception as exc:
            log.warning("Could not finalize HTML report: %s", exc)

    # Display execution summary popup
    try:
        show_summary_popup(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration_str=str(dur_str),
            failed_tests=_failed_tests,
            suite_title="Create Invoice Management",
            report_path=report_path,
        )
    except Exception as exc:
        log.warning("Could not display summary popup: %s", exc)
