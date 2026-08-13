import logging
import os
from datetime import datetime

import pytest
from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.tfa_page import TfaPage
from utils.excel_reader import update_test_result

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("conftest")

BASE_URL = os.environ.get(
    "SWARAJYA_BASE_URL",
    "https://swarajya-stg.corecotechnologies.com",
)
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


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
        r"(TC_(?:ADMIN|HR)_\d{3})",
        nodeid,
    )
    return match.group(1) if match else None


def pytest_runtest_logreport(report):
    if report.when != "call":
        return

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
