import logging
import os
import re
import shutil
import sys
from datetime import datetime
from typing import Optional

_MODULE_ROOT = os.path.dirname(os.path.abspath(__file__))
_UPDATE_ROOT = os.path.dirname(_MODULE_ROOT)
_WORKSPACE_ROOT = os.path.dirname(_UPDATE_ROOT)

for _p in (_MODULE_ROOT, _UPDATE_ROOT, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from playwright.sync_api import sync_playwright
from shared.reporter import PytestReporterPlugin
from shared.utils.popup import show_summary_popup

from customer_update_pages.login_page import LoginPage
from customer_update_utils.excel_reader import build_automation_id, read_credentials, update_test_result

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("customer_conftest")

SCREENSHOTS_DIR = os.path.join(_MODULE_ROOT, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

_session_stats = {"passed": 0, "failed": 0, "skipped": 0, "start_time": datetime.now(), "failed_tests": []}
_html_reporter = PytestReporterPlugin(suite_title="Customer Update Management")


def pytest_addoption(parser):
    """Add CLI flags for headed mode and slow motion."""
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
            parser.addoption("--headed", action="store_true", default=False, help="Run browser in visible headed mode")
        except ValueError:
            pass
    if "--headless" not in existing:
        try:
            parser.addoption("--headless", action="store_true", default=False, help="Run browser headless")
        except ValueError:
            pass
    if "--slowmo" not in existing:
        try:
            parser.addoption("--slowmo", action="store", default=0, type=int, help="Slow down Playwright actions (ms)")
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
    br = playwright_instance.chromium.launch(
        headless=not headed,
        slow_mo=slowmo,
        args=["--start-maximized", "--disable-dev-shm-usage"],
    )
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


def _is_valid_auth_state(path: Optional[str]) -> bool:
    if not path or not os.path.exists(path):
        return False
    try:
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for origin in data.get("origins", []):
            for item in origin.get("localStorage", []):
                if item.get("name") in ("token", "isLoggedIn") and item.get("value"):
                    return True
    except Exception:
        return False
    return False


@pytest.fixture(scope="session")
def session_storage_state(browser):
    """Authenticate as Admin once and cache auth_state.json for fast session reuse."""
    storage_path = os.path.join(_MODULE_ROOT, "test_data", "auth_state.json")
    fallback_auth = os.path.join(_WORKSPACE_ROOT, "swarajya-create", "customer-management", "test_data", "auth_state.json")

    # Reuse existing auth state if present and valid
    if not os.path.exists(storage_path) and os.path.exists(fallback_auth):
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        try:
            shutil.copy2(fallback_auth, storage_path)
        except Exception:
            pass

    if _is_valid_auth_state(storage_path):
        return storage_path

    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    _wait_until_server_healthy(page)

    login_page = LoginPage(page)
    success = login_page.login(role="Admin")
    if success:
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        context.storage_state(path=storage_path)
        log.info(f"Saved authenticated session state to {storage_path}")
    else:
        log.warning("Initial login failed; tests will authenticate per-test")

    context.close()
    return storage_path if _is_valid_auth_state(storage_path) else None


@pytest.fixture(scope="function")
def authenticated_page(browser, session_storage_state):
    """Provides an authenticated Playwright page fixture with auto-login fallback."""
    storage = session_storage_state if _is_valid_auth_state(session_storage_state) else None
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        storage_state=storage,
    )
    page = context.new_page()
    page.set_default_timeout(15000)
    page.set_default_navigation_timeout(30000)

    _wait_until_server_healthy(page, max_retries=3, delay_s=2)

    if not storage:
        login_page = LoginPage(page)
        login_page.login(role="Admin")
        storage_path = os.path.join(_MODULE_ROOT, "test_data", "auth_state.json")
        try:
            context.storage_state(path=storage_path)
        except Exception:
            pass

    yield page
    context.close()


@pytest.fixture(scope="function")
def unauthenticated_page(browser):
    """Provides a fresh unauthenticated Playwright page fixture."""
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()
    page.set_default_timeout(15000)
    page.set_default_navigation_timeout(30000)

    _wait_until_server_healthy(page, max_retries=3, delay_s=2)

    yield page
    context.close()


# ----------------- Reporting & Screenshot Hooks -----------------

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
        if hasattr(item, "callspec"):
            for param_val in item.callspec.params.values():
                if isinstance(param_val, dict) and "Test Case ID" in param_val:
                    tc_id = param_val["Test Case ID"]
                    break
        if tc_id == "UNKNOWN":
            m = re.search(r"TC_[A-Za-z0-9_]+", item.name)
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
            except Exception:
                scr = None
        remarks = "Execution Passed Successfully"
        update_test_result(tc_id, "PASS", remarks, report.duration)
        _html_reporter.record_test(
            item=item,
            report=report,
            status="PASS",
            remarks=remarks,
            auto_id=build_automation_id(tc_id) if tc_id != "UNKNOWN" else "",
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
            auto_id=build_automation_id(tc_id) if tc_id != "UNKNOWN" else "",
            screenshot_path=scr,
            duration=report.duration,
        )

    elif report.skipped:
        _session_stats["skipped"] += 1
        remarks = "Scenario Skipped"
        update_test_result(tc_id, "SKIPPED", remarks, report.duration)
        _html_reporter.record_test(
            item=item,
            report=report,
            status="SKIPPED",
            remarks=remarks,
            auto_id=build_automation_id(tc_id) if tc_id != "UNKNOWN" else "",
            duration=report.duration,
        )


def pytest_sessionfinish(session, exitstatus):
    """Generate HTML report and display desktop summary popup dialog."""
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
            report_path = _html_reporter.finalize_report(filename_prefix="customer_update")
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
            suite_title="Customer Update Management",
            report_path=report_path,
        )
    except Exception as exc:
        log.warning(f"Could not display summary popup: {exc}")
