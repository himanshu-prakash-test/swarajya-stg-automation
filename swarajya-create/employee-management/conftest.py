import logging
import os
import sys
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_CREATE_ROOT = os.path.dirname(_PROJECT_ROOT)
_WORKSPACE_ROOT = os.path.dirname(_CREATE_ROOT)

for _p in (_PROJECT_ROOT, _CREATE_ROOT, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from playwright.sync_api import sync_playwright

from shared.pages.login_page import LoginPage
from shared.pages.base_page import BASE_URL
from shared.utils.paths import AUTH_STATE_FILE
from shared.utils.popup import show_summary_popup
from shared.reporter import PytestReporterPlugin
from emp_utils.excel_reader import (
    build_automation_id,
    read_base_url,
    read_credentials,
    update_test_result,
    SHEET_NAME,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("emp_conftest")

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
def pw(playwright_instance):
    return playwright_instance


@pytest.fixture(scope="session")
def browser(playwright_instance, headed, slowmo):
    log.info(f"Launching Chromium browser (headless={not headed}, slow_mo={slowmo})")
    br = playwright_instance.chromium.launch(
        headless=not headed,
        slow_mo=slowmo,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    yield br
    br.close()


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
def session_storage_state(browser):
    """Authenticate using credentials from Excel createemp-mgmt banner and cache auth state."""
    storage_path = AUTH_STATE_FILE
    if _is_valid_auth_state(storage_path):
        return storage_path

    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    log.info(f"Performing session authentication from Excel [{SHEET_NAME}] banner")
    creds = read_credentials("Admin")
    login_page = LoginPage(page)
    success = login_page.login(
        employee_id=creds["employee_id"],
        password=creds["password"],
        auth_code=creds.get("auth_code"),
        role=creds.get("role", "Admin"),
        save_state_path=storage_path,
    )
    if success:
        login_page.save_auth_state(storage_path)
        log.info(f"Saved authenticated session state to {storage_path}")
    else:
        log.warning("Initial login failed; tests will authenticate per-test")

    try:
        page.close()
    except Exception:
        pass
    context.close()
    return storage_path if _is_valid_auth_state(storage_path) else None


@pytest.fixture(scope="session")
def session_context(session_storage_state):
    """Backward compatibility alias for session_storage_state."""
    return session_storage_state


@pytest.fixture(scope="function")
def authenticated_page(browser, session_storage_state):
    """Provides a Playwright page already authenticated via storage state."""
    kwargs = {"viewport": {"width": 1920, "height": 1080}}
    if session_storage_state and os.path.exists(session_storage_state):
        kwargs["storage_state"] = session_storage_state

    context = browser.new_context(**kwargs)
    page_instance = context.new_page()

    # Pre-inject saved sessionStorage
    LoginPage.inject_session_storage(page_instance)

    # Verify session is alive
    target_base = read_base_url()
    creds = read_credentials("Admin")
    try:
        page_instance.goto(f"{target_base}/default", timeout=12000, wait_until="domcontentloaded")
        if "login" in page_instance.url.lower() or "tfa" in page_instance.url.lower():
            LoginPage(page_instance).login(
                employee_id=creds["employee_id"],
                password=creds["password"],
                auth_code=creds.get("auth_code"),
                role=creds.get("role", "Admin"),
            )
    except Exception:
        LoginPage(page_instance).login(
            employee_id=creds["employee_id"],
            password=creds["password"],
            auth_code=creds.get("auth_code"),
            role=creds.get("role", "Admin"),
        )

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


@pytest.fixture(scope="function")
def unauthenticated_page(browser):
    """Provides a fresh, unauthenticated Playwright page for login flow tests."""
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
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


@pytest.fixture(scope="function")
def logged_in_page(authenticated_page):
    """Alias for authenticated_page."""
    return authenticated_page


@pytest.fixture(scope="function")
def page(request, authenticated_page, unauthenticated_page):
    """
    Intelligent page fixture: returns unauthenticated_page for login tests,
    and authenticated_page for data-driven flow tests.
    """
    if request.node.get_closest_marker("login") is not None:
        return unauthenticated_page
    return authenticated_page


@pytest.fixture
def admin_creds():
    """Dynamically read Admin credentials from Swarajya-test-data.xlsx."""
    return read_credentials("Admin")


@pytest.fixture
def employee_creds():
    """Dynamically read Employee credentials from Swarajya-test-data.xlsx."""
    return read_credentials("Employee")


@pytest.fixture
def manager_creds():
    """Dynamically read Manager credentials from Swarajya-test-data.xlsx."""
    return read_credentials("Manager")


@pytest.fixture
def base_url():
    """Dynamically read Base URL from Swarajya-test-data.xlsx."""
    return read_base_url()


def _extract_tc_id(item) -> str:
    """Extract standard test case ID from markers, params, or nodeid."""
    marker = item.get_closest_marker("tc_id")
    if marker and marker.args:
        return str(marker.args[0])
    if hasattr(item, "callspec"):
        for val in item.callspec.params.values():
            if isinstance(val, dict) and "Test Case ID" in val:
                return str(val["Test Case ID"])
    m = re.search(r"(TC_[A-Za-z0-9_]+)", item.name) or re.search(r"(TC_[A-Za-z0-9_]+)", getattr(item, "nodeid", ""))
    if m:
        return m.group(1)
    if "admin_login" in item.name:
        return "TC_EMP_AUTH_01"
    if "navigation_path" in item.name:
        return "TC_EMP_NAV_01"
    return re.sub(r"[^\w\-]", "_", item.name)[:50]


def pytest_configure(config):
    for marker in [
        "tc_id(id): Excel test case ID",
        "positive: Positive employee creation test cases",
        "negative: Negative employee validation test cases",
        "login: Authentication tests",
        "employee: Employee management test cases",
        "smoke: Core sanity smoke tests",
        "regression: Full regression test suite",
    ]:
        config.addinivalue_line("markers", marker)


_metrics = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
_failures: List[str] = []
_recorded_nodes = set()
_t0: Optional[datetime] = None
_html_reporter = PytestReporterPlugin(suite_title="Employee Management")


def _clean_old_screenshots(directory: str, max_age_hours: int = 24, max_files: int = 80):
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
    _clean_old_screenshots(SCREENSHOTS, max_age_hours=24, max_files=80)


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

    if report.when == "call" or (report.when == "setup" and (report.skipped or report.failed)):
        if report.nodeid in _recorded_nodes:
            return
        _recorded_nodes.add(report.nodeid)

        tc_id = _extract_tc_id(item) or "UNKNOWN"
        page_inst = item.funcargs.get("authenticated_page") or item.funcargs.get("page") or item.funcargs.get("unauthenticated_page")
        status = "PASS" if report.passed else "FAIL" if report.failed else "SKIPPED"
        auto_id = build_automation_id(tc_id) if tc_id != "UNKNOWN" else ""
        duration = getattr(report, "duration", 0.0)

        if status == "PASS":
            _metrics["passed"] += 1
            is_pos = "pos" in report.nodeid.lower() or "positive" in report.nodeid.lower()
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
        if page_inst and status in ("PASS", "FAIL"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shot_filename = f"{status}_{tc_id}__{ts}.png"
            shot_path = os.path.join(SCREENSHOTS, shot_filename)
            try:
                page_inst.screenshot(path=shot_path, timeout=5000)
                log.info(f"Captured test screenshot ({status}): {shot_filename}")
            except Exception as exc:
                log.warning(f"Failed to capture screenshot for {tc_id}: {exc}")
                shot_path = None

        if tc_id != "UNKNOWN":
            try:
                update_test_result(
                    tc_id=tc_id,
                    status=status,
                    remarks=remark,
                    sheet_name=SHEET_NAME,
                    duration_s=duration,
                )
            except Exception as exc:
                log.warning(f"Excel result update failed for {tc_id}: {exc}")

        _html_reporter.record_test(
            item=item,
            report=report,
            status=status,
            remarks=remark,
            auto_id=auto_id,
            screenshot_path=shot_path,
            duration=duration,
        )


def pytest_sessionfinish(session, exitstatus):
    elapsed = str(datetime.now() - _t0).split(".")[0] if _t0 else "?"
    passed = _metrics["passed"]
    failed = _metrics["failed"]
    skipped = _metrics["skipped"]
    total = _metrics["total"]
    tag = "ALL PASSED" if failed == 0 else f"{failed} FAILED"

    print(f"\n{'=' * 60}")
    print(f"  SWARAJYA EMPLOYEE CREATE EXCEL AUTOMATION - {tag}")
    print(f"{'=' * 60}")
    print(f"  Total : {total}   Passed : {passed}   Failed : {failed}   Skipped : {skipped}")
    print(f"  Time  : {elapsed}")
    if _failures:
        print("  Failed / observed defects:")
        for failure in _failures[:10]:
            print(f"    - {failure}")
    print(f"{'=' * 60}\n")

    if getattr(session.config.option, "collectonly", False):
        return

    if total == 0:
        return

    report_path = None
    try:
        report_path = _html_reporter.finalize_report(filename_prefix="employee_mgmt")
    except Exception as exc:
        log.warning(f"Could not finalize HTML report: {exc}")

    # Auto-open HTML report in system default browser if not running in CI
    if report_path and os.path.exists(report_path) and not os.environ.get("CI"):
        try:
            from shared.reporter.html_reporter import PlaywrightHTMLReporter
            PlaywrightHTMLReporter.open_in_browser(report_path)
            log.info(f"Opened HTML report in default browser: {report_path}")
        except Exception as exc:
            log.warning(f"Could not auto-open HTML report: {exc}")

    # Display styled execution summary desktop popup
    try:
        show_summary_popup(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration_str=elapsed,
            failures=_failures,
            report_path=report_path,
            suite_title="Employee Management Create",
        )
    except Exception as exc:
        log.warning(f"Popup display note: {exc}")
