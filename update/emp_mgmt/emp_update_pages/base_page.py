import time
from playwright.sync_api import Page, Locator
from emp_update_utils.logger import get_logger

log = get_logger("base_page")


class BasePage:
    def __init__(self, page: Page, base_url: str = "https://swarajya-stg.corecotechnologies.com"):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def goto(self, path: str = "/"):
        url = f"{self.base_url}{path}" if path.startswith("/") else path
        log.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        self.wait_for_dom_ready()

    def wait_for_dom_ready(self, timeout_ms: int = 15000):
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        except Exception:
            pass

    def wait_for_network_idle(self, timeout_ms: int = 10000):
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout_ms)
        except Exception:
            pass

    def click(self, selector: str, timeout_ms: int = 10000):
        self.page.locator(selector).first.wait_for(state="visible", timeout=timeout_ms)
        self.page.locator(selector).first.click()

    def fill(self, selector: str, text: str, timeout_ms: int = 10000):
        self.page.locator(selector).first.wait_for(state="visible", timeout=timeout_ms)
        self.page.locator(selector).first.fill(text)
        try:
            self.page.locator(selector).first.dispatch_event("input")
            self.page.locator(selector).first.dispatch_event("change")
        except Exception:
            pass

    def dismiss_any_tutorial_or_dialog(self):
        """Dismiss tutorial / tour popups that may overlay form controls."""
        try:
            dismiss_buttons = [
                self.page.locator("button:has-text('Skip')"),
                self.page.locator("button:has-text('Got it')"),
                self.page.locator("button:has-text('Close')"),
                self.page.locator(".introjs-skipbutton"),
                self.page.locator(".shepherd-cancel-icon"),
            ]
            for btn in dismiss_buttons:
                if btn.count() and btn.first.is_visible():
                    btn.first.click(force=True)
        except Exception:
            pass
