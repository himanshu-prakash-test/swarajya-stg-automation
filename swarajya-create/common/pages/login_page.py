import os
from typing import Optional
from playwright.sync_api import Page
from shared.pages.base_page import BasePage
from common.utils.excel_base import read_credentials


class LoginPage(BasePage):
    """
    Unified Login Page Object for Swarajya Create modules.
    Handles credential entry, 2FA OTP verification, and role-based authentication.
    """

    def __init__(self, page: Page, base_url: Optional[str] = None):
        super().__init__(page, base_url=base_url)

    def navigate(self):
        """Navigate to base login page."""
        self.goto("/")
        self.wait_for_dom_ready()

    def open(self):
        """Alias for navigate."""
        self.navigate()

    def is_on_dashboard(self) -> bool:
        """Check if user is on dashboard/landing screen."""
        url = self.page.url.lower()
        return (
            ("dashboard" in url or "default" in url or "employeelist" in url or "addnewemployee" in url or "vendor" in url)
            and "login" not in url
            and "tfa" not in url
        )

    def login(
        self,
        employee_id: Optional[str] = None,
        password: Optional[str] = None,
        auth_code: Optional[str] = None,
        role: str = "Manager",
        emp_id: Optional[str] = None,
        pwd: Optional[str] = None,
    ) -> bool:
        """
        Authenticate user and complete 2FA.
        Supports both direct credentials and role lookup.
        """
        resolved_id = employee_id or emp_id
        resolved_pwd = password or pwd

        # If credentials not directly supplied, look up by role from credentials.xlsx
        if not resolved_id or not resolved_pwd:
            creds_path = self._find_credentials_file()
            creds = read_credentials(role=role, path=creds_path)
            resolved_id = creds["employee_id"]
            resolved_pwd = creds["password"]
            auth_code = auth_code or creds.get("auth_code", "111111")

        if self.is_on_dashboard():
            self.log.info("Already on dashboard.")
            return True

        self.navigate()

        email_sel = "input#mat-input-0, input[name='email'], input[type='text'], input[placeholder*='Employee ID'], input[placeholder*='Email']"
        pass_sel = "input#mat-input-1, input[name='password'], input[type='password'], input[placeholder*='Password']"
        submit_sel = "button:has-text('Sign In'), button[type='submit'], button.btn-primary"

        self.fill(email_sel, resolved_id)
        self.fill(pass_sel, resolved_pwd)
        self.click(submit_sel)
        self.wait_for_dom_ready()

        # Check for 2FA screen
        try:
            self.page.wait_for_url(
                lambda u: "tfa" in u.lower() or "dashboard" in u.lower() or "default" in u.lower(),
                timeout=10000,
            )
        except Exception:
            pass

        if "tfa" in self.page.url.lower():
            tfa_sel = "input#mat-input-2, input[name='authCode'], input[placeholder*='OTP'], input[placeholder*='code'], input[type='text']"
            submit_tfa = "button:has-text('Submit'), button[type='submit'], button.btn-primary"
            self.fill(tfa_sel, auth_code or "111111")
            self.click(submit_tfa)

        self.wait_for_dom_ready()
        try:
            self.page.wait_for_url(
                lambda u: "tfa" not in u.lower() and (
                    "dashboard" in u.lower() or "default" in u.lower() or "vendor" in u.lower() or "employee" in u.lower()
                ),
                timeout=15000,
            )
            self._dismiss_tutorial()
            self._save_auth_state()
            return True
        except Exception:
            if not ("login" in self.page.url.lower() or "tfa" in self.page.url.lower()):
                self._save_auth_state()
                return True
            return False

    def _save_auth_state(self):
        """Save browser context storage state if auth_state path exists."""
        try:
            creds_file = self._find_credentials_file()
            if creds_file:
                auth_path = os.path.join(os.path.dirname(creds_file), "auth_state.json")
                self.page.context.storage_state(path=auth_path)
        except Exception:
            pass

    def _find_credentials_file(self) -> Optional[str]:
        """Locate credentials.xlsx dynamically from project test_data folders."""
        curr = os.path.dirname(os.path.abspath(__file__))
        for _ in range(4):
            candidate = os.path.join(curr, "test_data", "credentials.xlsx")
            if os.path.exists(candidate):
                return candidate
            for sub in ("vendor-management", "employee-management", "common"):
                sub_candidate = os.path.join(curr, sub, "test_data", "credentials.xlsx")
                if os.path.exists(sub_candidate):
                    return sub_candidate
            curr = os.path.dirname(curr)
        return None
