"""
Pytest configuration and fixtures for Create Invoice Management Automation.

Strictly adheres to framework standards:
- Dynamic test data and test case loading from shared Excel workbooks
- Session storage & authentication state caching for instant test starts
- 1-to-1 screenshot capture for every test execution
- Live updates to Swarajya-test-cases.xlsx [Sheet: createinvoice-mgmt]
- HTML report generation with full suite statistics
- macOS, Linux & Windows native summary popups (guarded for CI/CD)
"""

import os
import re
import sys
import logging
from datetime import datetime
from typing import List, Optional
import pytest

# Ensure module, create root, and workspace root are in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
CREATE_DIR = os.path.dirname(MODULE_DIR)
ROOT_DIR = os.path.dirname(CREATE_DIR)
for path_dir in (MODULE_DIR, CREATE_DIR, ROOT_DIR):
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

from playwright.sync_api import sync_playwright
from shared.pages.login_page import LoginPage
from shared.pages.tfa_page import TfaPage
from shared.utils.paths import AUTH_STATE_FILE
from invoice_utils.excel_reader import (
    get_base_url,
    read_credentials,
    update_test_result,
    build_automation_id,
    SHEET_NAME,
)
from shared.reporter.hooks import PytestReporterPlugin
from shared.reporter.models import TestCaseResult
from shared.utils.popup import show_summary_popup

log = logging.getLogger("invoice_conftest")

BASE_URL = os.environ.get("SWARAJYA_BASE_URL") or os.environ.get("BASE_URL") or get_base_url(sheet_name=SHEET_NAME)

SCREENSHOTS_DIR = os.path.join(MODULE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


# --- CLI options ---

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
            parser.addoption("--headed", action="store_true", default=False, help="Run browser in headed mode.")
        except ValueError:
            pass
    if "--headless" not in existing:
        try:
            parser.addoption("--headless", action="store_true", default=False, help="Run browser headless.")
        except ValueError:
            pass
    if "--slowmo" not in existing:
        try:
            parser.addoption("--slowmo", action="store", default=0, type=int, help="Slowdown Playwright actions (ms).")
        except ValueError:
            pass


def _is_headless(config) -> bool:
    """Determine headless state based on CLI flags, CI environment, and defaults."""
    if config.getoption("--headed", default=False):
        return False
    if config.getoption("--headless", default=False):
        return True
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return True
    env_val = os.environ.get("HEADLESS")
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes")
    return True


@pytest.fixture(scope="session")
def headed(request) -> bool:
    return not _is_headless(request.config)


@pytest.fixture(scope="session")
def slowmo(request) -> int:
    try:
        return request.config.getoption("--slowmo") or 0
    except Exception:
        return 0


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance, headed, slowmo):
    is_ci = bool(os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"))
    effective_headless = True if is_ci else not headed

    launch_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
    ]
    if effective_headless:
        launch_args.extend(["--headless=new", "--mute-audio"])
    elif sys.platform.startswith("win"):
        launch_args.append("--start-maximized")

    log.info(f"Launching Chromium browser (headless={effective_headless}, slow_mo={slowmo})")
    br = playwright_instance.chromium.launch(
        headless=effective_headless,
        slow_mo=slowmo,
        args=launch_args,
    )
    yield br
    br.close()


