import os
from typing import Optional
from playwright.sync_api import Page
from shared.pages.base_page import BasePage
from customer_update_utils.excel_reader import read_credentials
from shared.utils.logger import get_logger

log = get_logger("customer_update_login_page")


class LoginPage(BasePage):
    """Page Object for Swarajya Login and 2FA authentication for Customer Management."""

    def __init__(self, page: Page, base_url: str = "https://swarajya-stg.corecotechnologies.com"):
        super().__init__(page, base_url)

    def navigate(self):
        self.goto("/")
        self.wait_for_dom_ready()

    def login(
        self,
        employee_id: Optional[str] = None,
        password: Optional[str] = None,
        auth_code: Optional[str] = None,
        role: str = "Admin",
    ) -> bool:
        """Authenticate user and handle 2FA OTP verification."""
        if not employee_id or not password:
            creds = read_credentials(role)
            employee_id = creds.get("employee_id", "332")
            password = creds.get("password", "test@1234")
            auth_code = creds.get("auth_code", "111111")

        self.navigate()

        # If already logged in, check URL
        current_url = self.page.url.lower()
        if any(path in current_url for path in ("/default", "/customerdetails", "/invoicedashboard", "/invoicereports")):
            log.info("Already authenticated")
            return True

        # Fill credentials
        email_sel = "input#mat-input-0, input[name='email'], input[type='text'], input[placeholder*='Employee ID' i], input[placeholder*='Email' i]"
        pass_sel = "input#mat-input-1, input[name='password'], input[type='password'], input[placeholder*='Password' i]"
        submit_sel = "button:has-text('Sign In'), button[type='submit'], button.btn-primary"

        self.fill(email_sel, str(employee_id))
        self.fill(pass_sel, str(password))
        self.click(submit_sel)

        self.wait_for_dom_ready()

        # Handle 2FA if reached
        try:
            self.page.wait_for_url(
                lambda u: "tfa" in u.lower() or "dashboard" in u.lower() or "default" in u.lower() or "invoice" in u.lower() or "customer" in u.lower(),
                timeout=10000,
            )
        except Exception:
            pass

        if "tfa" in self.page.url.lower():
            tfa_sel = "input#mat-input-2, input[name='authCode'], input[placeholder*='OTP' i], input[placeholder*='code' i], input[type='text']"
            submit_tfa = "button:has-text('Submit'), button[type='submit'], button.btn-primary"
            self.fill(tfa_sel, str(auth_code or "111111"))
            self.click(submit_tfa)

        self.wait_for_dom_ready()
        try:
            self.page.wait_for_url(
                lambda u: "tfa" not in u.lower() and ("dashboard" in u.lower() or "default" in u.lower() or "customer" in u.lower() or "invoice" in u.lower()),
                timeout=15000,
            )
            self.dismiss_any_tutorial_or_dialog()
            return True
        except Exception:
            return not ("login" in self.page.url.lower() or "tfa" in self.page.url.lower())
