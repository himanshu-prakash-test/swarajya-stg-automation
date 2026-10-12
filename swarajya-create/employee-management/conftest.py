import logging
import os
import sys
import re
from datetime import datetime
from typing import Optional

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_CREATE_ROOT = os.path.dirname(_PROJECT_ROOT)
_WORKSPACE_ROOT = os.path.dirname(_CREATE_ROOT)
for _p in (_PROJECT_ROOT, _CREATE_ROOT, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from playwright.sync_api import sync_playwright

from shared.pages.login_page import LoginPage
from emp_utils.excel_reader import build_automation_id, read_credentials, update_test_result
from shared.pages.base_page import BASE_URL
from shared.utils.paths import AUTH_STATE_FILE
from shared.utils.popup import show_summary_popup
from shared.reporter import PytestReporterPlugin, TestCaseResult

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


def _headless(config) -> bool:
    if config.getoption("--headed", default=False):
        return False
    if config.getoption("--headless", default=False):
        return True
    env_val = os.environ.get("HEADLESS")
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes")
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


AUTH_STATE_PATH = AUTH_STATE_FILE


def _is_valid_auth_state(path: Optional[str]) -> bool:
    """Validate that auth_state.json exists and contains actual auth tokens or session storage."""
    if not path or not os.path.exists(path):
        return False
    # Check session storage file as well (Swarajya Angular app stores auth in sessionStorage)
    ss_file = path.replace(".json", "_session.json")
    if os.path.exists(ss_file):
        try:
            import json
            with open(ss_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data and any("token" in k.lower() or "isloggedin" in k.lower() or "currentuser" in k.lower() for k in data.keys()):
                return True
        except Exception:
            pass
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
def session_context(browser):
    """Log in once per session and save auth state for all tests."""
    if _is_valid_auth_state(AUTH_STATE_PATH):
        yield AUTH_STATE_PATH
        return

    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    log.info("Performing session-level authentication from createemp-mgmt sheet")
    login_page = LoginPage(page)
    success = login_page.login(role="Admin", sheet_name="createemp-mgmt")
    if success:
        log.info(f"Saved authenticated session state to {AUTH_STATE_PATH}")
    else:
        log.warning("Initial login failed; tests will authenticate per-test")

    try:
        page.close()
    except Exception:
        pass
    context.close()
    yield AUTH_STATE_PATH if _is_valid_auth_state(AUTH_STATE_PATH) else None


def _wait_until_server_healthy(timeout=60):
    import time
    import urllib.request

    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(f"{BASE_URL}/", timeout=4) as resp:
                if resp.status in (200, 301, 302):
                    return
        except Exception:
            time.sleep(2)


@pytest.fixture(scope="function")
def page(browser, request, session_context):
    """Use an authenticated page for Excel flows and a clean page for login tests."""
    _wait_until_server_healthy()
    is_login_test = request.node.get_closest_marker("login") is not None
    storage = session_context if _is_valid_auth_state(session_context) else None

    if is_login_test:
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page_instance = context.new_page()
    else:
        kwargs = {"viewport": {"width": 1920, "height": 1080}}
        if storage:
            kwargs["storage_state"] = storage
        context = browser.new_context(**kwargs)
        page_instance = context.new_page()
        LoginPage.inject_session_storage(page_instance)

        try:
            page_instance.goto(f"{BASE_URL}/default", timeout=12000, wait_until="domcontentloaded")
            if "login" in page_instance.url.lower() or "tfa" in page_instance.url.lower():
                LoginPage(page_instance).login(role="Admin", sheet_name="createemp-mgmt")
        except Exception:
            LoginPage(page_instance).login(role="Admin", sheet_name="createemp-mgmt")

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
_html_reporter = PytestReporterPlugin(suite_title="Employee Management")


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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" or (report.when == "setup" and report.skipped):
        if report.nodeid in _recorded_nodes:
            return
        _recorded_nodes.add(report.nodeid)

        tc_id = None
        if hasattr(item, "callspec"):
            for val in getattr(item.callspec, "params", {}).values():
                if isinstance(val, dict) and "Test Case ID" in val:
                    tc_id = val["Test Case ID"]
                    break
        if not tc_id:
            m = re.search(r"(TC_[A-Za-z0-9_]+)", item.name) or re.search(r"(TC_[A-Za-z0-9_]+)", report.nodeid)
            if m:
                tc_id = m.group(1)

        if not tc_id:
            tc_id = "UNKNOWN"

        page = item.funcargs.get("page")
        status = "PASS" if report.passed else "FAIL" if report.failed else "SKIPPED"
        auto_id = build_automation_id(tc_id) if tc_id != "UNKNOWN" else ""

        if status == "PASS":
            _metrics["passed"] += 1
            is_pos = "pos" in report.nodeid.lower()
            remark = (
                "Validation successful: Employee record created and verified in employee list."
                if is_pos
                else "Validation successful: Form rejected invalid input and prevented submission."
            )
        elif status == "FAIL":
            _metrics["failed"] += 1
            remark = _clean_failure_message(report.longrepr)
            _failures.append(f"{tc_id}: {remark}")
        else:
            _metrics["skipped"] += 1
            remark = "Skipped: Execution Type is API or non-UI in Excel workbook"
        _metrics["total"] += 1

        shot_path = None
        if page and status in ("PASS", "FAIL"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shot_filename = f"{status}_{tc_id}__{ts}.png"
            shot_path = os.path.join(SCREENSHOTS, shot_filename)
            try:
                page.screenshot(path=shot_path, timeout=5000)
                log.info(f"Captured 1-to-1 test screenshot ({status}): {shot_filename}")
            except Exception as exc:
                log.warning(f"Failed to capture screenshot for {tc_id}: {exc}")
                shot_path = None

        if tc_id != "UNKNOWN":
            try:
                update_test_result(tc_id, status, auto_id=auto_id, remark=remark)
            except Exception as exc:
                log.warning(f"Excel update failed for {tc_id}: {exc}")

        _html_reporter.record_test(
            item=item,
            report=report,
            status=status,
            remarks=remark,
            auto_id=auto_id,
            screenshot_path=shot_path,
            duration=getattr(report, "duration", 0.0),
        )


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

    report_path = None
    if total > 0:
        try:
            report_path = _html_reporter.finalize_report(filename_prefix="employee_mgmt")
        except Exception as exc:
            log.warning(f"Could not finalize HTML report: {exc}")

    try:
        show_summary_popup(
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            duration=elapsed,
            failures=_failures,
            report_path=report_path,
        )
    except Exception as exc:
        log.warning(f"Popup display note: {exc}")