def _wait_until_server_healthy(page, max_retries: int = 5, delay_s: int = 3) -> bool:
    """Poll staging URL dynamically to confirm server is healthy and not 503."""
    import time
    url = f"{BASE_URL.rstrip('/')}/"
    for attempt in range(1, max_retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            content = page.content().lower()
            if "service unavailable" not in content and "503" not in content:
                return True
            log.warning(f"Attempt {attempt}: Staging server returned 503. Retrying in {delay_s}s...")
        except Exception as exc:
            log.warning(f"Attempt {attempt}: Health check exception: {exc}. Retrying in {delay_s}s...")
        time.sleep(delay_s)
    return False


def _is_valid_auth_state(path: Optional[str]) -> bool:
    """Validate that auth_state.json exists and contains actual auth tokens or session storage."""
    if not path or not os.path.exists(path):
        return False
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
    """Authenticate as Admin once dynamically and cache auth_state.json."""
    storage_path = AUTH_STATE_FILE
    if _is_valid_auth_state(storage_path):
        log.info(f"Using existing valid auth state: {storage_path}")
        return storage_path

    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    _wait_until_server_healthy(page)

    login_page = LoginPage(page, BASE_URL)
    creds = read_credentials(role="Admin", sheet_name=SHEET_NAME)
    success = login_page.login(
        employee_id=creds["employee_id"],
        password=creds["password"],
        auth_code=creds.get("auth_code") or os.environ.get("SWARAJYA_AUTH_CODE") or os.environ.get("AUTH_CODE"),
    )
    if success:
        page.wait_for_timeout(1000)
        login_page.save_auth_state(path=storage_path)
        log.info(f"Saved authenticated session state to {storage_path}")
    else:
        log.warning("Initial login failed; tests will authenticate per-test")

    context.close()
    return storage_path if _is_valid_auth_state(storage_path) else None


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def admin_creds():
    return read_credentials(role="Admin", sheet_name=SHEET_NAME)


@pytest.fixture(scope="function")
def logged_in_page(browser, session_storage_state, admin_creds):
    """Provides an authenticated Playwright page fixture with auto-login fallback."""
    storage = session_storage_state if _is_valid_auth_state(session_storage_state) else None
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        storage_state=storage,
    )
    page = context.new_page()
    page.set_default_timeout(15000)
    page.set_default_navigation_timeout(30000)

    # Pre-inject saved sessionStorage
    LoginPage.inject_session_storage(page, storage_path=storage)

    # Health check
    _wait_until_server_healthy(page, max_retries=3, delay_s=2)

    # Verify session is alive
    try:
        page.goto(f"{BASE_URL}/invoice", timeout=12000, wait_until="domcontentloaded")
        if "login" in page.url.lower() or "tfa" in page.url.lower():
            log.info("Session expired or redirected to login, re-authenticating...")
            login = LoginPage(page, BASE_URL)
            login.login(
                employee_id=admin_creds["employee_id"],
                password=admin_creds["password"],
                auth_code=admin_creds.get("auth_code") or os.environ.get("SWARAJYA_AUTH_CODE") or os.environ.get("AUTH_CODE"),
            )
            login.save_auth_state(path=storage)
    except Exception:
        login = LoginPage(page, BASE_URL)
        login.login(
            employee_id=admin_creds["employee_id"],
            password=admin_creds["password"],
            auth_code=admin_creds.get("auth_code") or os.environ.get("SWARAJYA_AUTH_CODE") or os.environ.get("AUTH_CODE"),
        )

    yield page
    context.close()


@pytest.fixture(scope="function")
def context(logged_in_page):
    """Yield context of logged_in_page for tests requiring context control (e.g. offline emulation)."""
    return logged_in_page.context


@pytest.fixture(scope="function")
def page(logged_in_page):
    """Alias page fixture to logged_in_page."""
    return logged_in_page


@pytest.fixture(scope="function")
def authenticated_page(logged_in_page):
    """Alias authenticated_page to logged_in_page."""
    return logged_in_page


# --- Session Metrics & HTML Reporting Plugin ---

_results = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
_failed_tests: List[str] = []
_recorded_nodes = set()
_start_time = None
_html_reporter = PytestReporterPlugin(suite_title="Create Invoice Management")


