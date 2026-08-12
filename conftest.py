"""
conftest.py - Pytest fixtures for the Swarajya Automation Framework.

Provides:
- Browser lifecycle management (Playwright)
- Page and context fixtures (fresh per test)
- LoginPage and TfaPage POM fixtures
- Automatic screenshot capture on test failure
- Test result tracking in the Excel test case file
- Popup-based test execution summary
"""
import os
import logging
from datetime import datetime

import pytest
from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.tfa_page import TfaPage
from utils.excel_reader import read_credentials, update_test_result

# ── Logging Configuration ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("conftest")

# ── Constants ──
BASE_URL = os.environ.get(
    "SWARAJYA_BASE_URL",
    "https://swarajya-stg.corecotechnologies.com",
)
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")

# Ensure output directories exist
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def pytest_addoption(parser):
    """Add custom command-line options for browser launch mode."""
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in headed (visible GUI) mode. Default is headless.",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode (default).",
    )


def is_headless(config) -> bool:
    """
    Determine whether browser should run in headless mode.
    Priority:
    1. CLI flag --headed -> False (headed)
    2. CLI flag --headless -> True (headless)
    3. Environment variable HEADLESS -> bool
    4. Default -> True (headless)
    """
    try:
        if config.getoption("--headed"):
            return False
        if config.getoption("--headless"):
            return True
    except (ValueError, AttributeError):
        pass

    env_val = os.environ.get("HEADLESS")
    if env_val is not None:
        return env_val.lower() in ("true", "1", "yes")

    return True


@pytest.fixture(scope="session")
def playwright_instance():
    """Start Playwright once per test session."""
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance, request):
    """Launch a Chromium browser once per test session."""
    headless_mode = is_headless(request.config)
    logger.info("Launching Chromium browser (headless=%s)", headless_mode)

    launch_args = []
    if not headless_mode:
        launch_args.append("--start-maximized")
    else:
        launch_args.extend([
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1920,1080",
        ])

    browser_inst = playwright_instance.chromium.launch(
        headless=headless_mode,
        slow_mo=0,
        args=launch_args,
    )
    yield browser_inst
    logger.info("Closing browser")
    browser_inst.close()


@pytest.fixture(scope="function")
def context(browser, request):
    """Create a fresh browser context for each test (isolated cookies/storage)."""
    headless_mode = is_headless(request.config)
    if headless_mode:
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
    else:
        ctx = browser.new_context(no_viewport=True)
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context):
    """Create a new page (tab) for each test."""
    pg = context.new_page()
    pg.set_default_timeout(10_000)
    yield pg
    pg.close()


# ═══════════════════════════════════════════════════════════════════
# PAGE OBJECT FIXTURES
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture
def login_page(page):
    """
    Provides a LoginPage instance pre-navigated to the login URL.
    Ready for immediate interaction.
    """
    lp = LoginPage(page, BASE_URL)
    lp.navigate()
    return lp


@pytest.fixture
def tfa_page(page):
    """
    Provides a TfaPage instance (no navigation — used after LoginPage login).
    """
    return TfaPage(page, BASE_URL)


@pytest.fixture
def base_url():
    """Provides the base URL for direct navigation tests."""
    return BASE_URL


# ═══════════════════════════════════════════════════════════════════
# CREDENTIAL FIXTURES
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture
def employee_credentials():
    """Read Employee role credentials from credentials.xlsx."""
    return read_credentials("Employee")


@pytest.fixture
def manager_credentials():
    """Read Manager role credentials from credentials.xlsx."""
    return read_credentials("Manager")


# ═══════════════════════════════════════════════════════════════════
# SCREENSHOT ON FAILURE (autouse)
# ═══════════════════════════════════════════════════════════════════

