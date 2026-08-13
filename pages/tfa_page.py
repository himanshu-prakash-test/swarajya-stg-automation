"""Page object for the Swarajya 2FA (Google Auth Code) page."""
import logging

log = logging.getLogger(__name__)


class TfaPage:
    TFA_URL_FRAGMENT = "/tfa-authcode/"
    DEFAULT_TIMEOUT = 10_000
    SNACKBAR_TIMEOUT = 5_000

    def __init__(self, page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # --- Locators ---

    @property
    def auth_code_input(self):
        return self.page.get_by_label("Enter Google Auth Code")

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="Submit")

    @property
    def back_to_login_link(self):
        return self.page.get_by_role("link", name="Back to Login")

    @property
    def error_snackbar(self):
        return self.page.locator("simple-snack-bar")

    @property
    def page_heading(self):
        return self.page.locator("text=Swarajya 2FA - Google Auth Code")

    # --- Queries ---

    def is_on_tfa_page(self) -> bool:
        return self.TFA_URL_FRAGMENT in self.page.url

    def wait_for_tfa_page(self, timeout: int = None):
        timeout = timeout or self.DEFAULT_TIMEOUT
        self.page.wait_for_url(
            lambda url: self.TFA_URL_FRAGMENT in url,
            timeout=timeout,
        )
        self.page.wait_for_timeout(500)
        return self

    # --- Actions ---

    def enter_auth_code(self, code: str):
        self.auth_code_input.fill(str(code))
        return self

    def click_submit(self):
        self.submit_button.click()
        return self

    def submit_auth_code(self, code: str):
        self.enter_auth_code(code)
        self.click_submit()
        return self

    def click_back_to_login(self):
        self.back_to_login_link.click()
        return self

    # --- Assertions ---

    def is_auth_code_input_visible(self) -> bool:
        return self.auth_code_input.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_submit_button_visible(self) -> bool:
        return self.submit_button.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_back_to_login_visible(self) -> bool:
        return self.back_to_login_link.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def get_error_message(self, timeout: int = None) -> str:
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            return self.error_snackbar.inner_text().strip()
        except Exception:
            return ""

    def is_error_displayed(self, timeout: int = None) -> bool:
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_dashboard_loaded(self, timeout: int = 15_000) -> bool:
        try:
            self.page.wait_for_url(lambda url: "/default" in url, timeout=timeout)
            self.page.wait_for_load_state("networkidle", timeout=10_000)
            return True
        except Exception:
            return False

    def get_dashboard_title(self) -> str:
        return self.page.title()
