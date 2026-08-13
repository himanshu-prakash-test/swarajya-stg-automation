"""
LoginPage - Swarajya Login Page Object.

Locators and flow mirror the existing features/himanshu repository.
"""

import logging

logger = logging.getLogger(__name__)


class LoginPage:
    LOGIN_PATH = "/"
    DEFAULT_TIMEOUT = 10_000
    SNACKBAR_TIMEOUT = 5_000

    def __init__(self, page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    @property
    def employee_id_input(self):
        return self.page.get_by_label("Employee ID")

    @property
    def password_input(self):
        return self.page.get_by_label("Password")

    @property
    def sign_in_button(self):
        return self.page.get_by_role("button", name="Sign In")

    @property
    def forgot_password_link(self):
        return self.page.get_by_role("link", name="Forgot Password")

    @property
    def error_snackbar(self):
        return self.page.locator("simple-snack-bar")

    def navigate(self):
        url = f"{self.base_url}{self.LOGIN_PATH}"
        logger.info("Navigating to login page: %s", url)
        self.page.goto(url, wait_until="networkidle", timeout=30_000)
        self.page.wait_for_timeout(1000)
        return self

    def enter_employee_id(self, employee_id: str):
        logger.info("Entering Employee ID (length: %d)", len(str(employee_id)))
        self.employee_id_input.fill(str(employee_id))
        return self

    def enter_password(self, password: str):
        logger.info("Entering password (masked)")
        self.password_input.fill(str(password))
        return self

    def click_sign_in(self):
        logger.info("Clicking Sign In")
        self.sign_in_button.click()
        return self

    def login(self, employee_id: str, password: str):
        self.enter_employee_id(employee_id)
        self.enter_password(password)
        self.click_sign_in()
        return self

    def get_error_message(self, timeout=None) -> str:
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            return self.error_snackbar.inner_text().strip()
        except Exception:
            return ""

    def is_error_displayed(self, timeout=None) -> bool:
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_current_url(self) -> str:
        return self.page.url
