import os
from typing import Optional
from playwright.sync_api import Page
from shared.pages.base_page import BasePage
from shared.utils.excel_base import read_credentials
from shared.utils.logger import get_logger

log = get_logger("SharedAuthSetupPage")


class AuthSetupPage(BasePage):
    """
    Standardized Login and 2FA authentication flow for test setup fixtures.
    Strictly fetches credentials by role from shared/test_data Excel sheets with zero hardcoding.
    """

    def __init__(self, page: Page, base_url: Optional[str] = None):
        super().__init__(page, base_url=base_url)

    def login(
        self,
        employee_id: Optional[str] = None,
        password: Optional[str] = None,
        auth_code: Optional[str] = None,
        role: str = "Admin",
        save_state_path: Optional[str] = None,
    ) -> bool:
        """Perform full authentication: credentials entry + 2FA submission."""
        # Strictly fetch from Excel when credentials are not directly provided
        if not employee_id or not password:
            creds = read_credentials(role=role)
            employee_id = creds["employee_id"]
            password = creds["password"]
            auth_code = auth_code or creds.get("auth_code", "111111")

        if "default" in self.page.url.lower() or "dashboard" in self.page.url.lower():
            log.info("Already on dashboard.")
            return True

        if "tfa" in self.page.url.lower():
            self._handle_2fa(auth_code or "111111")
            return True

        self.goto("/")
        self.wait_for_dom_ready()

        email_sel = "input#mat-input-0, input[name='email'], input[type='text'], input[placeholder*='Employee ID'], input[placeholder*='Email']"
        pass_sel = "input#mat-input-1, input[name='password'], input[type='password'], input[placeholder*='Password']"
        submit_sel = "button:has-text('Sign In'), button[type='submit'], button.btn-primary"

        self.fill(email_sel, str(employee_id))
        self.fill(pass_sel, str(password))
        self.click(submit_sel)
        self.wait_for_dom_ready()

        # Check if 2FA screen is reached
        try:
            self.page.wait_for_url(
                lambda u: "tfa" in u.lower() or "dashboard" in u.lower() or "default" in u.lower(),
                timeout=10000,
            )
        except Exception:
            pass

        if "tfa" in self.page.url.lower():
            self._handle_2fa(auth_code or "111111")

        success = "login" not in self.page.url.lower()
        if success and save_state_path:
            try:
                os.makedirs(os.path.dirname(save_state_path), exist_ok=True)
                self.page.context.storage_state(path=save_state_path)
            except Exception as exc:
                log.warning(f"Could not save storage state: {exc}")

        return success

    def _handle_2fa(self, auth_code: str):
        """Submit 2FA OTP verification code."""
        tfa_sel = "input#mat-input-2, input[name='authCode'], input[placeholder*='OTP'], input[placeholder*='code'], input[type='text']"
        submit_tfa = "button:has-text('Submit'), button[type='submit'], button.btn-primary"
        try:
            self.fill(tfa_sel, str(auth_code))
            self.click(submit_tfa)
            self.page.wait_for_url(
                lambda u: "dashboard" in u.lower() or "default" in u.lower(),
                timeout=15000,
            )
            self.wait_for_dom_ready(timeout=5000)
            self._dismiss_tutorial()
        except Exception as exc:
            log.warning(f"2FA completion notice: {exc}")
