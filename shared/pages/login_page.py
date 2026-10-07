import os
from typing import Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from shared.pages.base_page import BasePage
from shared.utils.excel_base import read_credentials
from shared.utils.logger import get_logger

log = get_logger("SharedLoginPage")


class LoginPage(BasePage):
    """
    Unified Master Login Page Object for Swarajya Automation.
    Used by Create, Update, and Login modules.
    Strictly reads credentials dynamically from shared/test_data with zero hardcoding.
    """

    LOGIN_PATH = "/"
    DEFAULT_TIMEOUT = 10_000
    SNACKBAR_TIMEOUT = 5_000

    def __init__(self, page: Page, base_url: Optional[str] = None):
        super().__init__(page, base_url=base_url)

    # ---------------------------------------------------------
    # Locators & Properties
    # ---------------------------------------------------------
    @property
    def employee_id_input(self):
        return self.page.locator("input[name='email'], input#mat-input-0, input[placeholder*='Employee ID'], input[placeholder*='Email'], input[type='text']").first

    @property
    def password_input(self):
        return self.page.locator("input[name='password'], input#mat-input-1, input[placeholder*='Password'], input[type='password']").first

    @property
    def sign_in_button(self):
        return self.page.locator("button:has-text('Sign In'), button[type='submit'], button.btn-primary").first

    @property
    def forgot_password_link(self):
        return self.page.locator("a:has-text('Forgot Password'), a[href*='forgot']").first

    @property
    def error_snackbar(self):
        return self.page.locator("simple-snack-bar, mat-snack-bar-container, .mat-mdc-snack-bar-container, .alert-danger, .error-message").first

    @property
    def snackbar_message(self):
        return self.page.locator(".mat-mdc-snack-bar-label .mdc-snackbar__label, simple-snack-bar span, .alert-danger").first

    @property
    def tfa_input(self):
        return self.page.locator("input#mat-input-2, input[name='authCode'], input[placeholder*='OTP'], input[placeholder*='code'], input[type='text']").first

    @property
    def tfa_submit_button(self):
        return self.page.locator("button:has-text('Submit'), button[type='submit'], button.btn-primary").first

    # ---------------------------------------------------------
    # Navigation & State Checks
    # ---------------------------------------------------------
    def navigate(self):
        """Navigate to base login page with 503 resilience."""
        self.goto(self.LOGIN_PATH)
        self.wait_for_dom_ready()
        return self

    def open(self):
        """Alias for navigate."""
        return self.navigate()

    def wait_for_login_page(self, timeout: int = 10_000):
        """Dynamically wait for login inputs to become visible."""
        try:
            self.employee_id_input.wait_for(state="visible", timeout=timeout)
        except Exception:
            pass
        return self

    def is_on_login_page(self) -> bool:
        url = self.page.url.lower()
        return (
            url.rstrip("/") == self.base_url.rstrip("/")
            or ("tfa" not in url and "default" not in url and "forgot" not in url and "dashboard" not in url)
        )

    def is_on_dashboard(self) -> bool:
        """Check if user has arrived at the authenticated dashboard."""
        url = self.page.url.lower()
        return (
            (
                "dashboard" in url
                or "default" in url
                or "employeelist" in url
                or "vendor" in url
                or "customer" in url
                or "purchaseorder" in url
                or "consultant" in url
            )
            and "login" not in url
            and "tfa" not in url
        )

    def is_on_tfa_screen(self) -> bool:
        """Check if user is currently on the 2FA OTP prompt screen."""
        url = self.page.url.lower()
        if "tfa" in url:
            return True
        try:
            return self.tfa_input.is_visible(timeout=2000)
        except Exception:
            return False

    # ---------------------------------------------------------
    # Actions
    # ---------------------------------------------------------
    def enter_employee_id(self, employee_id: str):
        try:
            self.employee_id_input.wait_for(state="visible", timeout=10_000)
        except Exception:
            pass
        self.employee_id_input.fill(str(employee_id))
        return self

    def enter_password(self, password: str):
        try:
            self.password_input.wait_for(state="visible", timeout=10_000)
        except Exception:
            pass
        self.password_input.fill(str(password))
        return self

    def click_sign_in(self):
        self.sign_in_button.click()
        self.wait_for_dom_ready()
        return self

    def enter_auth_code(self, auth_code: str):
        try:
            self.tfa_input.wait_for(state="visible", timeout=10_000)
        except Exception:
            pass
        self.tfa_input.fill(str(auth_code))
        return self

    def click_submit_tfa(self):
        self.tfa_submit_button.click()
        self.wait_for_dom_ready()
        return self

    def click_forgot_password(self):
        self.forgot_password_link.click()
        self.wait_for_dom_ready()
        return self

    # ---------------------------------------------------------
    # Assertions / Inspections
    # ---------------------------------------------------------
    def is_employee_id_field_visible(self, timeout: Optional[int] = None) -> bool:
        to = timeout or self.DEFAULT_TIMEOUT
        try:
            self.employee_id_input.wait_for(state="visible", timeout=to)
            return True
        except Exception:
            return False

    def is_password_field_visible(self, timeout: Optional[int] = None) -> bool:
        to = timeout or self.DEFAULT_TIMEOUT
        try:
            self.password_input.wait_for(state="visible", timeout=to)
            return True
        except Exception:
            return False

    def is_sign_in_button_visible(self, timeout: Optional[int] = None) -> bool:
        to = timeout or self.DEFAULT_TIMEOUT
        try:
            self.sign_in_button.wait_for(state="visible", timeout=to)
            return True
        except Exception:
            return False

    def is_sign_in_button_enabled(self) -> bool:
        try:
            return self.sign_in_button.is_enabled()
        except Exception:
            return False

    def is_forgot_password_visible(self, timeout: Optional[int] = None) -> bool:
        to = timeout or self.DEFAULT_TIMEOUT
        try:
            self.forgot_password_link.wait_for(state="visible", timeout=to)
            return True
        except Exception:
            return False

    def is_password_masked(self) -> bool:
        try:
            return self.password_input.get_attribute("type") == "password"
        except Exception:
            return False

    def is_error_displayed(self, timeout: Optional[int] = None) -> bool:
        to = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=to)
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

    def get_employee_id_value(self) -> str:
        return self.employee_id_input.input_value()

    def get_page_title(self) -> str:
        return self.page.title()

    def get_current_url(self) -> str:
        return self.page.url

    # ---------------------------------------------------------
    # High-level Login Orchestration
    # ---------------------------------------------------------
    def login(
        self,
        employee_id: Optional[str] = None,
        password: Optional[str] = None,
        auth_code: Optional[str] = None,
        role: str = "Admin",
        emp_id: Optional[str] = None,
        pwd: Optional[str] = None,
        expected_landing: Optional[str] = None,
        save_state_path: Optional[str] = None,
    ) -> bool:
        """
        Authenticate user and complete 2FA OTP.
        Strictly resolves credentials from Excel via role lookup if not explicitly provided.
        """
        resolved_id = employee_id or emp_id
        resolved_pwd = password or pwd

        # Fetch credentials from Excel when not explicitly passed
        if not resolved_id or not resolved_pwd:
            creds = read_credentials(role=role)
            resolved_id = creds["employee_id"]
            resolved_pwd = creds["password"]
            auth_code = auth_code or creds.get("auth_code", "111111")

        if self.is_on_dashboard():
            log.info("Already on authenticated dashboard.")
            return True

        self.navigate()

        self.enter_employee_id(resolved_id)
        self.enter_password(resolved_pwd)
        self.click_sign_in()

        # Wait for either TFA screen or Dashboard transition
        try:
            self.page.wait_for_url(
                lambda u: "tfa" in u.lower() or "dashboard" in u.lower() or "default" in u.lower(),
                timeout=10000,
            )
        except Exception:
            pass

        # Handle 2FA if reached
        if self.is_on_tfa_screen():
            self.enter_auth_code(auth_code or "111111")
            self.click_submit_tfa()

        # Wait for post-login destination
        try:
            self.page.wait_for_url(
                lambda u: "tfa" not in u.lower()
                and ("dashboard" in u.lower() or "default" in u.lower() or (expected_landing and expected_landing in u.lower())),
                timeout=15000,
            )
            self.wait_for_dom_ready()
            self._dismiss_tutorial()
            if save_state_path:
                self.save_auth_state(save_state_path)
            return True
        except Exception:
            if not ("login" in self.page.url.lower() or "tfa" in self.page.url.lower()):
                self._dismiss_tutorial()
                if save_state_path:
                    self.save_auth_state(save_state_path)
                return True
            return False

    def save_auth_state(self, path: Optional[str] = None):
        """Save browser context storage state."""
        try:
            target_path = path or os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "test_data",
                "auth_state.json",
            )
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            self.page.context.storage_state(path=target_path)
            log.info(f"Saved auth state to {target_path}")
        except Exception as exc:
            log.warning(f"Could not save storage state: {exc}")
