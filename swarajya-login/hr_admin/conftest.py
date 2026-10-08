"""
conftest.py — Fixtures and hooks for HR & Admin Login Module.

Provides browser lifecycle, page objects, credential fixtures,
automatic screenshots on failure, Excel result updates, and a
summary popup after the run.
"""

import os
import sys
import re
import logging
from datetime import datetime

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # swarajya-login/hr_admin
_LOGIN_ROOT = os.path.dirname(_PROJECT_ROOT)               # swarajya-login
_WORKSPACE_ROOT = os.path.dirname(_LOGIN_ROOT)             # workspace root
for _p in (_PROJECT_ROOT, _LOGIN_ROOT, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from playwright.sync_api import sync_playwright

from common.pages.login_page import LoginPage
from common.pages.tfa_page import TfaPage
from common.utils.excel_reader import get_base_url, read_credentials, update_test_result
from shared.utils.popup import show_summary_popup
from shared.reporter import PytestReporterPlugin, TestCaseResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("hr_admin_conftest")

SHEET_NAME = "loginhr_admin"
BASE_URL = os.environ.get("SWARAJYA_BASE_URL") or get_base_url(SHEET_NAME)
SCREENSHOTS_DIR = os.path.join(_PROJECT_ROOT, "screenshots")
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
            parser.addoption("--headed", action="store_true", default=False,
                             help="Run browser in headed mode.")
        except ValueError:
            pass
    if "--headless" not in existing:
        try:
            parser.addoption("--headless", action="store_true", default=False,
                             help="Run browser headless (default).")
        except ValueError:
            pass


def _is_headless(config) -> bool:
    try:
        if config.getoption("--headed"):
            return False
        if config.getoption("--headless"):
            return True
    except (ValueError, AttributeError):
        pass
    env = os.environ.get("HEADLESS")
    if env is not None:
        return env.lower() in ("true", "1", "yes")
    return True


# --- Browser lifecycle ---

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance, request):
    headless = _is_headless(request.config)
    log.info("Launching Chromium (headless=%s)", headless)
    args = (["--start-maximized"] if not headless
            else ["--no-sandbox", "--disable-dev-shm-usage",
                  "--disable-gpu", "--window-size=1920,1080"])
    b = playwright_instance.chromium.launch(headless=headless, slow_mo=0, args=args)
    yield b
    b.close()


@pytest.fixture(scope="function")
def context(browser, request):
    headless = _is_headless(request.config)
    ctx = (browser.new_context(viewport={"width": 1920, "height": 1080})
           if headless else browser.new_context(no_viewport=True))
    yield ctx
    ctx.close()


# --- Dynamic Server Health & Page Lifecycle ---

@pytest.fixture(scope="session", autouse=True)
def server_health_check(playwright_instance, base_url):
    """
    Dynamically verify target server responsiveness once per test session
    using Playwright's native API request context.
    Avoids redundant checks, static sleeps, or blocking loops on individual tests.
    """
    timeout_ms = int(os.environ.get("SERVER_HEALTH_TIMEOUT_MS", 10_000))
    try:
        req_ctx = playwright_instance.request.new_context()
        resp = req_ctx.get(base_url, timeout=timeout_ms)
        if resp.status in (200, 301, 302):
            log.info("Target server is healthy (%s returned %d)", base_url, resp.status)
        else:
            log.warning("Target server returned HTTP %d for %s", resp.status, base_url)
    except Exception as exc:
        log.warning("Server check encountered %s for %s; test suite will rely on page dynamic retry", exc, base_url)


@pytest.fixture(scope="function")
def page(context):
    default_timeout = int(os.environ.get("PLAYWRIGHT_DEFAULT_TIMEOUT_MS", 15_000))
    pg = context.new_page()
    pg.set_default_timeout(default_timeout)
    yield pg
    pg.close()


# --- Page-object fixtures ---

@pytest.fixture
def login_page(page):
    lp = LoginPage(page, BASE_URL)
    lp.navigate()
    return lp


@pytest.fixture
def tfa_page(page):
    return TfaPage(page, BASE_URL)


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


# --- Credential fixtures ---

@pytest.fixture
def admin_credentials():
    return read_credentials("Admin")


@pytest.fixture
def hr_credentials():
    return read_credentials("HR")


# --- 1-to-1 Screenshot for Every Test Case ---

