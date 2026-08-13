"""
conftest.py — fixtures and hooks for the Swarajya login test suite.

Provides browser lifecycle, page objects, credential fixtures,
automatic screenshots on failure, Excel result updates, and a
tkinter popup summary after the run.
"""
import os
import re
import logging
from datetime import datetime

import pytest
from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.tfa_page import TfaPage
from utils.excel_reader import read_credentials, update_test_result

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
    parser.addoption("--headed", action="store_true", default=False,
                     help="Run browser in headed mode.")
    parser.addoption("--headless", action="store_true", default=False,
                     help="Run browser headless (default).")


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


@pytest.fixture(scope="function")
def page(context):
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


# --- Screenshot on failure ---

@pytest.fixture(autouse=True)
def capture_screenshot_on_failure(request, page):
    yield
    if request.node.rep_call and request.node.rep_call.failed:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = request.node.name.replace("[", "_").replace("]", "").replace("/", "_")
        path = os.path.join(SCREENSHOTS_DIR, f"{name}_{ts}.png")
        try:
            page.screenshot(path=path, full_page=True)
            log.info("Screenshot: %s", path)
        except Exception as exc:
            log.warning("Screenshot failed: %s", exc)


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


def pytest_sessionstart(session):
    global _start_time
    _start_time = datetime.now()


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
    import tkinter as tk
    from tkinter import font as tkfont

    root = tk.Tk()
    root.withdraw()

    popup = tk.Toplevel(root)
    popup.title("Swarajya Automation — Results")
    popup.geometry("520x480")
    popup.resizable(False, False)
    popup.configure(bg="#1a1a2e")

    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - 260
    y = (popup.winfo_screenheight() // 2) - 240
    popup.geometry(f"+{x}+{y}")
    popup.attributes("-topmost", True)

    # title
    tf = tk.Frame(popup, bg="#16213e", pady=12)
    tf.pack(fill="x")
    tk.Label(tf, text="SWARAJYA LOGIN AUTOMATION",
             font=tkfont.Font(family="Segoe UI", size=14, weight="bold"),
             fg="#e0e0e0", bg="#16213e").pack()

    # status banner
    if failed == 0:
        bg, txt = "#0f9b58", "ALL TESTS PASSED"
    else:
        bg, txt = "#d32f2f", f"{failed} TEST(S) FAILED"
    bf = tk.Frame(popup, bg=bg, pady=10)
    bf.pack(fill="x")
    tk.Label(bf, text=txt, font=tkfont.Font(family="Segoe UI", size=13, weight="bold"),
             fg="white", bg=bg).pack()

    # stats
    sf = tk.Frame(popup, bg="#1a1a2e", pady=15, padx=20)
    sf.pack(fill="x")
    stat_font = tkfont.Font(family="Consolas", size=12)
    label_font = tkfont.Font(family="Segoe UI", size=11)

    for i, (lbl, val, clr) in enumerate([
        ("Total Tests", str(total), "#b0bec5"),
        ("Passed", str(passed), "#4caf50"),
        ("Failed", str(failed), "#f44336" if failed else "#b0bec5"),
        ("Skipped", str(skipped), "#ff9800" if skipped else "#b0bec5"),
        ("Duration", duration, "#64b5f6"),
    ]):
        tk.Label(sf, text=f"  {lbl}", font=label_font,
                 fg="#b0bec5", bg="#1a1a2e", anchor="w", width=14).grid(row=i, column=0, sticky="w", pady=2)
        tk.Label(sf, text=":  ", font=label_font,
                 fg="#666", bg="#1a1a2e").grid(row=i, column=1, pady=2)
        tk.Label(sf, text=val, font=stat_font,
                 fg=clr, bg="#1a1a2e", anchor="w").grid(row=i, column=2, sticky="w", pady=2)

    # failed list
    if failed_tests:
        ff = tk.Frame(popup, bg="#1a1a2e", padx=20)
        ff.pack(fill="x")
        tk.Label(ff, text="Failed Tests",
                 font=tkfont.Font(family="Segoe UI", size=10, weight="bold"),
                 fg="#f44336", bg="#1a1a2e").pack(anchor="w", pady=(5, 3))
        fl_font = tkfont.Font(family="Consolas", size=9)
        for ft in failed_tests[:8]:
            name = ft[:55] + "..." if len(ft) > 55 else ft
            tk.Label(ff, text=f"  x  {name}", font=fl_font,
                     fg="#ef9a9a", bg="#1a1a2e", anchor="w").pack(anchor="w")
        if len(failed_tests) > 8:
            tk.Label(ff, text=f"     ... and {len(failed_tests) - 8} more",
                     font=fl_font, fg="#999", bg="#1a1a2e", anchor="w").pack(anchor="w")

    # close button
    btf = tk.Frame(popup, bg="#1a1a2e", pady=10)
    btf.pack(fill="x", side="bottom")
    tk.Button(btf, text="Close",
              font=tkfont.Font(family="Segoe UI", size=10),
              fg="white", bg="#424242", activebackground="#616161",
              activeforeground="white", relief="flat", cursor="hand2",
              padx=30, pady=5,
              command=lambda: (popup.destroy(), root.destroy())).pack()

    popup.after(60000, lambda: (popup.destroy(), root.destroy()))
    popup.protocol("WM_DELETE_WINDOW", lambda: (popup.destroy(), root.destroy()))
    popup.mainloop()
