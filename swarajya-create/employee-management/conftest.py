import logging
import os
import re
from datetime import datetime

import pytest
from playwright.sync_api import sync_playwright

from emp_pages.login_page import LoginPage
from emp_utils.excel_reader import build_automation_id, read_credentials, update_test_result
from emp_utils.popup import show_summary_popup

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


def _headless(config) -> bool:
    try:
        return not config.getoption("--headed")
    except (ValueError, AttributeError):
        return True


def _tc_id_from_nodeid(nodeid: str):
    match = re.search(r"(TC_[A-Z]+_[A-Z]+_\d+)", nodeid)
    return match.group(1) if match else None


@pytest.fixture(scope="session")
def pw():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(pw, request):
    headless = _headless(request.config)
    log.info(f"Launching Chromium (headless={headless})")
    browser_instance = pw.chromium.launch(headless=headless, args=["--no-sandbox"])
    yield browser_instance
    browser_instance.close()


AUTH_STATE_PATH = os.path.join(ROOT, "test_data", "auth_state.json")


@pytest.fixture(scope="session")
def session_context(browser):
    """Log in once per session and save auth state for all tests."""
    creds = read_credentials("Employee")
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    log.info("Performing session-level authentication from credentials.xlsx")
    LoginPage(page).login(creds["employee_id"], creds["password"], creds["auth_code"])
    context.storage_state(path=AUTH_STATE_PATH)
    try:
        page.close()
    except Exception:
        pass
    context.close()
    yield AUTH_STATE_PATH


def _wait_until_server_healthy(timeout=60):
    import time
    import urllib.request

    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen("https://swarajya-stg.corecotechnologies.com/", timeout=4) as resp:
                if resp.status in (200, 301, 302):
                    return
        except Exception:
            time.sleep(2)


@pytest.fixture(scope="function")
def page(browser, request, session_context):
    """Use an authenticated page for Excel flows and a clean page for login tests."""
    _wait_until_server_healthy()
    is_login_test = request.node.get_closest_marker("login") is not None
    if is_login_test:
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
    else:
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, storage_state=session_context)
    page_instance = context.new_page()
    page_instance.set_default_timeout(25000)

    yield page_instance

    try:
        page_instance.close()
    except Exception:
        pass
    try:
        context.close()
    except Exception:
        pass


@pytest.fixture
def logged_in_page(page):
    return page


@pytest.fixture
def employee_creds():
    return read_credentials("Employee")


@pytest.fixture
def manager_creds():
    return read_credentials("Manager")


@pytest.fixture(autouse=True)
def _take_screenshot_after_test(request, page):
    yield
    status = "PASS"
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        status = "FAIL"
    elif getattr(request.node, "rep_setup", None) and request.node.rep_setup.failed:
        status = "FAIL"

    tc_id = None
    if hasattr(request.node, "callspec"):
        for val in request.node.callspec.params.values():
            if isinstance(val, dict) and "Test Case ID" in val:
                tc_id = val["Test Case ID"]
                break
    if not tc_id:
        m = re.search(r"TC_[A-Z]+_[A-Z]+_\d+", request.node.name)
        if m:
            tc_id = m.group(0)

    label = tc_id if tc_id else re.sub(r"[^\w\-]", "_", request.node.name)[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shot_filename = f"{status}_{label}__{timestamp}.png"
    path = os.path.join(SCREENSHOTS, shot_filename)
    try:
        page.screenshot(path=path, full_page=True)
        log.info(f"Captured 1-to-1 test screenshot ({status}): {shot_filename}")
    except Exception as exc:
        log.warning(f"Failed to capture screenshot for {request.node.name}: {exc}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_configure(config):
    for marker in [
        "tc_id(id): Excel test case ID",
        "positive: Positive employee creation test cases",
        "negative: Negative employee validation test cases",
        "login: Authentication tests",
        "employee: Employee management test cases",
    ]:
        config.addinivalue_line("markers", marker)


_metrics = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
_failures = []
_recorded_nodes = set()
_t0 = None


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


def pytest_sessionstart(session):
    global _t0
    _t0 = datetime.now()
    _clean_old_screenshots(SCREENSHOTS, max_age_hours=24, max_files=60)


def _record_excel_result(report, status: str, remark: str = ""):
    tc_id = _tc_id_from_nodeid(report.nodeid)
    if not tc_id or report.nodeid in _recorded_nodes:
        return

    _recorded_nodes.add(report.nodeid)
    _metrics["total"] += 1
    if status == "PASS":
        _metrics["passed"] += 1
    elif status == "FAIL":
        _metrics["failed"] += 1
        _failures.append(f"{tc_id}: {remark or 'failed'}")
    else:
        _metrics["skipped"] += 1
        _failures.append(f"{tc_id}: {remark or 'skipped'}")

    try:
        update_test_result(
            tc_id,
            status,
            auto_id=build_automation_id(tc_id),
            remark=remark,
        )
    except Exception as exc:
        log.warning(f"Excel update failed for {tc_id}: {exc}")


def _clean_failure_message(longrepr) -> str:
    if not longrepr:
        return "Test failed: Assertion error"
    text = str(longrepr)
    for line in reversed(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        if "AssertionError:" in line:
            return line.split("AssertionError:", 1)[1].strip()
        if line.startswith("E "):
            return line[2:].strip()
    return text.splitlines()[-1].strip()[:240]


def pytest_runtest_logreport(report):
    if report.when == "call":
        if report.passed:
            is_pos = "pos" in report.nodeid.lower()
            remark = (
                "Validation successful: Employee record created and verified in employee list."
                if is_pos
                else "Validation successful: Form rejected invalid input and prevented submission."
            )
            _record_excel_result(report, "PASS", remark)
        elif report.failed:
            message = _clean_failure_message(report.longrepr)
            _record_excel_result(report, "FAIL", message[:240])
    elif report.when == "setup":
        if report.skipped:
            _record_excel_result(report, "SKIP", "Skipped: Execution Type is API in Excel workbook")
        elif report.failed:
            message = _clean_failure_message(report.longrepr)
            _record_excel_result(report, "FAIL", message[:240])


def pytest_sessionfinish(session, exitstatus):
    elapsed = str(datetime.now() - _t0).split(".")[0] if _t0 else "?"
    passed = _metrics["passed"]
    failed = _metrics["failed"]
    skipped = _metrics["skipped"]
    total = _metrics["total"]
    tag = "ALL PASSED" if failed == 0 else f"{failed} FAILED"

    print(f"\n{'=' * 56}")
    print(f"  SWARAJYA CREATE EXCEL AUTOMATION - {tag}")
    print(f"{'=' * 56}")
    print(f"  Total : {total}   Passed : {passed}   Failed : {failed}   Skipped : {skipped}")
    print(f"  Time  : {elapsed}")
    if _failures:
        print("  Failed / skipped cases:")
        for failure in _failures[:10]:
            print(f"    - {failure}")
    print(f"{'=' * 56}\n")

    if getattr(session.config.option, "collectonly", False):
        return

    try:
        show_summary_popup(
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            duration=elapsed,
            failures=_failures,
        )
    except Exception as exc:
        log.warning(f"Popup display note: {exc}")
