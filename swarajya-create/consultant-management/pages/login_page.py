"""Page object for the Swarajya login page."""

import logging

log = logging.getLogger(__name__)


class LoginPage:
    LOGIN_PATH = "/"
    DEFAULT_TIMEOUT = 10_000
    SNACKBAR_TIMEOUT = 5_000

    def __init__(self, page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    @property
    def employee_id_input(self):
        return self.page.locator("input[name='emp_id'], input[name='employee_id'], input[placeholder*='Employee' i]").or_(self.page.get_by_label("Employee ID"))

    @property
    def password_input(self):
        return self.page.locator("input[name='password'], input[type='password']").or_(self.page.get_by_label("Password"))

    @property
    def sign_in_button(self):
        return self.page.get_by_role("button", name="Sign In").or_(self.page.locator("button:has-text('Sign In')"))

    @property
    def forgot_password_link(self):
        return self.page.get_by_role("link", name="Forgot Password")

    @property
    def error_snackbar(self):
        return self.page.locator("simple-snack-bar")

    @property
    def snackbar_message(self):
        return self.page.locator(".mat-mdc-snack-bar-label .mdc-snackbar__label")

    def navigate(self):
        url = f"{self.base_url}{self.LOGIN_PATH}"
        log.info("Opening %s", url)
        for attempt in range(5):
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)

                # Check if already authenticated
                if any(k in self.page.url for k in ("/default", "/employeeList", "/empProfile/")):
                    return self

                # Dynamic wait for login input or error condition
                self.employee_id_input.wait_for(state="visible", timeout=8_000)
                return self
            except Exception:
                body_text = self.page.locator("body").inner_text() if self.page.locator("body").count() else ""
                if "service unavailable" in body_text.lower() or "503" in body_text:
                    log.warning("Staging 503 detected; reloading (attempt %d)...", attempt + 1)
                    self.page.reload(wait_until="domcontentloaded", timeout=30_000)
                    continue
                if attempt == 4:
                    raise
                log.warning("Login page was not ready; retrying navigation (attempt %d)", attempt + 1)
        return self

    def enter_employee_id(self, emp_id: str):
        self.employee_id_input.wait_for(state="visible", timeout=self.DEFAULT_TIMEOUT)
        self.employee_id_input.fill(str(emp_id))
        return self

    def enter_password(self, password: str):
        self.password_input.wait_for(state="visible", timeout=self.DEFAULT_TIMEOUT)
        self.password_input.fill(password)
        return self

    def click_sign_in(self):
        self.sign_in_button.scroll_into_view_if_needed()
        self.sign_in_button.click(force=True)
        return self

    def login(self, emp_id: str, password: str):
        if any(k in self.page.url for k in ("/default", "/employeeList", "/empProfile/")):
            return self
        self.enter_employee_id(emp_id)
        self.enter_password(password)
        self.click_sign_in()
        # Dynamically wait for URL transition to TFA, dashboard, or employee list
        try:
            self.page.wait_for_url(
                lambda url: any(k in url for k in ("/tfa-authcode/", "/default", "/employeeList", "/empProfile/")),
                timeout=6_000,
            )
        except Exception:
            if self.sign_in_button.is_visible() and self.sign_in_button.is_enabled():
                self.click_sign_in()
        return self

    def click_forgot_password(self):
        log.info("Clicking Forgot Password")
        self.forgot_password_link.click()
        return self

    def is_on_login_page(self) -> bool:
        url = self.page.url
        return (url.rstrip("/") == self.base_url.rstrip("/")
                or ("tfa-authcode" not in url
                    and "default" not in url
                    and "forgot" not in url))

    def is_employee_id_field_visible(self, timeout=None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        return self.employee_id_input.is_visible(timeout=timeout)

    def is_password_field_visible(self, timeout=None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        return self.password_input.is_visible(timeout=timeout)

    def is_sign_in_button_visible(self, timeout=None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        return self.sign_in_button.is_visible(timeout=timeout)

    def is_sign_in_button_enabled(self, timeout=None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        return self.sign_in_button.is_enabled(timeout=timeout)

    def is_forgot_password_visible(self, timeout=None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        return self.forgot_password_link.is_visible(timeout=timeout)

    def is_password_masked(self) -> bool:
        return self.page.locator("input[name='password']").get_attribute("type") == "password"

    def get_error_message(self, timeout: int = None) -> str:
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            return self.error_snackbar.inner_text().strip()
        except Exception:
            return ""

    def is_error_displayed(self, timeout: int = None) -> bool:
        timeout = timeout or self.SNACKBAR_TIMEOUT
        try:
            self.error_snackbar.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def get_employee_id_value(self) -> str:
        return self.employee_id_input.input_value()

    def get_page_title(self) -> str:
        return self.page.title()

    def get_current_url(self) -> str:
        return self.page.url
