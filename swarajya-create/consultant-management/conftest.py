"""
Conftest for Consultant Management Automation.
Provides Playwright browser, page, login_page, and tfa_page fixtures, Excel reporting, and popup.
"""

import os
import sys
import logging
from datetime import datetime
import pytest
from playwright.sync_api import sync_playwright

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
CREATE_DIR = os.path.dirname(MODULE_DIR)
ROOT_DIR = os.path.dirname(CREATE_DIR)
LOGIN_DIR = os.path.join(ROOT_DIR, "swarajya-login", "swarajya-automation")
for p in (LOGIN_DIR, CREATE_DIR, ROOT_DIR, MODULE_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from shared.utils.popup import show_desktop_popup
except ImportError:
    show_desktop_popup = None

from pages.login_page import LoginPage
from pages.tfa_page import TfaPage
from consultant_workbook import ConsultantWorkbook

logger = logging.getLogger("consultant.conftest")

_start_time = datetime.now()
BASE_URL = os.environ.get("SWARAJYA_BASE_URL", "https://swarajya-stg.corecotechnologies.com")
SCREENSHOTS_DIR = os.path.join(MODULE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
WORKBOOK_PATH = os.path.join(MODULE_DIR, "test_data", "Create-Consultant-Management.xlsx")
_workbook = ConsultantWorkbook(WORKBOOK_PATH) if os.path.exists(WORKBOOK_PATH) else None

RESULT_SUMMARY = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "failed_tests": [],
}


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
            parser.addoption("--headed", action="store_true", default=False, help="Run browser in headed mode")
        except ValueError:
            pass
    if "--headless" not in existing:
        try:
            parser.addoption("--headless", action="store_true", default=False, help="Run browser headless")
        except ValueError:
            pass
    if "--slowmo" not in existing:
        try:
            parser.addoption("--slowmo", action="store", default=0, type=int, help="Slowdown Playwright actions (ms)")
        except ValueError:
            pass


def is_headless(config):
    if config.getoption("--headed", default=False):
        return False
    if config.getoption("--headless", default=False):
        return True
    env_val = os.environ.get("HEADLESS")
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes")
    return True


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance, request):
    headless = is_headless(request.config)
    slowmo = 0
    try:
        slowmo = request.config.getoption("--slowmo") or 0
    except (ValueError, AttributeError):
        pass

    launch_args = []
    if not headless:
        launch_args.append("--start-maximized")
    else:
        launch_args.extend([
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
        ])

    browser = playwright_instance.chromium.launch(
        headless=headless,
        slow_mo=slowmo,
        args=launch_args,
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser, request):
    headless = is_headless(request.config)
    if headless:
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    else:
        ctx = browser.new_context(no_viewport=True)
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context):
    pg = context.new_page()
    pg.set_default_timeout(10_000)
    yield pg
    pg.close()


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def login_page(page, base_url):
    return LoginPage(page, base_url)


@pytest.fixture
def tfa_page(page, base_url):
    return TfaPage(page, base_url)


@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(request, page):
    yield
    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = request.node.name.replace("[", "_").replace("]", "").replace("/", "_")
        path = os.path.join(SCREENSHOTS_DIR, f"{name}_{timestamp}.png")
        try:
            page.screenshot(path=path, full_page=True)
            logger.info("Screenshot saved: %s", path)
        except Exception as exc:
            logger.warning("Screenshot failed: %s", exc)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def _find_tc_id(nodeid):
    import re
    match = re.search(r"(TC_CONSULTANT_(?:POS|NEG)_\d+)", nodeid)
    return match.group(1) if match else None


def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    RESULT_SUMMARY["total"] += 1
    if report.passed:
        RESULT_SUMMARY["passed"] += 1
    elif report.failed:
        RESULT_SUMMARY["failed"] += 1
        RESULT_SUMMARY["failed_tests"].append(report.nodeid)
    elif report.skipped:
        RESULT_SUMMARY["skipped"] += 1

    tc_id = _find_tc_id(report.nodeid)
    if not tc_id or not _workbook:
        return

    if report.passed:
        result = "PASS"
        remarks = "Automation completed successfully."
    elif report.failed:
        result = "FAIL"
        remarks = str(getattr(report, "longreprtext", ""))[:1000]
    elif report.skipped:
        result = "SKIPPED"
        remarks = str(getattr(report, "longreprtext", ""))[:1000]
    else:
        return

    try:
        _workbook.update_test_result(tc_id, result, remarks)
    except Exception as exc:
        logger.warning("Could not update Excel for %s: %s", tc_id, exc)


def pytest_sessionfinish(session, exitstatus):
    duration = datetime.now() - _start_time if _start_time else None
    dur_str = str(duration).split(".")[0] if duration else "N/A"
    RESULT_SUMMARY["duration"] = dur_str

    passed = RESULT_SUMMARY["passed"]
    failed = RESULT_SUMMARY["failed"]
    skipped = RESULT_SUMMARY["skipped"]
    total = RESULT_SUMMARY["total"]
    failed_tests = RESULT_SUMMARY["failed_tests"]

    status = "ALL PASSED" if failed == 0 else f"{failed} FAILED"

    lines = [
        f"{'=' * 56}",
        f"  SWARAJYA CONSULTANT MANAGEMENT - {status}",
        f"{'=' * 56}",
        f"  Total : {total}   Passed : {passed}   Failed : {failed}   Skipped : {skipped}",
        f"  Time  : {dur_str}",
        f"{'=' * 56}",
    ]
    if failed_tests:
        lines.append("  Failed Tests:")
        for ft in failed_tests[:10]:
            lines.append(f"    - {ft}")
        lines.append(f"{'=' * 56}")

    try:
        print("\n" + "\n".join(lines) + "\n")
    except UnicodeEncodeError:
        print("\n" + "\n".join(lines).encode("ascii", "replace").decode() + "\n")

    if not getattr(session.config.option, "collectonly", False) and not is_headless(session.config):
        if show_desktop_popup:
            show_desktop_popup(
                title=os.environ.get("SWARAJYA_POPUP_TITLE", "Swarajya Consultant Management - Results"),
                total=total,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration=dur_str,
                failed_tests=failed_tests,
            )
