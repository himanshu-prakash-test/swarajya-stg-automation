"""Page object for Consultant Management on Swarajya staging."""

import logging
import os
import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

log = logging.getLogger(__name__)


class ConsultantPage:
    """Encapsulates page interactions for the Consultant Management workflow."""

    FIELD_NAME_MAP = {
        "first name": "firstname",
        "middle name": "middlename",
        "last name": "lastname",
        "phone": "phone",
        "personal email": "personal_email",
        "email": "personal_email",
        "address": "address",
        "monthly fees": "monthly_fees",
        "tds percentage": "tds_percentage",
        "bank name": "bank_name",
        "account number": "account_number",
        "ifsc code": "ifsc",
        "ifsc": "ifsc",
        "bank branch": "bank_branch",
        "account type": "account_type",
        "active": "isActive",
    }

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.list_path = os.environ.get("CONSULTANT_LIST_PATH", "/consultantdetails")

    # ── Navigation & Overlays ──

    def dismiss_intro_if_present(self):
        """Dismiss intro tutorial overlay if visible."""
        try:
            skip_btn = self.page.locator("button:has-text('Skip Intro'), .close-drawer, button:has-text('close')").first
            if skip_btn.is_visible(timeout=1_500):
                skip_btn.click(force=True)
                time.sleep(0.5)
        except Exception:
            pass

    def navigate_to_list(self):
        """Navigate to the Consultant Dashboard page."""
        url = f"{self.base_url}{self.list_path}"
        if not self.page.url.startswith(url):
            log.info("Navigating to Consultant list: %s", url)
            self.page.goto(url, wait_until="domcontentloaded", timeout=30_000)

        self.dismiss_intro_if_present()

        # Dynamic wait for table, search, or new consultant button
        try:
            self.page.locator("button:has-text('New Consultant'), input[placeholder*='Search' i], tbody tr").first.wait_for(
                state="visible", timeout=10_000
            )
        except Exception:
            # Fallback: try navigating via /finance
            log.warning("Consultant list not loaded directly; trying via /finance")
            self.page.goto(f"{self.base_url}/finance", wait_until="domcontentloaded", timeout=30_000)
            self.page.locator("mat-card:has-text('Consultant Management'), div:has-text('Consultant Management')").first.click()
            self.dismiss_intro_if_present()
            self.page.locator("button:has-text('New Consultant'), tbody tr").first.wait_for(state="visible", timeout=10_000)

        return self

    def click_new_consultant(self):
        """Click the 'New Consultant' button to open the creation form."""
        self.navigate_to_list()
        self.dismiss_intro_if_present()
        btn = self.page.locator("button:has-text('New Consultant')").first
        btn.wait_for(state="visible", timeout=8_000)
        btn.click()

        # Wait for form input fields to appear
        self.page.locator("input[name='firstname'], input[name='lastname']").first.wait_for(state="visible", timeout=8_000)
        return self

    # ── Form Operations ──

    def fill_field(self, field_label: str, value: str):
        """Fill a specific form field by human label."""
        key = str(field_label).strip().lower().lstrip("•-* ").strip()
        attr_name = self.FIELD_NAME_MAP.get(key, key)
        val_str = str(value) if value is not None else ""

        if attr_name == "isActive" or "active" in key:
            checked = val_str.lower() in ("ticked", "true", "yes", "1", "active")
            self.set_active_checkbox(checked)
            return

        if attr_name == "account_type" or "account type" in key:
            if val_str:
                self.select_account_type(val_str)
            return

        if attr_name == "address":
            field = self.page.locator("textarea[name='address'], textarea#mat-input-5").first
        else:
            field = self.page.locator(f"input[name='{attr_name}'], [name='{attr_name}']").first

        if field.count():
            field.wait_for(state="visible", timeout=3_000)
            try:
                field.fill(val_str)
            except Exception:
                # Handle non-numeric text input on input[type='number']
                try:
                    field.evaluate("(el, val) => { el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }", val_str)
                except Exception:
                    pass

    def select_account_type(self, account_type: str):
        """Select Account Type from dropdown (Savings / Current)."""
        select_el = self.page.locator("mat-select[name='account_type'], mat-select").first
        select_el.click()
        time.sleep(0.5)
        option = self.page.locator(f"mat-option:has-text('{account_type}')").first
        if option.is_visible(timeout=3_000):
            option.click()
        else:
            # Fallback to first available option
            self.page.locator("mat-option").first.click()
        time.sleep(0.3)

    def set_active_checkbox(self, is_active: bool):
        """Set the Active checkbox state."""
        chk = self.page.locator("mat-checkbox[name='isActive'], input[name='isActive']").first
        if not chk.count():
            return
        is_checked = "mat-mdc-checkbox-checked" in (chk.get_attribute("class") or "") or chk.is_checked()
        if is_checked != is_active:
            chk.click()

    def fill_consultant_form(self, fields_dict: dict):
        """Fill all fields present in the dictionary."""
        for label, val in fields_dict.items():
            self.fill_field(label, val)
        return self

    def click_save(self, force: bool = False):
        """Click Save if enabled; otherwise log that validation prevented submission."""
        if not self.is_save_button_enabled():
            log.info("Save button is disabled as expected by validation rules.")
            return self
        save_btn = self.page.locator("button:has-text('Save'), button[type='submit']").first
        try:
            save_btn.scroll_into_view_if_needed()
            save_btn.click(timeout=3_000, force=force)
        except Exception as e:
            log.info("Save button click was not completed: %s", e)
        return self

    def click_cancel(self):
        """Click the Cancel button on the form."""
        cancel_btn = self.page.locator("button:has-text('Cancel')").first
        if cancel_btn.is_visible(timeout=3_000):
            cancel_btn.click()
        return self

    def handle_confirmation_dialog(self, action: str = "Yes"):
        """Handle Yes/No on confirmation modal popup."""
        dialog = self.page.locator("mat-dialog-container, .modal-dialog, .swal2-popup, .cdk-overlay-pane").first
        try:
            dialog.wait_for(state="visible", timeout=4_000)
            btn = dialog.locator(f"button:has-text('{action}')").first
            btn.wait_for(state="visible", timeout=3_000)
            btn.click()
            time.sleep(1)
            return True
        except Exception:
            return False

    # ── List & Search Operations ──

    def search_consultant(self, query: str):
        """Search for a consultant by name or keyword."""
        self.navigate_to_list()
        search_input = self.page.locator("input[placeholder*='Search' i]").first
        if search_input.is_visible(timeout=5_000):
            search_input.fill(query)
            search_input.press("Enter")
            self.page.wait_for_load_state("networkidle")
            time.sleep(1)
        return self

    def is_consultant_in_list(self, name: str) -> bool:
        """Check if consultant appears in the table."""
        self.navigate_to_list()
        self.search_consultant(name)
        rows = self.page.locator("tbody tr")
        if not rows.count():
            return False
        for i in range(rows.count()):
            row_text = rows.nth(i).inner_text()
            if name.lower() in row_text.lower():
                return True
        return False

    def is_save_button_enabled(self) -> bool:
        """Check if Save button is enabled."""
        save_btn = self.page.locator("button:has-text('Save')").first
        if not save_btn.count():
            return False
        disabled = save_btn.get_attribute("disabled") is not None or "mat-mdc-button-disabled" in (save_btn.get_attribute("class") or "")
        return not disabled

    def get_validation_errors(self) -> list:
        """Retrieve all visible validation error messages."""
        errors = []
        error_locators = self.page.locator("mat-error, .error-message, .invalid-feedback, .mat-mdc-snack-bar-label, simple-snack-bar")
        count = error_locators.count()
        for i in range(count):
            txt = error_locators.nth(i).inner_text().strip()
            if txt and txt not in errors:
                errors.append(txt)
        return errors
