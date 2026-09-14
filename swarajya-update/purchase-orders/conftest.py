import logging
import os
import sys
import shutil
from datetime import datetime
from typing import Optional
_MODULE_ROOT = os.path.dirname(os.path.abspath(__file__))
_UPDATE_ROOT = os.path.dirname(_MODULE_ROOT)
_WORKSPACE_ROOT = os.path.dirname(_UPDATE_ROOT)
for _p in (_MODULE_ROOT, _UPDATE_ROOT, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import re
import pytest
from playwright.sync_api import sync_playwright
from shared.reporter import PytestReporterPlugin
from shared.utils.popup import show_summary_popup

from po_update_pages.login_page import LoginPage
from po_update_utils.excel_reader import read_credentials

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("po_conftest")

SCREENSHOTS_DIR = os.path.join(_MODULE_ROOT, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

_session_stats = {"passed": 0, "failed": 0, "skipped": 0, "start_time": datetime.now(), "failed_tests": []}
_html_reporter = PytestReporterPlugin(suite_title="Purchase Order Update Management")


def pytest_addoption(parser):
    """Add CLI flags for headed mode and slow motion."""
    try:
        parser.addoption("--headed", action="store_true", default=False, help="Run tests in visible headed browser")
    except Exception:
        pass
    try:
        parser.addoption("--slowmo", type=int, default=0, help="Slow down Playwright actions by milliseconds")
    except Exception:
        pass


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(request, playwright_instance):
    """Launch shared Playwright browser instance."""
    is_headed = request.config.getoption("--headed", default=False)
    env_headless = os.environ.get("HEADLESS", "true").lower() == "true"
    headless = False if is_headed else env_headless

    slow_mo = request.config.getoption("--slowmo", default=0)

    browser = playwright_instance.chromium.launch(
        headless=headless,
        slow_mo=slow_mo,
        args=["--start-maximized", "--disable-dev-shm-usage"],
    )
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def session_storage_state(browser):
    """Authenticate and cache auth_state.json for fast session reuse."""
    storage_path = os.path.join(_MODULE_ROOT, "test_data", "auth_state.json")
    fallback_auth = os.path.join(_WORKSPACE_ROOT, "swarajya-create", "customer-management", "test_data", "auth_state.json")

    # Reuse existing auth state if present and recent
    if not os.path.exists(storage_path) and os.path.exists(fallback_auth):
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        shutil.copy2(fallback_auth, storage_path)

    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    login_page = LoginPage(page)
    success = login_page.login(role="Admin")
    if success:
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        context.storage_state(path=storage_path)
        log.info(f"Saved authenticated session state to {storage_path}")

    context.close()
    return storage_path if os.path.exists(storage_path) else None


@pytest.fixture(scope="function")
def authenticated_page(browser, session_storage_state):
    """Provide an authenticated Playwright page context."""
    kwargs = {"viewport": {"width": 1920, "height": 1080}}
    if session_storage_state and os.path.exists(session_storage_state):
        kwargs["storage_state"] = session_storage_state

    context = browser.new_context(**kwargs)
    page = context.new_page()

    if not session_storage_state or not os.path.exists(session_storage_state):
        login_page = LoginPage(page)
        login_page.login(role="Admin")

    yield page
    context.close()


@pytest.fixture(scope="function")
def unauthenticated_page(browser):
    """Provide a fresh, clean Playwright page."""
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    yield page
    context.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    tc_id = "UNKNOWN"
    for marker in item.iter_markers(name="tc_id"):
        if marker.args:
            tc_id = marker.args[0]
            break

    if tc_id == "UNKNOWN":
        m = re.search(r"TC_PO_(?:POS|NEG|AUTH|NAV|FORM)_\d+", item.name)
        if m:
            tc_id = m.group(0)

    page = item.funcargs.get("authenticated_page") or item.funcargs.get("unauthenticated_page") or item.funcargs.get("page")
    scr = None

    if report.passed:
        _session_stats["passed"] += 1
        if page:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_name = tc_id if tc_id != "UNKNOWN" else item.name.replace("[", "_").replace("]", "_")
            scr = os.path.join(SCREENSHOTS_DIR, f"PASS_{clean_name}_{ts}.png")
            try:
                page.screenshot(path=scr)
            except Exception as e:
                log.warning(f"Could not capture pass screenshot: {e}")
                scr = None
        _html_reporter.record_test(
            item=item,
            report=report,
            status="PASS",
            remarks="Execution Passed Successfully",
            auto_id=tc_id if tc_id != "UNKNOWN" else "",
            screenshot_path=scr,
            duration=report.duration,
        )
    elif report.failed:
        _session_stats["failed"] += 1
        fail_label = tc_id if tc_id != "UNKNOWN" else item.name
        _session_stats["failed_tests"].append(fail_label)
        if page:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_name = item.name.replace("[", "_").replace("]", "_")
            scr = os.path.join(SCREENSHOTS_DIR, f"FAIL_{clean_name}_{ts}.png")
            try:
                page.screenshot(path=scr, full_page=True)
                log.info(f"Failure screenshot captured: {scr}")
            except Exception as e:
                log.warning(f"Could not capture screenshot: {e}")
                scr = None
        err_msg = str(report.longrepr) if report.longrepr else "Test Assertion / Execution Failure"
        _html_reporter.record_test(
            item=item,
            report=report,
            status="FAIL",
            remarks=err_msg[:250],
            auto_id=tc_id if tc_id != "UNKNOWN" else "",
            screenshot_path=scr,
            duration=report.duration,
        )
    elif report.skipped:
        _session_stats["skipped"] += 1
        _html_reporter.record_test(
            item=item,
            report=report,
            status="SKIPPED",
            remarks="Scenario Skipped",
            auto_id=tc_id if tc_id != "UNKNOWN" else "",
            duration=report.duration,
        )


def pytest_sessionfinish(session, exitstatus):
    """Generate HTML report and display desktop summary popup dialog."""
    if getattr(session.config.option, "collectonly", False):
        return

    dur = (datetime.now() - _session_stats["start_time"]).total_seconds()
    dur_str = f"{int(dur // 60)}m {int(dur % 60)}s"
    total = _session_stats["passed"] + _session_stats["failed"] + _session_stats["skipped"]

    report_path = None
    if total > 0:
        try:
            report_path = _html_reporter.finalize_report(filename_prefix="po_update")
        except Exception as exc:
            log.warning(f"Could not finalize HTML report: {exc}")

    try:
        show_summary_popup(
            total=total,
            passed=_session_stats["passed"],
            failed=_session_stats["failed"],
            skipped=_session_stats["skipped"],
            duration_str=dur_str,
            failed_tests=_session_stats["failed_tests"],
            suite_title="Purchase Order Update Management",
            report_path=report_path,
        )
    except Exception as e:
        log.warning(f"Could not display summary popup: {e}")
