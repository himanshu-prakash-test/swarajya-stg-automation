"""
conftest.py — fixtures and hooks for the Swarajya login test suite.

Provides browser lifecycle, page objects, credential fixtures,
automatic screenshots on failure, Excel result updates, and a
tkinter popup summary after the run.
"""
import os
import sys
import re
import logging
from datetime import datetime

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_LOGIN_ROOT = os.path.dirname(_PROJECT_ROOT)
_WORKSPACE_ROOT = os.path.dirname(_LOGIN_ROOT)
for _p in (_PROJECT_ROOT, _LOGIN_ROOT, _WORKSPACE_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pytest
from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.tfa_page import TfaPage
from utils.excel_reader import read_credentials, update_test_result
from shared.utils.popup import show_summary_popup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("conftest")

BASE_URL = os.environ.get(
    "SWARAJYA_BASE_URL",
    "https://swarajya-stg.corecotechnologies.com",
)
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


# --- CLI options ---

def pytest_addoption(parser):
    try:
        parser.addoption("--headed", action="store_true", default=False,
                         help="Run browser in headed mode.")
    except ValueError:
        pass
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
def page(context):
    _wait_until_server_healthy()
    pg = context.new_page()
    pg.set_default_timeout(30_000)
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


@pytest.fixture
def base_url():
    return BASE_URL


# --- Credential fixtures ---

@pytest.fixture
def employee_credentials():
    return read_credentials("Employee")


@pytest.fixture
def manager_credentials():
    return read_credentials("Manager")


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
    global _start_time
    _start_time = datetime.now()
    _clean_old_screenshots(SCREENSHOTS_DIR, max_age_hours=24, max_files=60)


def pytest_runtest_logreport(report):
    # count results
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

    # update Excel
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

    try:
        update_test_result(tc_id, result, remarks)
    except Exception as exc:
        log.warning("Excel update failed for %s: %s", tc_id, exc)


def pytest_sessionfinish(session, exitstatus):
    """Print console summary and show a popup with test results."""
    duration = datetime.now() - _start_time if _start_time else None
    dur_str = str(duration).split(".")[0] if duration else "N/A"

    passed = _results["passed"]
    failed = _results["failed"]
    skipped = _results["skipped"]
    total = _results["total"]

    status = "ALL PASSED" if failed == 0 else f"{failed} FAILED"

    lines = [
        f"{'=' * 44}",
        f"  SWARAJYA LOGIN AUTOMATION — {status}",
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

    # popup
    try:
        _show_popup(passed, failed, skipped, total, dur_str, _failed_tests)
        return
    except Exception:
        pass

    # fallback: Windows MessageBox
    try:
        import ctypes
        icon = 0x40 if failed == 0 else 0x10
        msg = (f"Total: {total}\nPassed: {passed}\nFailed: {failed}\n"
               f"Skipped: {skipped}\nDuration: {dur_str}")
        if _failed_tests:
            msg += "\n\nFailed:\n" + "\n".join(f"  - {t}" for t in _failed_tests[:5])
        ctypes.windll.user32.MessageBoxW(0, msg, f"Swarajya — {status}", icon)
    except Exception:
        pass


def _show_popup(passed, failed, skipped, total, duration, failed_tests):
    show_summary_popup(
        passed=passed,
        failed=failed,
        skipped=skipped,
        total=total,
        duration_str=str(duration),
        failed_tests=failed_tests,
        title="SWARAJYA LOGIN AUTOMATION",
    )
