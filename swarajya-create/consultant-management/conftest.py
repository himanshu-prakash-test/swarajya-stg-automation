import logging
import os
import sys
from datetime import datetime

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
if _MODULE_DIR not in sys.path:
    sys.path.insert(0, _MODULE_DIR)

import pytest
from playwright.sync_api import sync_playwright

from pages.login_page import LoginPage
from pages.tfa_page import TfaPage

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
SCREENSHOTS_DIR = os.path.join(_MODULE_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def pytest_addoption(parser):
    try:
        parser.addoption("--headed", action="store_true", default=False, help="Run browser in headed mode")
    except ValueError:
        pass
    try:
        parser.addoption("--headless", action="store_true", default=False, help="Run browser in headless mode")
    except ValueError:
        pass


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def is_headless_mode(request):
    if request.config.getoption("--headed"):
        return False
    if request.config.getoption("--headless"):
        return True
    return True


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance, is_headless_mode):
    br = playwright_instance.chromium.launch(headless=is_headless_mode)
    yield br
    br.close()


@pytest.fixture
def context(browser):
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        ignore_https_errors=True,
    )
    yield ctx
    ctx.close()


@pytest.fixture
def page(context):
    pg = context.new_page()
    yield pg
    pg.close()


@pytest.fixture
def login_page(page, base_url):
    return LoginPage(page, base_url)


@pytest.fixture
def tfa_page(page, base_url):
    return TfaPage(page, base_url)
