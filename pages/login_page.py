"""
LoginPage - Page Object Model for the Swarajya Login Page.

Locators verified against the live staging application.
Uses Playwright's recommended get_by_label / get_by_role for stability.
"""
import logging

logger = logging.getLogger(__name__)


class LoginPage:
    """Page Object representing the Swarajya login page."""

    # ── URL ──
    LOGIN_PATH = "/"

    # ── Timeouts ──
    DEFAULT_TIMEOUT = 10_000  # 10 seconds
    SNACKBAR_TIMEOUT = 5_000  # Snackbar auto-dismisses quickly

    def __init__(self, page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # ────────────────────────── Locators ──────────────────────────

    @property
    def employee_id_input(self):
        """Employee ID input field (label: 'Employee ID', name='email')."""
        return self.page.get_by_label("Employee ID")

    @property
    def password_input(self):
        """Password input field (label: 'Password', type='password')."""
        return self.page.get_by_label("Password")

    @property
    def sign_in_button(self):
        """Sign In button."""
        return self.page.get_by_role("button", name="Sign In")

    @property
    def forgot_password_link(self):
        """Forgot Password link (navigates to /forgot)."""
        return self.page.get_by_role("link", name="Forgot Password")

    @property
    def error_snackbar(self):
        """Angular Material snackbar displaying error messages."""
        return self.page.locator("simple-snack-bar")

    @property
    def snackbar_message(self):
        """Text content inside the snackbar."""
        return self.page.locator(".mat-mdc-snack-bar-label .mdc-snackbar__label")

    # ────────────────────────── Navigation ──────────────────────────

    def navigate(self):
        """Navigate to the login page and wait for it to fully load."""
        url = f"{self.base_url}{self.LOGIN_PATH}"
        logger.info("Navigating to login page: %s", url)
        self.page.goto(url, wait_until="networkidle", timeout=30_000)
        self.page.wait_for_timeout(1000)  # Allow Angular rendering
        return self

    # ────────────────────────── Actions ──────────────────────────

    def enter_employee_id(self, employee_id: str):
        """Fill the Employee ID field. Logs the action (not the value for security)."""
        logger.info("Entering Employee ID (length: %d)", len(str(employee_id)))
        self.employee_id_input.fill(str(employee_id))
        return self

    def enter_password(self, password: str):
        """Fill the Password field. Does NOT log the password value."""
        logger.info("Entering password (masked)")
        self.password_input.fill(password)
        return self

    def click_sign_in(self):
        """Click the Sign In button."""
        logger.info("Clicking Sign In button")
        self.sign_in_button.click()
        return self

    def login(self, employee_id: str, password: str):
        """
        Compound action: enter credentials and click Sign In.
        Does NOT log credentials for security.
        """
        logger.info("Performing login action for employee (length: %d)", len(str(employee_id)))
        self.enter_employee_id(employee_id)
        self.enter_password(password)
        self.click_sign_in()
        return self

    def click_forgot_password(self):
        """Click the Forgot Password link."""
        logger.info("Clicking Forgot Password link")
        self.forgot_password_link.click()
        return self

    # ────────────────────────── Assertions / Queries ──────────────────────────

    def is_on_login_page(self) -> bool:
        """Check if the current page is the login page."""
        current_url = self.page.url
        # Login page is at root "/" or might have returnUrl params
        is_login = (
            current_url.rstrip("/") == self.base_url.rstrip("/")
            or "tfa-authcode" not in current_url
            and "default" not in current_url
            and "forgot" not in current_url
        )
        logger.info("Is on login page: %s (URL: %s)", is_login, current_url)
        return is_login

    def is_employee_id_field_visible(self) -> bool:
        """Check if the Employee ID input is visible."""
        return self.employee_id_input.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_password_field_visible(self) -> bool:
        """Check if the Password input is visible."""
        return self.password_input.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_sign_in_button_visible(self) -> bool:
        """Check if the Sign In button is visible."""
        return self.sign_in_button.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_sign_in_button_enabled(self) -> bool:
        """Check if the Sign In button is enabled (not disabled)."""
        return self.sign_in_button.is_enabled()

    def is_forgot_password_visible(self) -> bool:
        """Check if the Forgot Password link is visible."""
        return self.forgot_password_link.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_password_masked(self) -> bool:
        """Verify the password field has type='password' (input is masked)."""
        input_type = self.page.locator("input[name='password']").get_attribute("type")
        is_masked = input_type == "password"
        logger.info("Password masked: %s (type='%s')", is_masked, input_type)
        return is_masked

    def get_error_message(self, timeout: int = None) -> str:
        """
        Wait for the error snackbar to appear and return its text.
        Returns empty string if snackbar doesn't appear within timeout.
        """
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            message = self.error_snackbar.inner_text().strip()
            logger.info("Error message displayed: '%s'", message)
            return message
        except Exception:
            logger.info("No error snackbar appeared within %dms", timeout)
            return ""

    def is_error_displayed(self, timeout: int = None) -> bool:
        """Check if any error snackbar is currently visible."""
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_employee_id_value(self) -> str:
        """Get the current value of the Employee ID field."""
        return self.employee_id_input.input_value()

    def get_page_title(self) -> str:
        """Get the browser page title."""
        return self.page.title()

    def get_current_url(self) -> str:
        """Get the current page URL."""
        return self.page.url
