"""
TfaPage - Page Object Model for the Swarajya 2FA (Google Auth Code) Page.

After successful Employee ID + Password login, the user is redirected to:
  /tfa-authcode/{encoded_token}

This page has a single input for the Google Authenticator code and a Submit button.
"""
import logging

logger = logging.getLogger(__name__)


class TfaPage:
    """Page Object representing the Swarajya 2FA verification page."""

    # ── URL pattern ──
    TFA_URL_FRAGMENT = "/tfa-authcode/"

    # ── Timeouts ──
    DEFAULT_TIMEOUT = 10_000
    SNACKBAR_TIMEOUT = 5_000

    def __init__(self, page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # ────────────────────────── Locators ──────────────────────────

    @property
    def auth_code_input(self):
        """Google Auth Code input field (label: 'Enter Google Auth Code', name='authCode')."""
        return self.page.get_by_label("Enter Google Auth Code")

    @property
    def submit_button(self):
        """Submit button on the 2FA page."""
        return self.page.get_by_role("button", name="Submit")

    @property
    def back_to_login_link(self):
        """'Back to Login' link (navigates to /)."""
        return self.page.get_by_role("link", name="Back to Login")

    @property
    def error_snackbar(self):
        """Angular Material snackbar for error messages."""
        return self.page.locator("simple-snack-bar")

    @property
    def page_heading(self):
        """Page heading text 'Swarajya 2FA - Google Auth Code'."""
        return self.page.locator("text=Swarajya 2FA - Google Auth Code")

    # ────────────────────────── Queries ──────────────────────────

    def is_on_tfa_page(self) -> bool:
        """Check if the current URL contains the 2FA path fragment."""
        current_url = self.page.url
        result = self.TFA_URL_FRAGMENT in current_url
        logger.info("Is on 2FA page: %s (URL: %s)", result, current_url)
        return result

    def wait_for_tfa_page(self, timeout: int = None):
        """Wait until the URL contains the 2FA path fragment."""
        timeout = timeout or self.DEFAULT_TIMEOUT
        logger.info("Waiting for 2FA page to load...")
        self.page.wait_for_url(
            lambda url: self.TFA_URL_FRAGMENT in url,
            timeout=timeout,
        )
        self.page.wait_for_timeout(500)  # Allow Angular rendering
        return self

    # ────────────────────────── Actions ──────────────────────────

    def enter_auth_code(self, code: str):
        """Fill the Google Auth Code field. Does NOT log the code value."""
        logger.info("Entering 2FA auth code (masked)")
        self.auth_code_input.fill(str(code))
        return self

    def click_submit(self):
        """Click the Submit button."""
        logger.info("Clicking 2FA Submit button")
        self.submit_button.click()
        return self

    def submit_auth_code(self, code: str):
        """Compound action: enter code and click Submit."""
        logger.info("Submitting 2FA auth code")
        self.enter_auth_code(code)
        self.click_submit()
        return self

    def click_back_to_login(self):
        """Click the 'Back to Login' link."""
        logger.info("Clicking 'Back to Login' link")
        self.back_to_login_link.click()
        return self

    # ────────────────────────── Assertions ──────────────────────────

    def is_auth_code_input_visible(self) -> bool:
        """Check if the auth code input is visible."""
        return self.auth_code_input.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_submit_button_visible(self) -> bool:
        """Check if the Submit button is visible."""
        return self.submit_button.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_back_to_login_visible(self) -> bool:
        """Check if the 'Back to Login' link is visible."""
        return self.back_to_login_link.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def get_error_message(self, timeout: int = None) -> str:
        """Wait for error snackbar and return its text."""
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            message = self.error_snackbar.inner_text().strip()
            logger.info("2FA error message: '%s'", message)
            return message
        except Exception:
            logger.info("No 2FA error snackbar appeared within %dms", timeout)
            return ""

    def is_error_displayed(self, timeout: int = None) -> bool:
        """Check if any error snackbar is visible on the 2FA page."""
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_dashboard_loaded(self, timeout: int = 15_000) -> bool:
        """Check if the page has navigated to the dashboard after 2FA."""
        try:
            self.page.wait_for_url(
                lambda url: "/default" in url,
                timeout=timeout,
            )
            self.page.wait_for_load_state("networkidle", timeout=10_000)
            return True
        except Exception:
            return False

    def get_dashboard_title(self) -> str:
        """Get the page title after navigating to the dashboard."""
        return self.page.title()
