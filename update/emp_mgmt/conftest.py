"""
Conftest for Employee Management Update Automation.
Provides Playwright browser, context, page fixtures, credentials, and result reporting.
"""

import os
import sys
import logging
from datetime import datetime
import openpyxl
import pytest
from playwright.sync_api import sync_playwright

# Ensure project root and update/emp_mgmt are in sys.path
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(MODULE_DIR))
LOGIN_DIR = os.path.join(ROOT_DIR, "swarajya-login", "swarajya-automation")
for p in (MODULE_DIR, ROOT_DIR, LOGIN_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from shared.utils.popup import show_desktop_popup
except ImportError:
    show_desktop_popup = None

from update.emp_mgmt.employee_workbook import update_employee_result

logger = logging.getLogger("update.emp_mgmt.conftest")

_start_time = datetime.now()
BASE_URL = os.environ.get("SWARAJYA_BASE_URL", "https://swarajya-stg.corecotechnologies.com")
CREDENTIALS_FILE = os.path.join(MODULE_DIR, "test_data", "credentials.xlsx")
SCREENSHOTS_DIR = os.path.join(MODULE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

RESULT_SUMMARY = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "failed_tests": [],
}


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


def is_headless(config):
    if config.getoption("--headed", default=False):
        return False
    if config.getoption("--headless", default=False):
        return True
    env_val = os.environ.get("HEADLESS")
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes")
    return True


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance, request):
    headless = is_headless(request.config)
    slowmo = 0
    try:
        slowmo = request.config.getoption("--slowmo") or 0
    except (ValueError, AttributeError):
        pass

    launch_args = []
    if not headless:
        launch_args.append("--start-maximized")
    else:
        launch_args.extend([
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
        ])

    browser = playwright_instance.chromium.launch(
        headless=headless,
        slow_mo=slowmo,
        args=launch_args,
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser, request):
    headless = is_headless(request.config)
    if headless:
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    else:
        ctx = browser.new_context(no_viewport=True)
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context):
    pg = context.new_page()
    pg.set_default_timeout(10_000)
    yield pg
    pg.close()


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


def _read_credentials(role="HR"):
    if not os.path.exists(CREDENTIALS_FILE):
        return {"employee_id": "332", "password": "test@1234", "auth_code": "111111"}
    wb = openpyxl.load_workbook(CREDENTIALS_FILE, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    if not rows or len(rows) < 2:
        return {"employee_id": "332", "password": "test@1234", "auth_code": "111111"}
    headers = [str(h or "").strip().lower() for h in rows[0]]
    role_idx = headers.index("role") if "role" in headers else 0
    id_idx = next((i for i, h in enumerate(headers) if "id" in h), 1)
    pwd_idx = next((i for i, h in enumerate(headers) if "pass" in h), 2)
    code_idx = next((i for i, h in enumerate(headers) if "code" in h), 3)

    target_role = role.strip().upper()
    fallback_row = None
    for r in rows[1:]:
        if not r or not any(r):
            continue
        if fallback_row is None:
            fallback_row = r
        if str(r[role_idx] or "").strip().upper() == target_role:
            return {
                "role": str(r[role_idx] or ""),
                "employee_id": str(r[id_idx] or "").strip(),
                "password": str(r[pwd_idx] or "").strip(),
                "auth_code": str(r[code_idx] or "").strip(),
            }
    if fallback_row:
        return {
            "role": str(fallback_row[role_idx] or ""),
            "employee_id": str(fallback_row[id_idx] or "").strip(),
            "password": str(fallback_row[pwd_idx] or "").strip(),
            "auth_code": str(fallback_row[code_idx] or "").strip(),
        }
    return {"employee_id": "332", "password": "test@1234", "auth_code": "111111"}


@pytest.fixture
def employee_credentials():
    role = os.environ.get("SWARAJYA_ROLE", "HR")
    return _read_credentials(role)


@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(request, page):
    yield
    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = request.node.name.replace("[", "_").replace("]", "").replace("/", "_")
        path = os.path.join(SCREENSHOTS_DIR, f"{name}_{timestamp}.png")
        try:
            page.screenshot(path=path, full_page=True)
            logger.info("Screenshot saved: %s", path)
        except Exception as exc:
            logger.warning("Screenshot failed: %s", exc)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def _find_tc_id(nodeid):
    import re
    match = re.search(r"(TC_[A-Z]+_[A-Z]+_\d+)", nodeid)
    return match.group(1) if match else None


def pytest_runtest_logreport(report):
    if report.when != "call":
        return

    RESULT_SUMMARY["total"] += 1
    if report.passed:
        RESULT_SUMMARY["passed"] += 1
    elif report.failed:
        RESULT_SUMMARY["failed"] += 1
        RESULT_SUMMARY["failed_tests"].append(report.nodeid)
    elif report.skipped:
        RESULT_SUMMARY["skipped"] += 1

    tc_id = _find_tc_id(report.nodeid)
    if not tc_id:
        return

    if report.passed:
        result = "PASS"
        remarks = "Automation completed successfully."
    elif report.failed:
        result = "FAIL"
        remarks = str(getattr(report, "longreprtext", ""))[:1000]
    elif report.skipped:
        result = "SKIPPED"
        remarks = str(getattr(report, "longreprtext", ""))[:1000]
    else:
        return

    try:
        update_employee_result(tc_id, result, remarks)
    except Exception as exc:
        logger.warning("Could not update Excel for %s: %s", tc_id, exc)


def pytest_sessionfinish(session, exitstatus):
    duration = datetime.now() - _start_time if _start_time else None
    dur_str = str(duration).split(".")[0] if duration else "N/A"
    RESULT_SUMMARY["duration"] = dur_str

    passed = RESULT_SUMMARY["passed"]
    failed = RESULT_SUMMARY["failed"]
    skipped = RESULT_SUMMARY["skipped"]
    total = RESULT_SUMMARY["total"]
    failed_tests = RESULT_SUMMARY["failed_tests"]

    status = "ALL PASSED" if failed == 0 else f"{failed} FAILED"

    lines = [
        f"{'=' * 56}",
        f"  SWARAJYA EMPLOYEE UPDATE AUTOMATION - {status}",
        f"{'=' * 56}",
        f"  Total : {total}   Passed : {passed}   Failed : {failed}   Skipped : {skipped}",
        f"  Time  : {dur_str}",
        f"{'=' * 56}",
    ]
    if failed_tests:
        lines.append("  Failed Tests:")
        for ft in failed_tests[:10]:
            lines.append(f"    - {ft}")
        lines.append(f"{'=' * 56}")

    try:
        print("\n" + "\n".join(lines) + "\n")
    except UnicodeEncodeError:
        print("\n" + "\n".join(lines).encode("ascii", "replace").decode() + "\n")

    if not getattr(session.config.option, "collectonly", False) and not is_headless(session.config):
        if show_desktop_popup:
            show_desktop_popup(
                title=os.environ.get("SWARAJYA_POPUP_TITLE", "Swarajya Employee Update - Results"),
                total=total,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration=dur_str,
                failed_tests=failed_tests,
            )
