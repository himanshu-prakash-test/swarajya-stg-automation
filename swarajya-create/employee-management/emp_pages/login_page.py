from emp_pages.base_page import BasePage
from emp_utils.excel_reader import read_credentials


class LoginPage(BasePage):
    """Handles the Swarajya login form and 2FA auth-code screen."""

    def open(self):
        self.goto("/")

    def login(self, emp_id: str, pwd: str, auth_code: str = "111111"):
        """Perform full login: credentials + 2FA."""
        # If already logged in / on dashboard
        if self.is_on_dashboard():
            self.log.info("Already logged in and on dashboard.")
            return

        # Check if already on 2FA screen
        if "tfa" in self.page.url.lower():
            self.log.info("Completing 2FA auth-code screen")
            self.fill("input[name='authCode']", auth_code, timeout=15000)
            self.click("button:has-text('Submit')", timeout=15000)
            self.wait_for_url_contains("default", timeout=15000)
            self.wait_for_dom_ready(timeout=5000)
            self._dismiss_tutorial()
            try:
                import os
                auth_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_data", "auth_state.json")
                self.page.context.storage_state(path=auth_path)
            except Exception:
                pass
            return

        if "login" not in self.page.url.lower():
            self.open()

        # Wait for email input
        email_sel = "input[name='email'], input#mat-input-0, input[type='text'], input[placeholder*='Email' i], input[placeholder*='Employee' i]"
        pwd_sel = "input[name='password'], input#mat-input-1, input[type='password'], input[placeholder*='Password' i]"
        signin_sel = "button:has-text('Sign In'), button[type='submit']"
        auth_sel = "input[name='authCode'], input#mat-input-2, input[type='text'], input[placeholder*='Auth' i]"
        auth_submit_sel = "button:has-text('Submit'), button[type='submit']"

        try:
            self.page.locator(email_sel).first.wait_for(state="visible", timeout=10000)
        except Exception:
            self.goto("/")
            self.page.locator(email_sel).first.wait_for(state="visible", timeout=10000)

        # fill employee ID and password
        self.fill(email_sel, emp_id, timeout=15000)
        self.fill(pwd_sel, pwd, timeout=15000)
        self.click(signin_sel, timeout=15000)

        # Dynamically wait for 2FA screen, dashboard, or error toast to appear
        try:
            self.page.wait_for_function(
                "() => window.location.href.toLowerCase().includes('tfa') || window.location.href.toLowerCase().includes('default') || document.querySelector('simple-snack-bar, .mat-mdc-snack-bar-container') !== null",
                timeout=15000,
            )
        except Exception:
            pass

        # handle 2FA screen if it appears
        if "tfa" in self.page.url.lower():
            self.log.info("Completing 2FA auth-code screen")
            self.fill(auth_sel, auth_code, timeout=15000)
            self.click(auth_submit_sel, timeout=15000)

        # Wait for dashboard landing dynamically
        self.wait_for_url_contains("default", timeout=15000)
        self.wait_for_dom_ready(timeout=5000)
        self._dismiss_tutorial()
        try:
            import os
            auth_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_data", "auth_state.json")
            self.page.context.storage_state(path=auth_path)
        except Exception:
            pass

    def is_on_dashboard(self) -> bool:
        url = self.page.url.lower()
        return ("/default" in url or "employeelist" in url or "addnewemployee" in url) and "login" not in url and "tfa" not in url

