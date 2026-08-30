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
        return self.page.locator("input[name='email'], input#mat-input-0, input[type='text']").first

    @property
    def password_input(self):
        return self.page.locator("input[name='password'], input#mat-input-1, input[type='password']").first

    @property
    def sign_in_button(self):
        return self.page.get_by_role("button", name="Sign In")

    @property
    def forgot_password_link(self):
        return self.page.get_by_role("link", name="Forgot Password")

    @property
    def error_snackbar(self):
        return self.page.locator("simple-snack-bar, mat-snack-bar-container, .mat-mdc-snack-bar-container").first

    @property
    def snackbar_message(self):
        return self.page.locator(".mat-mdc-snack-bar-label .mdc-snackbar__label, simple-snack-bar span").first

    # --- Navigation ---

    def navigate(self):
        url = f"{self.base_url}{self.LOGIN_PATH}"
        log.info("Opening %s", url)
        backoffs = [3000, 6000, 12000, 20000, 30000]
        for attempt in range(len(backoffs) + 1):
            try:
                if self.page.url.rstrip("/") == self.base_url.rstrip("/"):
                    response = self.page.reload(wait_until="domcontentloaded", timeout=30_000)
                else:
                    response = self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)

                page_content = self.page.content().lower()
                if (response and response.status == 503) or "service unavailable" in page_content or "503" in page_content:
                    if attempt < len(backoffs):
                        wait_ms = backoffs[attempt]
                        log.warning("Staging 503 detected. Waiting %ds before retry %d...", wait_ms // 1000, attempt + 1)
                        self.page.wait_for_timeout(wait_ms)
                        continue

                self.employee_id_input.wait_for(state="visible", timeout=10_000)
                break
            except Exception:
                try:
                    page_content = self.page.content().lower()
                    if "service unavailable" in page_content or "503" in page_content:
                        if attempt < len(backoffs):
                            wait_ms = backoffs[attempt]
                            log.warning("503 in exception. Waiting %ds before retry %d...", wait_ms // 1000, attempt + 1)
                            self.page.wait_for_timeout(wait_ms)
                            continue
                except Exception:
                    pass
        return self

    def wait_for_login_page(self, timeout: int = 10_000):
        """Dynamically wait for login inputs to become visible."""
        self.employee_id_input.wait_for(state="visible", timeout=timeout)
        return self

    # --- Actions ---

    def enter_employee_id(self, emp_id: str):
        try:
            self.employee_id_input.wait_for(state="visible", timeout=10_000)
        except Exception:
            pass
        self.employee_id_input.fill(str(emp_id))
        return self

    def enter_password(self, password: str):
        try:
            self.password_input.wait_for(state="visible", timeout=10_000)
        except Exception:
            pass
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

    def is_employee_id_field_visible(self, timeout: int = None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            self.employee_id_input.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_password_field_visible(self, timeout: int = None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            self.password_input.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_sign_in_button_visible(self, timeout: int = None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            self.sign_in_button.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_sign_in_button_enabled(self) -> bool:
        return self.sign_in_button.is_enabled()

    def is_forgot_password_visible(self, timeout: int = None) -> bool:
        timeout = timeout or self.DEFAULT_TIMEOUT
        try:
            self.forgot_password_link.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def is_password_masked(self) -> bool:
        try:
            return self.password_input.get_attribute("type") == "password"
        except Exception:
            return False

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
