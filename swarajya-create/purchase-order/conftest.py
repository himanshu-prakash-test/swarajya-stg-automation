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

from po_pages.login_page import LoginPage
from po_utils.excel_reader import build_automation_id, read_credentials, update_test_result
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
    for _ in range(max_retries):
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
def session_storage_state(browser):
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


def _extract_tc_id(item) -> str:
    """Extract standard test case ID from markers, params, or function name."""
    marker = item.get_closest_marker("tc_id")
    if marker and marker.args:
        return str(marker.args[0])
    if hasattr(item, "callspec"):
        for val in item.callspec.params.values():
            if isinstance(val, dict) and "Test Case ID" in val:
                return str(val["Test Case ID"])
    match = re.search(r"TC_PO_[A-Z0-9_]+|TC_[A-Z0-9_]+", item.name)
    if match:
        return match.group(0)
    if "admin_login" in item.name:
        return "TC_PO_AUTH_01"
    if "navigation_path" in item.name:
        return "TC_PO_NAV_01"
    return re.sub(r"[^\w\-]", "_", item.name)[:50]


_session_stats = {"passed": 0, "failed": 0, "skipped": 0, "start_time": datetime.now(), "failed_tests": []}
_html_reporter = PytestReporterPlugin(suite_title="Purchase Order Management")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook executed around each test lifecycle phase.
    Visual evidence screenshot is captured strictly AFTER the test case has executed.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        tc_id = _extract_tc_id(item)
        page = item.funcargs.get("authenticated_page") or item.funcargs.get("unauthenticated_page") or item.funcargs.get("page")
        test_case_obj = item.funcargs.get("test_case", {})
        expected_res = test_case_obj.get("Expected Result", "") if isinstance(test_case_obj, dict) else ""

        from po_pages.form_executor import FormExecutor
        scr = getattr(FormExecutor, "last_custom_screenshot", None)
        FormExecutor.last_custom_screenshot = None

        if report.passed:
            _session_stats["passed"] += 1
            if not scr and page:
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=2000)
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                scr = os.path.join(SCREENSHOTS, f"PASS_{tc_id}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                try:
                    page.screenshot(path=scr, full_page=True)
                    log.info(f"Captured screenshot (PASS): {os.path.basename(scr)}")
                except Exception as exc:
                    log.warning(f"Could not capture screenshot for {tc_id}: {exc}")
                    scr = None

            remarks = f"PASS: Expected Result satisfied: {expected_res}" if expected_res else "PASS: Expected Result satisfied"
            update_test_result(tc_id, "PASS", error_message=remarks)
            try:
                _html_reporter.record_test(
                    item=item,
                    report=report,
                    status="PASS",
                    remarks=remarks,
                    auto_id=build_automation_id(tc_id),
                    screenshot_path=scr,
                    duration=report.duration,
                )
            except Exception as exc:
                log.warning(f"Failed to record result in HTML reporter: {exc}")

        elif report.failed:
            _session_stats["failed"] += 1
            err_msg = str(call.excinfo.value) if call.excinfo else "Test failed"
            _session_stats["failed_tests"].append(tc_id)
            if not scr and page:
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=2000)
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                scr = os.path.join(SCREENSHOTS, f"FAIL_{tc_id}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                try:
                    page.screenshot(path=scr, full_page=True)
                    log.info(f"Captured screenshot (FAIL): {os.path.basename(scr)}")
                except Exception as exc:
                    log.warning(f"Could not capture failure screenshot for {tc_id}: {exc}")
                    scr = None

            fail_remarks = f"FAIL: Expected Result NOT satisfied: {expected_res}. Error: {err_msg}" if expected_res else f"FAIL: {err_msg}"
            update_test_result(tc_id, "FAIL", error_message=fail_remarks)
            try:
                _html_reporter.record_test(
                    item=item,
                    report=report,
                    status="FAIL",
                    remarks=fail_remarks,
                    auto_id=build_automation_id(tc_id),
                    screenshot_path=scr,
                    duration=report.duration,
                )
            except Exception as exc:
                log.warning(f"Failed to record result in HTML reporter: {exc}")

        elif report.skipped:
            _session_stats["skipped"] += 1
            skip_msg = str(call.excinfo.value) if call.excinfo else "Test skipped"
            update_test_result(tc_id, "SKIPPED", error_message=f"SKIPPED: {skip_msg}")
            try:
                _html_reporter.record_test(
                    item=item,
                    report=report,
                    status="SKIPPED",
                    remarks=f"SKIPPED: {skip_msg}",
                    auto_id=build_automation_id(tc_id),
                    duration=report.duration,
                )
            except Exception as exc:
                log.warning(f"Failed to record result in HTML reporter: {exc}")


def pytest_sessionfinish(session, exitstatus):
    if getattr(session.config.option, "collectonly", False):
        return
    total = _session_stats["passed"] + _session_stats["failed"] + _session_stats["skipped"]
    if total == 0:
        return

    dur = (datetime.now() - _session_stats["start_time"]).total_seconds()
    dur_str = f"{int(dur // 60)}m {int(dur % 60)}s"

    report_path = None
    try:
        report_path = _html_reporter.finalize_report(filename_prefix="purchase_order")
    except Exception as exc:
        log.warning(f"Failed to generate custom HTML report: {exc}")

    tag = "ALL PASSED" if _session_stats["failed"] == 0 and total > 0 else "FAILURES OCCURRED" if _session_stats["failed"] > 0 else "SESSION COMPLETE"
    print(f"\n{'=' * 65}")
    print(f"  📊 SWARAJYA CREATE PURCHASE ORDER - {tag}")
    print(f"{'=' * 65}")
    print(f"  Total    : {total:<4} Passed : {_session_stats['passed']:<4} Failed : {_session_stats['failed']:<4} Skipped : {_session_stats['skipped']}")
    print(f"  Duration : {dur_str}")
    if _session_stats["failed_tests"]:
        print(f"  Failed Cases ({len(_session_stats['failed_tests'])}):")
        for ft in _session_stats["failed_tests"]:
            print(f"    ❌ {ft}")
    if report_path:
        print(f"  Report   : {report_path}")
    print(f"{'=' * 65}\n")

    try:
        if sys.platform == "darwin":
            import subprocess
            import threading
            import time

            def _bring_popup_to_front():
                time.sleep(0.4)
                try:
                    subprocess.run(
                        ["osascript", "-e", 'tell application "System Events" to set frontmost of (first process whose name is "python3" or name is "Python") to true'],
                        check=False,
                        capture_output=True,
                    )
                except Exception:
                    pass

            threading.Thread(target=_bring_popup_to_front, daemon=True).start()

            try:
                stat_msg = f"Passed: {_session_stats['passed']} | Failed: {_session_stats['failed']} | Duration: {dur_str}"
                subprocess.run(
                    ["osascript", "-e", f'display notification "{stat_msg}" with title "Purchase Order Management" sound name "Glass"'],
                    check=False,
                    capture_output=True,
                )
            except Exception:
                pass

        show_summary_popup(
            total=total,
            passed=_session_stats["passed"],
            failed=_session_stats["failed"],
            skipped=_session_stats["skipped"],
            duration_str=dur_str,
            failed_tests=_session_stats["failed_tests"],
            suite_title="Purchase Order Management",
            report_path=report_path,
        )
    except Exception as exc:
        log.warning(f"Could not display summary popup: {exc}")
