import os
from typing import Optional
from playwright.sync_api import Page
from vendor_utils.logger import get_logger

BASE_URL = os.environ.get("BASE_URL", "https://swarajya-stg.corecotechnologies.com").rstrip("/")


class BasePage:
    """Base page object providing dynamic event-driven Playwright interactions."""

    def __init__(self, page: Page):
        self.page = page
        self.base_url = BASE_URL
        self.log = get_logger(self.__class__.__name__)

    def goto(self, path: str = "/"):
        url = f"{self.base_url}/{path.lstrip('/')}"
        self.log.info(f"Opening {url}")
        for attempt in range(4):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                if "service unavailable" in self.page.content().lower() or "503" in self.page.content().lower():
                    self.page.wait_for_timeout(3000)
                    continue
                break
            except Exception:
                self.page.wait_for_timeout(2000)
        self.wait_for_dom_ready(timeout=5000)
        self._dismiss_tutorial()

    def wait_for_dom_ready(self, timeout: int = 5000):
        """Dynamically wait for document readyState to be interactive or complete."""
        try:
            self.page.wait_for_function(
                "() => document.readyState === 'interactive' || document.readyState === 'complete'",
                timeout=timeout,
            )
        except Exception:
            pass

    def _dismiss_tutorial(self):
        """Dismiss guided-tour overlays dynamically if present."""
        for _ in range(3):
            skip = self.page.locator("button:has-text('Skip Intro'), button:has-text('Skip'), .introjs-skipbutton")
            if skip.count() and skip.first.is_visible():
                try:
                    skip.first.click()
                    skip.first.wait_for(state="hidden", timeout=2000)
                except Exception:
                    pass
                return

    def click(self, selector: str, timeout: int = 8000):
        el = self.page.locator(selector).first
        el.wait_for(state="visible", timeout=timeout)
        el.click()

    def fill(self, selector: str, value: str, timeout: int = 8000):
        el = self.page.locator(selector).first
        el.wait_for(state="visible", timeout=timeout)
        el.fill(str(value))

    def is_visible(self, selector: str, timeout: int = 3000) -> bool:
        try:
            self.page.locator(selector).first.wait_for(
                state="visible", timeout=timeout
            )
            return True
        except Exception:
            return False

    def wait_for_hidden(self, selector: str, timeout: int = 5000) -> bool:
        try:
            self.page.locator(selector).first.wait_for(
                state="hidden", timeout=timeout
            )
            return True
        except Exception:
            return False

    def wait_for_url_contains(self, fragment: str, timeout: int = 15000) -> bool:
        try:
            self.page.wait_for_url(lambda u: fragment.lower() in u.lower(), timeout=timeout)
            return True
        except Exception:
            return False

    def text(self, selector: str) -> str:
        return self.page.locator(selector).first.inner_text().strip()

    def get_toast(self, timeout: int = 4000) -> str:
        """Retrieve dynamic snackbar or toast notification text."""
        toast_sel = "simple-snack-bar, .mat-mdc-snack-bar-container, .mat-snack-bar-container, .toast, [role='alert']"
        try:
            el = self.page.locator(toast_sel).first
            el.wait_for(state="visible", timeout=timeout)
            return el.inner_text().strip()
        except Exception:
            return ""
