import logging
import os
import sys
import re
from datetime import datetime

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import pytest
from playwright.sync_api import sync_playwright

from vendor_pages.login_page import LoginPage
from vendor_utils.excel_reader import build_automation_id, read_credentials, update_test_result
from vendor_utils.popup import show_summary_popup

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
        parser.addoption("--headed", action="store_true", default=False, help="Run browser in headed mode")
    if "--slowmo" not in existing:
        parser.addoption("--slowmo", action="store", default=0, type=int, help="Slowdown Playwright actions (ms)")


@pytest.fixture(scope="session")
def headed(request) -> bool:
    return request.config.getoption("--headed")


@pytest.fixture(scope="session")
def slowmo(request) -> int:
    return request.config.getoption("--slowmo")


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
    """Authenticate as Manager/Admin once and cache auth_state.json."""
    storage_path = os.path.join(ROOT, "test_data", "auth_state.json")
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    _wait_until_server_healthy(page)

    login_page = LoginPage(page)
    success = login_page.login(role="Manager")
    if success:
        context.storage_state(path=storage_path)
        log.info(f"Saved authenticated session state to {storage_path}")
    else:
        log.warning("Initial login failed; tests will authenticate per-test")

    context.close()
    return storage_path if os.path.exists(storage_path) else None


@pytest.fixture(scope="function")
def authenticated_page(browser, session_storage_state):
    """Provides an authenticated Playwright page fixture."""
    storage = session_storage_state if session_storage_state and os.path.exists(session_storage_state) else None
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        storage_state=storage,
    )
    page = context.new_page()
    page.set_default_timeout(15000)
    page.set_default_navigation_timeout(30000)

    # Health check
    _wait_until_server_healthy(page, max_retries=3, delay_s=2)

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

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    # Extract test case ID
    tc_id = None
    if hasattr(item, "callspec"):
        for param_val in item.callspec.params.values():
            if isinstance(param_val, dict) and "Test Case ID" in param_val:
                tc_id = param_val["Test Case ID"]
                break
    if not tc_id:
        m = re.search(r"TC_VENDOR_[A-Z]+_\d+", item.name)
        if m:
            tc_id = m.group(0)

    status = "PASS" if report.passed else "FAIL" if report.failed else "SKIPPED"
    remarks = ""
    if report.failed and call.excinfo:
        remarks = str(call.excinfo.value)[:200].replace("\n", " ")

    # Update Excel
    if tc_id:
        sheet = getattr(item, "_sheet_name", None)
        update_test_result(tc_id, status=status, remarks=remarks, sheet_name=sheet)

    # Save 1-to-1 screenshot for every test case
    page = item.funcargs.get("authenticated_page") or item.funcargs.get("unauthenticated_page") or item.funcargs.get("page")
    if page:
        try:
            label = tc_id if tc_id else re.sub(r"[^\w\-]", "_", item.name)[:50]
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shot_filename = f"{status}_{label}__{ts}.png"
            shot_path = os.path.join(SCREENSHOTS, shot_filename)
            page.screenshot(path=shot_path, full_page=True)
            log.info(f"Captured 1-to-1 test screenshot ({status}): {shot_filename}")
        except Exception as exc:
            log.warning(f"Could not capture screenshot for {item.name}: {exc}")


def _clean_old_screenshots(directory: str, max_age_hours: int = 24, max_files: int = 60):
    """Automatically purge screenshots older than max_age_hours or if count exceeds max_files."""
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


# ----------------- Summary Popup Hook -----------------

_SESSION_START = None


def pytest_sessionstart(session):
    global _SESSION_START
    _SESSION_START = datetime.now()
    _clean_old_screenshots(SCREENSHOTS, max_age_hours=24, max_files=60)


def pytest_sessionfinish(session, exitstatus):
    if getattr(session.config.option, "collectonly", False):
        return

    duration = datetime.now() - _SESSION_START if _SESSION_START else None
    dur_str = str(duration).split(".")[0] if duration else "0:00:00"

    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    passed = len(reporter.stats.get("passed", [])) if reporter else 0
    failed = len(reporter.stats.get("failed", [])) if reporter else 0
    skipped = len(reporter.stats.get("skipped", [])) if reporter else 0
    total = passed + failed + skipped

    banner_title = "ALL PASSED" if failed == 0 and total > 0 else "FAILURES OCCURRED" if failed > 0 else "SESSION COMPLETE"
    print("\n" + "=" * 56)
    print(f"  SWARAJYA VENDOR AUTOMATION - {banner_title}")
    print("=" * 56)
    print(f"  Total : {total:<4} Passed : {passed:<4} Failed : {failed:<4} Skipped : {skipped}")
    print(f"  Time  : {dur_str}")
    print("=" * 56 + "\n")

    show_summary_popup(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration_str=dur_str,
    )