@pytest.fixture(autouse=True)
def capture_screenshot_after_test(request, page):
    yield
    status = "PASS"
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        status = "FAIL"
    elif getattr(request.node, "rep_setup", None) and request.node.rep_setup.failed:
        status = "FAIL"

    tc_id = None
    m = re.search(r"TC_[A-Z]+_\d+|TC_[A-Z]+", request.node.name)
    if m:
        tc_id = m.group(0)

    label = tc_id if tc_id else re.sub(r"[^\w\-]", "_", request.node.name)[:50]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shot_filename = f"{status}_{label}__{ts}.png"
    path = os.path.join(SCREENSHOTS_DIR, shot_filename)
    try:
        page.screenshot(path=path, full_page=True)
        log.info("Captured 1-to-1 test screenshot (%s): %s", status, shot_filename)
    except Exception as exc:
        log.warning("Screenshot failed for %s: %s", request.node.name, exc)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# --- Custom markers ---

def pytest_configure(config):
    config.addinivalue_line("markers", "tc_id(id): Link test to Excel TC ID")
    config.addinivalue_line("markers", "role(name): Role under test")


# --- Result tracking + popup ---

_results = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
_failed_tests = []
_start_time = None
_html_reporter = PytestReporterPlugin(suite_title="HR & Admin Login Authentication")


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


def pytest_runtest_logreport(report):
    if report.when == "call":
        _results["total"] += 1
        if report.passed:
            _results["passed"] += 1
        elif report.failed:
            _results["failed"] += 1
            _failed_tests.append(report.nodeid.split("::")[-1])
    elif report.when == "setup" and report.skipped:
        _results["total"] += 1
        _results["skipped"] += 1

    if report.when != "call" and not (report.when == "setup" and report.skipped):
        return

    tc_id = None
    match = re.search(r"(TC_\w+)", report.nodeid)
    if match:
        tc_id = match.group(1)
    if not tc_id:
        return

    if report.passed:
        result, remarks = "PASS", ""
    elif report.failed:
        result = "FAIL"
        remarks = str(getattr(report, "longreprtext", ""))[:500]
    elif report.skipped:
        result = "SKIPPED"
        remarks = (getattr(report, "wasxfail", "")
                   or (str(report.longrepr[2])[:500]
                       if report.longrepr and len(report.longrepr) > 2 else ""))
    else:
        return

    shot_path = None
    if os.path.exists(SCREENSHOTS_DIR):
        for f in sorted(os.listdir(SCREENSHOTS_DIR), reverse=True):
            if f.lower().endswith(".png") and (tc_id in f or report.nodeid.split("::")[-1] in f):
                shot_path = os.path.join(SCREENSHOTS_DIR, f)
                break

    try:
        update_test_result(tc_id, result, remarks)
    except Exception as exc:
        log.warning("Excel update failed for %s: %s", tc_id, exc)

    test_res = TestCaseResult(
        nodeid=report.nodeid,
        name=tc_id,
        tc_id=tc_id,
        status=result,
        duration=getattr(report, "duration", 0.0),
        module_name="HR & Admin Login",
        description="HR & Admin Login Authentication test verification",
        error_message=remarks if result == "FAIL" else "",
        stacktrace=str(report.longrepr) if getattr(report, "longrepr", None) else "",
        screenshot_path=shot_path,
        remarks=remarks,
        auto_id=f"AUT_{tc_id}",
    )
    _html_reporter.reporter.add_result(test_res)


def pytest_sessionfinish(session, exitstatus):
    duration = datetime.now() - _start_time if _start_time else None
    dur_str = str(duration).split(".")[0] if duration else "N/A"

    passed = _results["passed"]
    failed = _results["failed"]
    skipped = _results["skipped"]
    total = _results["total"]

    status = "ALL PASSED" if failed == 0 else f"{failed} FAILED"

    lines = [
        f"{'=' * 44}",
        f"  SWARAJYA HR & ADMIN LOGIN — {status}",
        f"{'=' * 44}",
        f"  Total: {total}  |  Passed: {passed}  |  Failed: {failed}  |  Skipped: {skipped}",
        f"  Duration: {dur_str}",
    ]
    if _failed_tests:
        lines.append("  Failed:")
        for ft in _failed_tests[:10]:
            lines.append(f"    - {ft}")
    lines.append(f"{'=' * 44}")

    try:
        print("\n" + "\n".join(lines) + "\n")
    except UnicodeEncodeError:
        print("\n" + "\n".join(lines).encode("ascii", "replace").decode() + "\n")

    if getattr(session.config.option, "collectonly", False):
        return

    report_path = None
    if total > 0:
        try:
            report_path = _html_reporter.finalize_report(filename_prefix="login_hr_admin")
        except Exception as exc:
            log.warning(f"Could not finalize HTML report: {exc}")

    try:
        show_summary_popup(
            passed=passed,
            failed=failed,
            skipped=skipped,
            total=total,
            duration_str=str(dur_str),
            failed_tests=_failed_tests,
            title="SWARAJYA HR & ADMIN LOGIN",
            report_path=report_path,
        )
    except Exception:
        pass
