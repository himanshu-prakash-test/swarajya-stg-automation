import logging
import os
import sys
from datetime import datetime

import pytest
from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.tfa_page import TfaPage
from utils.excel_reader import update_test_result, read_credentials

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("conftest")

_start_time = datetime.now()

BASE_URL = os.environ.get(
    "SWARAJYA_BASE_URL",
    "https://swarajya-stg.corecotechnologies.com",
)
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

RESULT_SUMMARY = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "failed_tests": [],
}


def _show_test_results_popup(summary):
    if os.environ.get("PYTEST_NO_POPUP") == "1":
        return
    if not os.environ.get("DISPLAY") and sys.platform != "darwin":
        return

    try:
        import tkinter as tk
    except Exception:
        return

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    win = tk.Toplevel(root)
    popup_title = os.environ.get("SWARAJYA_POPUP_TITLE", "Swarajya Automation - Results")
    win.title(popup_title)
    win.configure(bg="#101d2b")
    win.geometry("820x620")
    win.minsize(820, 620)
    win.attributes("-topmost", True)

    header = tk.Frame(win, bg="#cb3b3b", height=90)
    header.pack(fill="x")
    title = tk.Label(
        header,
        text=os.environ.get("SWARAJYA_POPUP_HEADER", "SWARAJYA LOGIN AUTOMATION"),
        bg="#cb3b3b",
        fg="white",
        font=("Arial", 26, "bold"),
        pady=22,
    )
    title.pack(anchor="center")

    fail_count = summary["failed"]
    banner_text = "ALL TESTS PASSED" if fail_count == 0 else f"{fail_count} TEST(S) FAILED"
    banner_bg = "#2ca56d" if fail_count == 0 else "#cb3b3b"
    banner = tk.Label(
        win,
        text=banner_text,
        bg=banner_bg,
        fg="white",
        font=("Arial", 26, "bold"),
        pady=20,
        width=40,
    )
    banner.pack(fill="x")

    stats = tk.Frame(win, bg="#101d2b", padx=30, pady=20)
    stats.pack(fill="x")

    rows = [
        ("Total Tests", str(summary["total"])),
        ("Passed", str(summary["passed"])),
        ("Failed", str(summary["failed"])),
        ("Skipped", str(summary["skipped"])),
        ("Duration", summary.get("duration", "0:00:00")),
    ]

    for label, value in rows:
        row = tk.Frame(stats, bg="#101d2b")
        row.pack(fill="x", pady=8)
        tk.Label(row, text=label, bg="#101d2b", fg="#e5e7eb", font=("Arial", 20), width=18, anchor="w").pack(side="left")
        tk.Label(row, text=":", bg="#101d2b", fg="#e5e7eb", font=("Arial", 20), width=2).pack(side="left")
        color = "#4ade80" if label == "Passed" else "#f87171" if label == "Failed" else "#e5e7eb"
        tk.Label(row, text=value, bg="#101d2b", fg=color, font=("Arial", 20, "bold"), anchor="w").pack(side="left")

    failed_tests = summary["failed_tests"]
    failed_frame = tk.Frame(win, bg="#101d2b", padx=30, pady=10)
    failed_frame.pack(fill="both", expand=True)

    tk.Label(
        failed_frame,
        text="Failed Tests",
        bg="#101d2b",
        fg="#f87171",
        font=("Arial", 24, "bold"),
        anchor="w",
    ).pack(anchor="w", pady=(10, 5))

    failed_text = "\n".join(f"x {name}" for name in failed_tests) if failed_tests else "None"
    failed_label = tk.Label(
        failed_frame,
        text=failed_text,
        bg="#101d2b",
        fg="#fca5a5",
        justify="left",
        anchor="w",
        font=("Arial", 15),
        wraplength=720,
    )
    failed_label.pack(anchor="w", fill="x")

    button_frame = tk.Frame(win, bg="#101d2b", pady=18)
    button_frame.pack(fill="x")
    close_button = tk.Button(
        button_frame,
        text="Close",
        command=lambda: (win.destroy(), root.destroy()),
        width=18,
        height=2,
        bg="#e5e7eb",
        fg="#101d2b",
        font=("Arial", 18),
        bd=1,
    )
    close_button.pack()

    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), root.destroy()))
    auto_close_ms = os.environ.get("SWARAJYA_POPUP_AUTO_CLOSE_MS")
    if auto_close_ms:
        win.after(int(auto_close_ms), lambda: (win.destroy(), root.destroy()))
    win.wait_visibility()
    root.mainloop()


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", default=False)
    parser.addoption("--headless", action="store_true", default=False)


