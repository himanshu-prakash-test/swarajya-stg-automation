from playwright.sync_api import Page
from emp_utils.logger import get_logger

log = get_logger("BasePage")

BASE_URL = "https://swarajya-stg.corecotechnologies.com"


class BasePage:
    """Thin wrapper around Playwright Page with dynamic waiting and resilience."""

    def __init__(self, page: Page):
        self.page = page
        self.log = get_logger(self.__class__.__name__)

    def goto(self, path: str):
        url = f"{BASE_URL}/{path.lstrip('/')}"
        self.log.info(f"Opening {url}")
        for attempt in range(1, 7):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=20000)
                self.wait_for_dom_ready(timeout=5000)
                try:
                    content = self.page.content().lower()
                    if "service unavailable" in content or "503" in content:
                        self.log.warning(f"Attempt {attempt}: Encountered Service Unavailable. Retrying...")
                        self.page.wait_for_timeout(3500)
                        continue
                except Exception:
                    pass
                self._dismiss_tutorial()
                return
            except Exception as e:
                self.log.warning(f"Navigation attempt {attempt} failed: {e}")
                self.page.wait_for_timeout(2000)
        self.page.goto(url, wait_until="commit", timeout=20000)
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
        """Some pages show a guided-tour overlay. Click it away and wait dynamically."""
        for _ in range(3):
            skip = self.page.locator("button:has-text('Skip Intro')")
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

    def click_card(self, card_title: str):
        """Click one of the dashboard-style navigation cards by its heading text."""
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

    def get_toast(self, timeout: int = 3000) -> str:
        toast_selector = (
            "simple-snack-bar, .mat-mdc-snack-bar-label, "
            ".toast-message, [role='alert'], .mat-snack-bar-container"
        )
        try:
            toast_locator = self.page.locator(toast_selector).first
            toast_locator.wait_for(state="visible", timeout=timeout)
            return toast_locator.inner_text().strip()
        except Exception:
            return ""
