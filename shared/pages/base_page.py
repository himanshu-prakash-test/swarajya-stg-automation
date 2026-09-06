import os
import time
from typing import List, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from shared.utils.logger import get_logger

BASE_URL = os.environ.get(
    "SWARAJYA_BASE_URL",
    os.environ.get("BASE_URL", "https://swarajya-stg.corecotechnologies.com"),
).rstrip("/")


class BasePage:
    """
    Master Base Page Object for Swarajya Automation.
    Shared across both Create (Vendor, Employee, Consultant) and Login modules.
    Provides robust, event-driven Playwright interactions, retry mechanisms,
    dynamic DOM synchronization, and tutorial dismissals.
    """

    def __init__(self, page: Page, base_url: Optional[str] = None):
        self.page = page
        self.base_url = (base_url or BASE_URL).rstrip("/")
        self.log = get_logger(self.__class__.__name__)

    def goto(self, path: str = "/"):
        """Navigate to a path relative to base_url with resilience against 503 errors."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        self.log.info(f"Opening {url}")
        for attempt in range(1, 5):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
                content = self.page.content().lower()
                if "service unavailable" in content or "503" in content:
                    self.log.warning(f"Attempt {attempt}: Encountered Service Unavailable (503). Retrying in 3s...")
                    self.page.wait_for_timeout(3000)
                    continue
                break
            except Exception as exc:
                self.log.warning(f"Navigation attempt {attempt} failed: {exc}")
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
        """Dismiss guided-tour overlays (Intro.js / skip intro) dynamically if present."""
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
        """Wait for selector to be visible, then click."""
        el = self.page.locator(selector).first
        el.wait_for(state="visible", timeout=timeout)
        el.click()

    def fill(self, selector: str, value: str, timeout: int = 8000):
        """
        Fill form input with Playwright fill(), falling back to JavaScript evaluation
        with input/change event dispatch if the browser rejects typing into restricted types.
        """
        el = self.page.locator(selector).first
        el.wait_for(state="visible", timeout=timeout)
        try:
            el.fill(str(value))
        except Exception:
            el.evaluate(
                """(input, val) => {
                    input.value = val;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }""",
                str(value),
            )

    def is_visible(self, selector: str, timeout: int = 3000) -> bool:
        """Check if an element matching selector is visible within timeout."""
        try:
            self.page.locator(selector).first.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_hidden(self, selector: str, timeout: int = 5000) -> bool:
        """Wait for an element matching selector to become hidden."""
        try:
            self.page.locator(selector).first.wait_for(state="hidden", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_url_contains(self, fragment: str, timeout: int = 15000) -> bool:
        """Wait until page URL contains the specified substring."""
        try:
            self.page.wait_for_url(lambda u: fragment.lower() in u.lower(), timeout=timeout)
            return True
        except Exception:
            return False

    def text(self, selector: str) -> str:
        """Retrieve inner text of the first matching element."""
        return self.page.locator(selector).first.inner_text().strip()

    def click_card(self, card_title: str):
        """Click one of the dashboard-style navigation cards by heading text."""
        try:
            card_locator = self.page.locator(f"text={card_title}").first
            if self.is_visible(f"text={card_title}", timeout=4000):
                card_locator.click()
                self.wait_for_dom_ready(timeout=5000)
                self._dismiss_tutorial()
            else:
                self.log.info(f"Card '{card_title}' not visible, proceeding...")
        except Exception as e:
            self.log.warning(f"Could not click card '{card_title}': {e}")

    def get_toast(self, timeout: int = 4000) -> str:
        """Retrieve dynamic snackbar or toast notification text."""
        toast_sel = (
            "simple-snack-bar, .mat-mdc-snack-bar-container, "
            ".mat-snack-bar-container, .toast, .toast-message, [role='alert']"
        )
        try:
            el = self.page.locator(toast_sel).first
            el.wait_for(state="visible", timeout=timeout)
            return el.inner_text().strip()
        except Exception:
            return ""

    def get_validation_errors(self) -> List[str]:
        """Collect visible inline validation error messages."""
        err_sel = "mat-error, .text-danger, .error-message, [role='alert'], .invalid-feedback, .mat-mdc-form-field-error"
        errors = []
        try:
            elements = self.page.locator(err_sel).all()
            for el in elements:
                if el.is_visible():
                    t = el.inner_text().strip()
                    if t and t not in errors:
                        errors.append(t)
        except Exception:
            pass
        return errors

    def is_form_invalid(self) -> bool:
        """Check if form or fields currently have ng-invalid or aria-invalid classes."""
        try:
            invalid_count = self.page.locator(
                "form.ng-invalid, input.ng-invalid, textarea.ng-invalid, "
                "mat-select.ng-invalid, mat-form-field.mat-form-field-invalid, [aria-invalid='true']"
            ).count()
            return invalid_count > 0
        except Exception:
            return False
