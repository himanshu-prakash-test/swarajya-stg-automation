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

    # --- Locators ---

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

    @property
    def snackbar_message(self):
        return self.page.locator(".mat-mdc-snack-bar-label .mdc-snackbar__label")

    # --- Navigation ---

    def navigate(self):
        url = f"{self.base_url}{self.LOGIN_PATH}"
        log.info("Opening %s", url)
        self.page.goto(url, wait_until="networkidle", timeout=30_000)
        self.page.wait_for_timeout(1000)
        return self

    # --- Actions ---

    def enter_employee_id(self, emp_id: str):
        self.employee_id_input.fill(str(emp_id))
        return self

    def enter_password(self, password: str):
        self.password_input.fill(password)
        return self

    def click_sign_in(self):
        self.sign_in_button.click()
        return self

    def login(self, emp_id: str, password: str):
        self.enter_employee_id(emp_id)
        self.enter_password(password)
        self.click_sign_in()
        return self

    def click_forgot_password(self):
        self.forgot_password_link.click()
        return self

    # --- Queries ---

    def is_on_login_page(self) -> bool:
        url = self.page.url
        return (url.rstrip("/") == self.base_url.rstrip("/")
                or ("tfa-authcode" not in url
                    and "default" not in url
                    and "forgot" not in url))

    def is_employee_id_field_visible(self) -> bool:
        return self.employee_id_input.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_password_field_visible(self) -> bool:
        return self.password_input.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_sign_in_button_visible(self) -> bool:
        return self.sign_in_button.is_visible(timeout=self.DEFAULT_TIMEOUT)

    def is_sign_in_button_enabled(self) -> bool:
        return self.sign_in_button.is_enabled()

    def is_forgot_password_visible(self) -> bool:
        return self.forgot_password_link.is_visible(timeout=self.DEFAULT_TIMEOUT)

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
