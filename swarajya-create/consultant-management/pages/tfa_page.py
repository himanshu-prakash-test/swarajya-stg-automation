"""
TfaPage - Swarajya 2FA Page Object.

Mirrors the existing repository's Google Auth Code flow.
"""

import logging

logger = logging.getLogger(__name__)


class TfaPage:
    TFA_URL_FRAGMENT = "/tfa-authcode/"
    DEFAULT_TIMEOUT = 10_000
    SNACKBAR_TIMEOUT = 5_000

    def __init__(self, page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

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

    def is_on_tfa_page(self) -> bool:
        return self.TFA_URL_FRAGMENT in self.page.url

    def is_back_to_login_visible(self, timeout=None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        return self.back_to_login_link.is_visible(timeout=timeout)

    def click_back_to_login(self):
        logger.info("Clicking Back to Login")
        self.back_to_login_link.click()
        return self

    def wait_for_tfa_page(self, timeout=None):
        timeout = timeout or self.DEFAULT_TIMEOUT
        self.page.wait_for_url(
            lambda url: self.TFA_URL_FRAGMENT in url or "/default" in url or "/employeeList" in url or "/empProfile/" in url,
            timeout=timeout,
        )
        if self.is_on_tfa_page():
            self.auth_code_input.wait_for(state="visible", timeout=timeout)
        return self

    def enter_auth_code(self, code: str):
        logger.info("Entering 2FA auth code (masked)")
        self.auth_code_input.fill(str(code))
        return self

    def click_submit(self):
        logger.info("Clicking 2FA Submit")
        self.submit_button.click()
        return self

    def submit_auth_code(self, code: str):
        self.enter_auth_code(code)
        self.click_submit()
        return self

    def is_auth_code_input_visible(self) -> bool:
        return self.auth_code_input.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_dashboard_loaded(self, timeout=15_000) -> bool:
        try:
            self.page.wait_for_url(
                lambda url: "/default" in url,
                timeout=timeout,
            )
            self.page.wait_for_load_state("networkidle", timeout=10_000)
            return True
        except Exception:
            return False

    def get_error_message(self, timeout=None) -> str:
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            return self.error_snackbar.inner_text().strip()
        except Exception:
            return ""
