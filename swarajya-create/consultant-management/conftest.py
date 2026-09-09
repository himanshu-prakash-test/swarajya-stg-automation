import logging
import os
import sys
import re
from datetime import datetime

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_CREATE_ROOT = os.path.dirname(_PROJECT_ROOT)
_WORKSPACE_ROOT = os.path.dirname(_CREATE_ROOT)
for _p in (_PROJECT_ROOT, _CREATE_ROOT, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from playwright.sync_api import sync_playwright

from consultant_pages.login_page import LoginPage
from consultant_utils.excel_reader import build_automation_id, read_credentials, update_test_result
from shared.utils.popup import show_summary_popup
from shared.reporter import PytestReporterPlugin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("conftest")

ROOT = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS = os.path.join(ROOT, "screenshots")
os.makedirs(SCREENSHOTS, exist_ok=True)


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


def is_headless(config) -> bool:
    if config.getoption("--headed", default=False):
        return False
    if config.getoption("--headless", default=False):
        return True
    env_val = os.environ.get("HEADLESS")
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes")
    return True


@pytest.fixture(scope="session")
def headed(request) -> bool:
    return not is_headless(request.config)


@pytest.fixture(scope="session")
def slowmo(request) -> int:
    try:
        return request.config.getoption("--slowmo") or 0
    except Exception:
        return 0


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance, headed, slowmo):
    br = playwright_instance.chromium.launch(headless=not headed, slow_mo=slowmo)
    yield br
    br.close()


def _wait_until_server_healthy(page, max_retries=6, delay_s=2):
    """Poll staging URL dynamically to confirm server is healthy and not 503."""
    url = "https://swarajya-stg.corecotechnologies.com/"
    for attempt in range(max_retries):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            content = page.content().lower()
            if "service unavailable" not in content and "503" not in content:
                return True
        except Exception:
            pass
        page.wait_for_timeout(delay_s * 1000)
    return False


@pytest.fixture(scope="session")
def session_storage_state(browser, tmp_path_factory):
    """Authenticate as Admin once and cache auth_state.json."""
    storage_path = os.path.join(ROOT, "test_data", "auth_state.json")
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    _wait_until_server_healthy(page)

    login_page = LoginPage(page)
    success = login_page.login(role="Admin")
    if success:
        context.storage_state(path=storage_path)
        log.info(f"Saved authenticated session state to {storage_path}")
    else:
        log.warning("Initial login failed; tests will authenticate per-test")

    context.close()
    return storage_path if os.path.exists(storage_path) else None


@pytest.fixture(scope="function")
def authenticated_page(browser, session_storage_state):
    """Provides a Playwright page already authenticated via storage state."""
    kwargs = {"viewport": {"width": 1920, "height": 1080}}
    if session_storage_state and os.path.exists(session_storage_state):
        kwargs["storage_state"] = session_storage_state

    context = browser.new_context(**kwargs)
    page = context.new_page()

    # If storage state was invalid, fallback to direct login
    if not session_storage_state or not os.path.exists(session_storage_state):
        login_page = LoginPage(page)
        login_page.login(role="Admin")

    yield page
    context.close()


@pytest.fixture(scope="function")
def unauthenticated_page(browser):
    """Provides a fresh, unauthenticated Playwright page for login tests."""
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    yield page
    context.close()


_session_stats = {"passed": 0, "failed": 0, "skipped": 0, "start_time": datetime.now(), "failed_tests": []}
_html_reporter = PytestReporterPlugin(suite_title="Consultant Management")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        tc_id = "UNKNOWN"
        match = re.search(r"TC_CONSULTANT_[A-Z0-9_]+", item.name)
        if match:
            tc_id = match.group(0)

        # Get test page if available
        page = item.funcargs.get("authenticated_page") or item.funcargs.get("unauthenticated_page")
        scr = None

        if report.passed:
            _session_stats["passed"] += 1
            if page:
                scr = os.path.join(SCREENSHOTS, f"PASS_{tc_id}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                try:
                    page.screenshot(path=scr)
                except Exception:
                    scr = None
            remarks = "Execution Passed Successfully"
            update_test_result(tc_id, "PASS", remarks, report.duration)
            _html_reporter.record_test(
                item=item,
                report=report,
                status="PASS",
                remarks=remarks,
                auto_id=build_automation_id(tc_id),
                screenshot_path=scr,
                duration=report.duration,
            )

        elif report.failed:
            _session_stats["failed"] += 1
            fail_label = tc_id if tc_id != "UNKNOWN" else item.name
            _session_stats["failed_tests"].append(fail_label)
            if page:
                scr = os.path.join(SCREENSHOTS, f"FAIL_{tc_id}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                try:
                    page.screenshot(path=scr)
                except Exception:
                    scr = None
            err_msg = str(report.longrepr) if report.longrepr else "Test Assertion / Execution Failure"
            remarks = err_msg[:250]
            update_test_result(tc_id, "FAIL", remarks, report.duration)
            _html_reporter.record_test(
                item=item,
                report=report,
                status="FAIL",
                remarks=remarks,
                auto_id=build_automation_id(tc_id),
                screenshot_path=scr,
                duration=report.duration,
            )

        elif report.skipped:
            _session_stats["skipped"] += 1
            remarks = "Scenario Skipped / Non-UI Flow"
            update_test_result(tc_id, "SKIP", remarks, report.duration)
            _html_reporter.record_test(
                item=item,
                report=report,
                status="SKIPPED",
                remarks=remarks,
                auto_id=build_automation_id(tc_id),
                duration=report.duration,
            )


def pytest_sessionfinish(session, exitstatus):
    if getattr(session.config.option, "collectonly", False):
        return
    dur = (datetime.now() - _session_stats["start_time"]).total_seconds()
    log.info(
        f"Session Complete: Passed={_session_stats['passed']}, Failed={_session_stats['failed']}, Skipped={_session_stats['skipped']} in {dur:.1f}s"
    )
    dur_str = f"{int(dur // 60)}m {int(dur % 60)}s"
    total = _session_stats["passed"] + _session_stats["failed"] + _session_stats["skipped"]

    report_path = None
    if total > 0:
        try:
            report_path = _html_reporter.finalize_report(filename_prefix="consultant_mgmt")
        except Exception as exc:
            log.warning(f"Could not finalize HTML report: {exc}")

    show_summary_popup(
        total=total,
        passed=_session_stats["passed"],
        failed=_session_stats["failed"],
        skipped=_session_stats["skipped"],
        duration_str=dur_str,
        failed_tests=_session_stats["failed_tests"],
        suite_title="Consultant Management",
        report_path=report_path,
    )