def _clean_old_screenshots(directory: str, max_age_hours: int = 24, max_files: int = 60):
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
    global _start_time
    _start_time = datetime.now()
    _clean_old_screenshots(SCREENSHOTS_DIR, max_age_hours=24, max_files=60)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" or (report.when == "setup" and (report.skipped or report.failed)):
        if getattr(report, "nodeid", "") in _recorded_nodes:
            return
        _recorded_nodes.add(report.nodeid)

        tc_id = "UNKNOWN"
        marker = item.get_closest_marker("tc_id")
        if marker and marker.args:
            tc_id = str(marker.args[0]).strip()
        else:
            match = re.search(r"(TC_[A-Za-z0-9_]+)", item.name) or re.search(r"(TC_[A-Za-z0-9_]+)", report.nodeid)
            if match:
                tc_id = match.group(1).strip()

        duration = getattr(report, "duration", 0.0)

        if hasattr(report, "wasxfail"):
            status = "FAIL"
            reason = getattr(report, "wasxfail", "") or "Application defect detected"
            remarks = f"Defect: {reason}"[:240]
            _results["failed"] += 1
            _failed_tests.append(f"{tc_id}: {remarks}")
        elif report.passed:
            status = "PASS"
            _results["passed"] += 1
            is_pos = "pos" in report.nodeid.lower() or "positive" in report.nodeid.lower()
            remarks = (
                "Validation successful: Invoice operation executed and verified."
                if is_pos
                else "Validation successful: Form rejected invalid input and prevented submission."
            )
        elif report.failed:
            status = "FAIL"
            _results["failed"] += 1
            remarks = str(getattr(report, "longreprtext", ""))[:500] or str(report.longrepr)[:500]
            _failed_tests.append(f"{tc_id} ({item.name})")
        else:
            status = "SKIPPED"
            _results["skipped"] += 1
            remarks = "Execution Skipped"
        _results["total"] += 1

        shot_path = None
        pg = item.funcargs.get("page") or item.funcargs.get("logged_in_page") or item.funcargs.get("authenticated_page")
        if pg and (status in ("PASS", "FAIL") or hasattr(report, "wasxfail")):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shot_prefix = "DEFECT" if hasattr(report, "wasxfail") else status
            shot_filename = f"{shot_prefix}_{tc_id}__{ts}.png"
            shot_path = os.path.join(SCREENSHOTS_DIR, shot_filename)
            try:
                pg.screenshot(path=shot_path, timeout=5000)
                log.info("Captured 1-to-1 test screenshot (%s): %s", shot_prefix, shot_filename)
            except Exception as exc:
                log.warning("Screenshot capture failed for %s: %s", tc_id, exc)
                shot_path = None

        if tc_id != "UNKNOWN":
            try:
                update_test_result(
                    tc_id=tc_id,
                    status=status,
                    remarks=remarks,
                    auto_id=build_automation_id(tc_id),
                    sheet_name=SHEET_NAME,
                )
            except Exception as exc:
                log.warning("Excel update failed for %s: %s", tc_id, exc)

        _html_reporter.record_test(
            item=item,
            report=report,
            status=status,
            remarks=remarks,
            auto_id=build_automation_id(tc_id),
            screenshot_path=shot_path,
            duration=duration,
        )


def pytest_sessionfinish(session, exitstatus):
    if getattr(session.config.option, "collectonly", False):
        return

    duration = datetime.now() - _start_time if _start_time else None
    dur_str = str(duration).split(".")[0] if duration else "N/A"

    passed = _results["passed"]
    failed = _results["failed"]
    skipped = _results["skipped"]
    total = _results["total"]

    status = "ALL PASSED" if failed == 0 and total > 0 else f"{failed} FAILED" if failed > 0 else "SESSION COMPLETE"

    lines = [
        f"{'=' * 50}",
        f"  SWARAJYA CREATE INVOICE MANAGEMENT — {status}",
        f"{'=' * 50}",
        f"  Total: {total:<4} | Passed: {passed:<4} | Failed: {failed:<4} | Skipped: {skipped}",
        f"  Duration: {dur_str}",
    ]
    if _failed_tests:
        lines.append("  Failed / observed defects:")
        for ft in _failed_tests[:10]:
            lines.append(f"    - {ft}")
    lines.append(f"{'=' * 50}")

    try:
        print("\n" + "\n".join(lines) + "\n")
    except UnicodeEncodeError:
        print("\n" + "\n".join(lines).encode("ascii", "replace").decode() + "\n")

    report_path = None
    if total > 0:
        try:
            report_path = _html_reporter.finalize_report(filename_prefix="create_invoice_management")
        except Exception as exc:
            log.warning("Could not finalize HTML report: %s", exc)

    # Display execution summary popup
    try:
        show_summary_popup(
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            duration_str=str(dur_str),
            failed_tests=_failed_tests,
            suite_title="Create Invoice Management",
            report_path=report_path,
        )
    except Exception as exc:
        log.warning("Could not display summary popup: %s", exc)