def is_headless(config):
    if config.getoption("--headed"):
        return False
    if config.getoption("--headless"):
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
        slow_mo=0,
        args=launch_args,
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser, request):
    headless = is_headless(request.config)

    if headless:
        ctx = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
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


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def login_page(page):
    lp = LoginPage(page, BASE_URL)
    lp.navigate()
    return lp


@pytest.fixture
def tfa_page(page):
    return TfaPage(page, BASE_URL)


@pytest.fixture
def employee_credentials():
    role = os.environ.get("SWARAJYA_ROLE", "HR")
    try:
        return read_credentials(role)
    except Exception:
        try:
            return read_credentials("Admin")
        except Exception:
            return read_credentials("Employee")


@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(request, page):
    yield

    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = (
            request.node.name
            .replace("[", "_")
            .replace("]", "")
            .replace("/", "_")
        )
        path = os.path.join(
            SCREENSHOTS_DIR,
            f"{name}_{timestamp}.png",
        )
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


def pytest_configure(config):
    for marker in [
        "smoke",
        "regression",
        "positive",
        "negative",
        "blocked",
        "security",
        "tfa",
    ]:
        config.addinivalue_line("markers", marker)


def _find_tc_id(nodeid):
    import re
    match = re.search(
        r"(TC_(?:ADMIN|HR|POS_UPD|NEG_UPD|CONSULTANT_POS|CONSULTANT_NEG)_\d+)",
        nodeid,
    )
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
        update_test_result(tc_id, result, remarks)
    except Exception as exc:
        logger.warning(
            "Could not update Excel for %s: %s",
            tc_id,
            exc,
        )


def pytest_sessionfinish(session, exitstatus):
    """Print console summary and show a popup with test results."""
    duration = datetime.now() - _start_time if _start_time else None
    dur_str = str(duration).split(".")[0] if duration else "N/A"
    RESULT_SUMMARY["duration"] = dur_str

    passed = RESULT_SUMMARY["passed"]
    failed = RESULT_SUMMARY["failed"]
    skipped = RESULT_SUMMARY["skipped"]
    total = RESULT_SUMMARY["total"]
    failed_tests = RESULT_SUMMARY["failed_tests"]

    header_title = os.environ.get("SWARAJYA_POPUP_HEADER", "SWARAJYA AUTOMATION")
    status = "ALL PASSED" if failed == 0 else f"{failed} FAILED"

    lines = [
        f"{'=' * 44}",
        f"  {header_title} — {status}",
        f"{'=' * 44}",
        f"  Total: {total}  |  Passed: {passed}  |  Failed: {failed}  |  Skipped: {skipped}",
        f"  Duration: {dur_str}",
    ]
    if failed_tests:
        lines.append("  Failed:")
        for ft in failed_tests[:10]:
            lines.append(f"    - {ft}")
    lines.append(f"{'=' * 44}")

    try:
        print("\n" + "\n".join(lines) + "\n")
    except UnicodeEncodeError:
        print("\n" + "\n".join(lines).encode("ascii", "replace").decode() + "\n")

    if not getattr(session.config.option, "collectonly", False):
        _show_test_results_popup(RESULT_SUMMARY)