@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(request, page):
    """
    Automatically capture a screenshot if a test fails.
    Screenshots are saved under screenshots/ with the test name and timestamp.
    """
    yield
    # After test execution
    if request.node.rep_call and request.node.rep_call.failed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = request.node.name.replace("[", "_").replace("]", "").replace("/", "_")
        filename = f"{test_name}_{timestamp}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        try:
            page.screenshot(path=filepath, full_page=True)
            logger.info("Screenshot saved: %s", filepath)
        except Exception as e:
            logger.warning("Failed to capture screenshot: %s", e)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test result on the item for use by the screenshot fixture."""
    import pluggy
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)




# ═══════════════════════════════════════════════════════════════════
# HTML REPORT CUSTOMIZATION
# ═══════════════════════════════════════════════════════════════════

def pytest_configure(config):
    """Register custom markers used by the suite."""
    config.addinivalue_line("markers", "tc_id(id): Link test to Excel Test Case ID")
    config.addinivalue_line("markers", "role(name): Specify the role being tested")


# ═══════════════════════════════════════════════════════════════════
# POP-UP NOTIFICATION AFTER TEST SUITE
# ═══════════════════════════════════════════════════════════════════

# Collect results as tests run
_test_results = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0, "total": 0}
_failed_tests = []
_start_time = None


def pytest_sessionstart(session):
    """Record the session start time."""
    global _start_time
    _start_time = datetime.now()


def pytest_runtest_logreport(report):
    """Track test results for the popup summary."""
    if report.when == "call":
        _test_results["total"] += 1
        if report.passed:
            _test_results["passed"] += 1
        elif report.failed:
            _test_results["failed"] += 1
            _failed_tests.append(report.nodeid.split("::")[-1])
    elif report.when == "setup" and report.skipped:
        _test_results["total"] += 1
        _test_results["skipped"] += 1
    elif report.when == "call" and report.failed:
        _test_results["errors"] += 1

    # ── Also update Excel (existing logic below) ──
    if report.when != "call" and not (report.when == "setup" and report.skipped):
        return

    tc_id = None
    remarks = ""
    if hasattr(report, "keywords"):
        for marker_name in report.keywords:
            if marker_name.startswith("TC_"):
                tc_id = marker_name
                break
    if not tc_id:
        import re
        match = re.search(r"(TC_\w+)", report.nodeid)
        if match:
            tc_id = match.group(1)
    if not tc_id:
        return

    if report.passed:
        result = "PASS"
    elif report.failed:
        result = "FAIL"
        remarks = str(report.longreprtext)[:500] if hasattr(report, "longreprtext") else ""
    elif report.skipped:
        result = "SKIPPED"
        if hasattr(report, "wasxfail"):
            remarks = report.wasxfail
        elif report.longrepr and len(report.longrepr) > 2:
            remarks = str(report.longrepr[2])[:500]

    try:
        update_test_result(tc_id, result, remarks)
    except Exception as e:
        logger.warning("Failed to update Excel result for %s: %s", tc_id, e)


def pytest_sessionfinish(session, exitstatus):
    """Show a pop-up dialog summarising test results after the suite completes."""
    duration = datetime.now() - _start_time if _start_time else None
    duration_str = str(duration).split(".")[0] if duration else "N/A"

    passed = _test_results["passed"]
    failed = _test_results["failed"]
    skipped = _test_results["skipped"]
    total = _test_results["total"]

    # Determine overall status
    if failed == 0:
        status_icon = "✅"
        status_text = "ALL TESTS PASSED"
    else:
        status_icon = "❌"
        status_text = f"{failed} TEST(S) FAILED"

    # Build summary text
    summary_lines = [
        f"{'═' * 44}",
        f"  SWARAJYA LOGIN AUTOMATION — RESULTS",
        f"{'═' * 44}",
        f"",
        f"  {status_icon}  {status_text}",
        f"",
        f"  Total Tests  :  {total}",
        f"  Passed       :  {passed}  ✅",
        f"  Failed       :  {failed}  {'❌' if failed else ''}",
        f"  Skipped      :  {skipped}  {'⏭️' if skipped else ''}",
        f"  Duration     :  {duration_str}",
        f"",
    ]

    if _failed_tests:
        summary_lines.append(f"  ── Failed Tests ──")
        for ft in _failed_tests[:10]:
            summary_lines.append(f"    ✗  {ft}")
        if len(_failed_tests) > 10:
            summary_lines.append(f"    ... and {len(_failed_tests) - 10} more")
        summary_lines.append("")

    if False:
        summary_lines.append(f"  📊 HTML Report: reports/report.html")

    summary_lines.append(f"{'═' * 44}")
    summary_text = "\n".join(summary_lines)

    # Print to console as well, with a Windows-safe fallback for unicode output.
    try:
        print("\n" + summary_text + "\n")
    except UnicodeEncodeError:
        safe_summary_text = summary_text.encode("ascii", errors="replace").decode("ascii")
        print("\n" + safe_summary_text + "\n")

    # ── Try tkinter pop-up first (richer UI) ──
    try:
        _show_tkinter_popup(
            passed, failed, skipped, total, duration_str,
            _failed_tests,
        )
        return
    except Exception as tk_err:
        logger.debug("tkinter popup failed: %s, falling back to ctypes", tk_err)

    # ── Fallback: Windows native MessageBox via ctypes ──
    try:
        import ctypes
        MB_OK = 0x00000000
        MB_ICONINFORMATION = 0x00000040
        MB_ICONERROR = 0x00000010
        icon = MB_ICONINFORMATION if failed == 0 else MB_ICONERROR

        msg = (
            f"Swarajya Login Automation Results\n"
            f"{'─' * 36}\n\n"
            f"Total:    {total}\n"
            f"Passed:   {passed}\n"
            f"Failed:   {failed}\n"
            f"Skipped:  {skipped}\n"
            f"Duration: {duration_str}\n"
        )
        if _failed_tests:
            msg += f"\nFailed:\n"
            for ft in _failed_tests[:5]:
                msg += f"  • {ft}\n"

        ctypes.windll.user32.MessageBoxW(
            0, msg, f"{'✅ ALL PASSED' if failed == 0 else '❌ FAILURES DETECTED'}", icon | MB_OK
        )
    except Exception as e:
        logger.warning("Could not show pop-up notification: %s", e)


def _show_tkinter_popup(passed, failed, skipped, total, duration, failed_tests):
    """Show a styled tkinter pop-up dialog with test results."""
    import tkinter as tk
    from tkinter import font as tkfont

    report_path = None

    root = tk.Tk()
    root.withdraw()  # Hide the root window

    popup = tk.Toplevel(root)
    popup.title("Swarajya Automation — Test Results")
    popup.geometry("520x480")
    popup.resizable(False, False)
    popup.configure(bg="#1a1a2e")

    # Center on screen
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - 260
    y = (popup.winfo_screenheight() // 2) - 240
    popup.geometry(f"+{x}+{y}")

    # Keep on top
    popup.attributes("-topmost", True)

    # ── Title bar ──
    title_bg = "#16213e"
    title_frame = tk.Frame(popup, bg=title_bg, pady=12)
    title_frame.pack(fill="x")

    title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
    tk.Label(
        title_frame, text="🏗️  SWARAJYA LOGIN AUTOMATION",
        font=title_font, fg="#e0e0e0", bg=title_bg,
    ).pack()

    # ── Status banner ──
    if failed == 0:
        banner_bg = "#0f9b58"
        banner_text = "✅  ALL TESTS PASSED"
    else:
        banner_bg = "#d32f2f"
        banner_text = f"❌  {failed} TEST(S) FAILED"

    banner_frame = tk.Frame(popup, bg=banner_bg, pady=10)
    banner_frame.pack(fill="x")
    banner_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
    tk.Label(
        banner_frame, text=banner_text,
        font=banner_font, fg="white", bg=banner_bg,
    ).pack()

    # ── Stats grid ──
    stats_frame = tk.Frame(popup, bg="#1a1a2e", pady=15, padx=20)
    stats_frame.pack(fill="x")

    stat_font = tkfont.Font(family="Consolas", size=12)
    label_font = tkfont.Font(family="Segoe UI", size=11)

    stats = [
        ("Total Tests", str(total), "#b0bec5"),
        ("Passed", str(passed), "#4caf50"),
        ("Failed", str(failed), "#f44336" if failed else "#b0bec5"),
        ("Skipped", str(skipped), "#ff9800" if skipped else "#b0bec5"),
        ("Duration", duration, "#64b5f6"),
    ]

    for i, (label, value, color) in enumerate(stats):
        tk.Label(
            stats_frame, text=f"  {label}", font=label_font,
            fg="#b0bec5", bg="#1a1a2e", anchor="w", width=14,
        ).grid(row=i, column=0, sticky="w", pady=2)

        tk.Label(
            stats_frame, text=":  ", font=label_font,
            fg="#666", bg="#1a1a2e",
        ).grid(row=i, column=1, pady=2)

        tk.Label(
            stats_frame, text=value, font=stat_font,
            fg=color, bg="#1a1a2e", anchor="w",
        ).grid(row=i, column=2, sticky="w", pady=2)

    # ── Failed tests list ──
    if failed_tests:
        fail_frame = tk.Frame(popup, bg="#1a1a2e", padx=20)
        fail_frame.pack(fill="x")

        tk.Label(
            fail_frame, text="── Failed Tests ──",
            font=tkfont.Font(family="Segoe UI", size=10, weight="bold"),
            fg="#f44336", bg="#1a1a2e",
        ).pack(anchor="w", pady=(5, 3))

        fail_list_font = tkfont.Font(family="Consolas", size=9)
        for ft in failed_tests[:8]:
            display_name = ft[:55] + "…" if len(ft) > 55 else ft
            tk.Label(
                fail_frame, text=f"  ✗  {display_name}",
                font=fail_list_font, fg="#ef9a9a", bg="#1a1a2e", anchor="w",
            ).pack(anchor="w")

        if len(failed_tests) > 8:
            tk.Label(
                fail_frame, text=f"     … and {len(failed_tests) - 8} more",
                font=fail_list_font, fg="#999", bg="#1a1a2e", anchor="w",
            ).pack(anchor="w")

    # ── Report link ──
    if False:
        link_frame = tk.Frame(popup, bg="#1a1a2e", pady=8)
        link_frame.pack(fill="x")

        def open_report():
            os.startfile(report_path)

        report_btn = tk.Button(
            link_frame, text="📊  Open HTML Report",
            font=tkfont.Font(family="Segoe UI", size=10),
            fg="white", bg="#1565c0", activebackground="#1976d2",
            activeforeground="white", relief="flat", cursor="hand2",
            padx=15, pady=5, command=open_report,
        )
        report_btn.pack(pady=5)

    # ── Close button ──
    btn_frame = tk.Frame(popup, bg="#1a1a2e", pady=10)
    btn_frame.pack(fill="x", side="bottom")

    close_btn = tk.Button(
        btn_frame, text="Close",
        font=tkfont.Font(family="Segoe UI", size=10),
        fg="white", bg="#424242", activebackground="#616161",
        activeforeground="white", relief="flat", cursor="hand2",
        padx=30, pady=5,
        command=lambda: (popup.destroy(), root.destroy()),
    )
    close_btn.pack()

    # Auto-close after 60 seconds
    popup.after(60000, lambda: (popup.destroy(), root.destroy()))

    popup.protocol("WM_DELETE_WINDOW", lambda: (popup.destroy(), root.destroy()))
    popup.mainloop()
