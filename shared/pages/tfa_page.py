"""Centralized Page Object for Swarajya 2FA (Google Auth Code) Page."""
import logging
from typing import Optional
from playwright.sync_api import Page
from shared.pages.base_page import BasePage

log = logging.getLogger("SharedTfaPage")


class TfaPage(BasePage):
    TFA_URL_FRAGMENT = "/tfa-authcode/"
    DEFAULT_TIMEOUT = 30_000
    SNACKBAR_TIMEOUT = 5_000

    def __init__(self, page: Page, base_url: Optional[str] = None):
        super().__init__(page, base_url=base_url)

    # --- Locators ---

    @property
    def auth_code_input(self):
        return self.page.locator("input[formcontrolname='authcode'], input[name='authcode'], input[placeholder*='Auth'], input[placeholder*='Google']").or_(self.page.get_by_label("Enter Google Auth Code")).first

    @property
    def submit_button(self):
        return self.page.get_by_role("button", name="Submit")

    @property
    def back_to_login_link(self):
        return self.page.get_by_role("link", name="Back to Login")

    @property
    def error_snackbar(self):
        return self.page.locator("simple-snack-bar, mat-snack-bar-container, .mat-mdc-snack-bar-container").first

    @property
    def page_heading(self):
        return self.page.locator("text=Swarajya 2FA - Google Auth Code").first

    # --- Queries ---

    def is_on_tfa_page(self) -> bool:
        return self.TFA_URL_FRAGMENT in self.page.url

    def wait_for_tfa_page(self, timeout: Optional[int] = None):
        to = timeout or self.DEFAULT_TIMEOUT
        self.page.wait_for_url(
            lambda url: self.TFA_URL_FRAGMENT in url,
            timeout=to,
        )
        try:
            self.auth_code_input.wait_for(state="visible", timeout=to)
        except Exception:
            pass
        return self

    # --- Actions ---

    def enter_auth_code(self, code: str):
        try:
            self.auth_code_input.wait_for(state="visible", timeout=10_000)
        except Exception:
            pass
        self.auth_code_input.fill(str(code))
        return self

    def click_submit(self):
        self.submit_button.click()
        return self

    def submit_auth_code(self, code: str):
        self.enter_auth_code(code)
        self.page.wait_for_timeout(300)
        self.click_submit()
        try:
            self.page.wait_for_url(
                lambda u: self.TFA_URL_FRAGMENT not in u,
                timeout=5_000,
            )
        except Exception:
            if self.is_on_tfa_page():
                self.click_submit()
        return self

    def click_back_to_login(self):
        self.back_to_login_link.click()
        return self

    # --- Assertions ---

    def is_auth_code_input_visible(self, timeout: Optional[int] = None) -> bool:
        to = timeout or self.DEFAULT_TIMEOUT
        try:
            self.auth_code_input.wait_for(state="visible", timeout=to)
            return True
        except Exception:
            return False

    def is_submit_button_visible(self, timeout: Optional[int] = None) -> bool:
        to = timeout or self.DEFAULT_TIMEOUT
        try:
            self.submit_button.wait_for(state="visible", timeout=to)
            return True
        except Exception:
            return False

    def is_back_to_login_visible(self, timeout: Optional[int] = None) -> bool:
        to = timeout or self.DEFAULT_TIMEOUT
        try:
            self.back_to_login_link.wait_for(state="visible", timeout=to)
            return True
        except Exception:
            return False

    def get_error_message(self, timeout: Optional[int] = None) -> str:
        to = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=to)
            return self.error_snackbar.inner_text().strip()
        except Exception:
            return ""

    def is_error_displayed(self, timeout: Optional[int] = None) -> bool:
        to = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=to)
            return True
        except Exception:
            return False

    def is_dashboard_loaded(self, timeout: int = 15_000) -> bool:
        try:
            self.page.wait_for_url(lambda url: "/default" in url, timeout=timeout)
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=5000)
            except Exception:
                pass
            return True
        except Exception:
            return False

    def get_dashboard_title(self) -> str:
        return self.page.title()
