import logging
import os
import sys
import re
from datetime import datetime
from typing import Optional

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

_WORKSPACE_ROOT = os.path.dirname(os.path.dirname(_PROJECT_ROOT))
if _WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, _WORKSPACE_ROOT)

import pytest
from playwright.sync_api import sync_playwright

from emp_update_pages.login_page import LoginPage
from emp_update_utils.excel_reader import build_automation_id, read_credentials, update_test_result
from shared.utils.popup import show_summary_popup

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
def session_storage_state(browser, tmp_path_factory):
    """Authenticate as HR once and cache auth_state.json."""
    storage_path = os.path.join(ROOT, "test_data", "auth_state.json")
    if _is_valid_auth_state(storage_path):
        return storage_path

    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    _wait_until_server_healthy(page)

    login_page = LoginPage(page)
    success = login_page.login(role="HR")
    if success:
        page.wait_for_timeout(1000)
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
        login_page.login(role="HR")
        storage_path = os.path.join(ROOT, "test_data", "auth_state.json")
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

_session_stats = {"passed": 0, "failed": 0, "skipped": 0, "start_time": datetime.now(), "failed_tests": []}


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    tc_id = "UNKNOWN"
    m = re.search(r"TC_(?:POS|NEG)_UPD_\d+", item.name)
    if m:
        tc_id = m.group(0)
    elif hasattr(item, "callspec"):
        for param_val in item.callspec.params.values():
            if isinstance(param_val, dict) and "Test Case ID" in param_val:
                tc_id = param_val["Test Case ID"]
                break

    page = item.funcargs.get("authenticated_page") or item.funcargs.get("unauthenticated_page") or item.funcargs.get("page")

    if report.passed:
        _session_stats["passed"] += 1
        if page:
            scr = os.path.join(SCREENSHOTS, f"PASS_{tc_id}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            try:
                page.screenshot(path=scr)
            except Exception:
                pass
        update_test_result(tc_id, "PASS", "Execution Passed Successfully", report.duration)

    elif report.failed:
        _session_stats["failed"] += 1
        fail_label = tc_id if tc_id != "UNKNOWN" else item.name
        _session_stats["failed_tests"].append(fail_label)
        if page:
            scr = os.path.join(SCREENSHOTS, f"FAIL_{tc_id}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            try:
                page.screenshot(path=scr)
            except Exception:
                pass
        err_msg = str(report.longrepr) if report.longrepr else "Test Assertion / Execution Failure"
        update_test_result(tc_id, "FAIL", err_msg[:250], report.duration)

    elif report.skipped:
        _session_stats["skipped"] += 1
        update_test_result(tc_id, "SKIPPED", "Scenario Skipped / Non-UI Flow", report.duration)


def pytest_sessionfinish(session, exitstatus):
    if getattr(session.config.option, "collectonly", False):
        return

    dur = (datetime.now() - _session_stats["start_time"]).total_seconds()
    log.info(
        f"Session Complete: Passed={_session_stats['passed']}, Failed={_session_stats['failed']}, Skipped={_session_stats['skipped']} in {dur:.1f}s"
    )
    dur_str = f"{int(dur // 60)}m {int(dur % 60)}s"
    total = _session_stats["passed"] + _session_stats["failed"] + _session_stats["skipped"]
    show_summary_popup(
        total=total,
        passed=_session_stats["passed"],
        failed=_session_stats["failed"],
        skipped=_session_stats["skipped"],
        duration_str=dur_str,
        failed_tests=_session_stats["failed_tests"],
        suite_title="Employee Update Management",
    )
