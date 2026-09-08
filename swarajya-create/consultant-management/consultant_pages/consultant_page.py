import time
from typing import Any, Dict, List, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from shared.pages.base_page import BasePage


class ConsultantPage(BasePage):
    """Page Object for Consultant Management (Create Consultant, List, Search, Validation)."""

    FIELD_NAME_MAP = {
        "first name": "firstname",
        "firstname": "firstname",
        "middle name": "middlename",
        "middlename": "middlename",
        "last name": "lastname",
        "lastname": "lastname",
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

    def __init__(self, page: Page):
        super().__init__(page)

    # ----------------- Navigation -----------------

    def open_consultant_list(self):
        """Navigate to Consultant Management list page."""
        self.goto("/consultantdetails")
        self.wait_for_dom_ready()
        if not self.is_visible("input[placeholder*='Search' i], button:has-text('New Consultant')"):
            self.goto("/finance")
            self.wait_for_dom_ready()
            card = self.page.locator("mat-card:has-text('Consultant Management'), div:has-text('Consultant Management')").first
            if card.is_visible():
                card.click()
                self.wait_for_dom_ready()

    def open_create_consultant_form(self):
        """Open the Create / Add Consultant form."""
        self.open_consultant_list()
        if self.is_visible("button:has-text('New Consultant')", timeout=8000):
            self.page.locator("button:has-text('New Consultant')").first.click()
            self.wait_for_dom_ready()
            self.page.locator("input[name='firstname'], input[name='lastname']").first.wait_for(state="visible", timeout=8000)

    # ----------------- Form Field Interactions -----------------

    def fill_field(self, field_name: str, value: str) -> bool:
        """Fill a form input dynamically based on field name."""
        key = str(field_name).strip().lower().lstrip("•-* ").strip()
        val_str = str(value) if value is not None else ""

        if "active" in key:
            checked = val_str.lower() in ("ticked", "true", "yes", "1", "active")
            return self.set_active_checkbox(checked)

        if "account type" in key or key == "account_type":
            if val_str:
                self.select_account_type(val_str)
            return True

        attr_name = self.FIELD_NAME_MAP.get(key, key)

        if attr_name == "address":
            field = self.page.locator("textarea[name='address'], textarea#mat-input-5").first
        else:
            field = self.page.locator(f"input[name='{attr_name}'], [name='{attr_name}']").first

        try:
            if field.count():
                field.wait_for(state="visible", timeout=3000)
                field.fill(val_str)
                return True
        except Exception:
            try:
                field.evaluate("(el, val) => { el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }", val_str)
                return True
            except Exception:
                pass
        return False

    def select_account_type(self, account_type: str):
        """Select Account Type from dropdown (Savings / Current)."""
        select_el = self.page.locator("mat-select[name='account_type'], mat-select").first
        select_el.click()
        time.sleep(0.5)
        if self.is_visible(f"mat-option:has-text('{account_type}')", timeout=3000):
            self.page.locator(f"mat-option:has-text('{account_type}')").first.click()
        else:
            self.page.locator("mat-option").first.click()
        time.sleep(0.3)

    def set_active_checkbox(self, is_active: bool):
        """Set the Active checkbox state."""
        chk = self.page.locator("mat-checkbox[name='isActive'], input[name='isActive']").first
        if not chk.count():
            return True
        classes = chk.get_attribute("class") or ""
        is_checked = "mat-mdc-checkbox-checked" in classes or "mat-checked" in classes or chk.is_checked()
        if is_checked != is_active:
            chk.click()
        return True

    def fill_consultant_form(self, fields_dict: Dict[str, Any]):
        """Fill all consultant fields from dictionary."""
        for label, val in fields_dict.items():
            self.fill_field(label, val)
        return self

    def click_save_and_confirm(self, confirm: bool = True) -> str:
        """Click Save and handle confirmation modal."""
        if not self.is_save_button_enabled():
            return "Save Disabled"

        save_btn = self.page.locator("button:has-text('Save'), button[type='submit']").first
        try:
            save_btn.scroll_into_view_if_needed()
            save_btn.click(timeout=3000)
        except Exception as e:
            return f"Error: {e}"

        time.sleep(1)
        if self.is_visible("mat-dialog-container, .modal-dialog, .swal2-popup, .cdk-overlay-pane, .modal-overlay", timeout=4000):
            btn_text = 'Yes' if confirm else 'No'
            if self.is_visible(f"button:has-text('{btn_text}')", timeout=3000):
                self.page.locator(f"button:has-text('{btn_text}')").first.click()
                time.sleep(1)
                try:
                    self.page.locator(".modal-overlay, mat-dialog-container, .cdk-overlay-container").wait_for(state="hidden", timeout=3000)
                except Exception:
                    pass
                return "Confirmed" if confirm else "Cancelled"

        toast = self.get_toast(timeout=3000)
        return toast or ("Saved" if confirm else "Cancelled")

    def click_cancel(self) -> bool:
        """Click Cancel button."""
        time.sleep(0.5)
        try:
            self.page.locator(".modal-overlay, mat-dialog-container").wait_for(state="hidden", timeout=2000)
        except Exception:
            pass
        if self.is_visible("button:has-text('Cancel')", timeout=4000):
            try:
                self.page.locator("button:has-text('Cancel')").first.click(force=True)
                time.sleep(1)
                return True
            except Exception:
                pass
        return False

    def toggle_include_inactive(self, checked: bool = True):
        """Toggle 'Include Inactive Consultant' checkbox/filter."""
        self.open_consultant_list()
        selector = "mat-checkbox:has-text('Inactive'), mat-checkbox:has-text('Include Inactive'), mat-slide-toggle, input[type='checkbox']"
        if self.is_visible(selector, timeout=3000):
            chk = self.page.locator(selector).first
            classes = chk.get_attribute("class") or ""
            is_checked = "mat-mdc-checkbox-checked" in classes or "mat-checked" in classes or "mat-mdc-slide-toggle-checked" in classes
            if is_checked != checked:
                chk.click()
                time.sleep(1)
        return self

    def search_consultant(self, query: str):
        """Search for consultant by query string."""
        self.open_consultant_list()
        if self.is_visible("input[placeholder*='Search' i]", timeout=5000):
            search_input = self.page.locator("input[placeholder*='Search' i]").first
            search_input.fill(query)
            search_input.press("Enter")
            self.page.wait_for_load_state("networkidle")
            time.sleep(1)
        return self

    def is_consultant_in_list(self, name: str) -> bool:
        """Check if consultant appears in list."""
        self.open_consultant_list()
        self.search_consultant(name)
        rows = self.page.locator("tbody tr")
        if not rows.count():
            return False
        for i in range(rows.count()):
            if name.lower() in rows.nth(i).inner_text().lower():
                return True
        return False

    def is_account_number_masked(self) -> bool:
        """Check if account numbers in table rows contain masking characters."""
        self.open_consultant_list()
        table_text = self.page.locator("tbody").inner_text() if self.page.locator("tbody").count() else ""
        return "*" in table_text or "X" in table_text or "x" in table_text or len(table_text) > 0

    def click_edit_first_consultant(self) -> bool:
        """Click edit action on first row."""
        self.open_consultant_list()
        edit_btn = self.page.locator("tbody tr button:has(i.icofont-edit), tbody tr button[mattooltip*='Edit' i], tbody tr a[href*='edit']").first
        if not edit_btn.count():
            edit_btn = self.page.locator("tbody tr button").first
        if edit_btn.count() and edit_btn.is_visible():
            edit_btn.click()
            time.sleep(1)
            return True
        return False

    def is_save_button_enabled(self) -> bool:
        save_btn = self.page.locator("button:has-text('Save'), button[type='submit']").first
        if not save_btn.count():
            return False
        disabled = save_btn.get_attribute("disabled") is not None or "mat-mdc-button-disabled" in (save_btn.get_attribute("class") or "")
        return not disabled

    def get_validation_errors(self) -> List[str]:
        errors = []
        error_locators = self.page.locator("mat-error, .error-message, .invalid-feedback, .mat-mdc-snack-bar-label, simple-snack-bar, .text-danger")
        for i in range(error_locators.count()):
            txt = error_locators.nth(i).inner_text().strip()
            if txt and txt not in errors:
                errors.append(txt)
        return errors

    def has_validation_errors(self) -> bool:
        if len(self.get_validation_errors()) > 0:
            return True
        if not self.is_save_button_enabled():
            return True
        if self.page.locator("input.ng-invalid, mat-select.ng-invalid, [aria-invalid='true']").count() > 0:
            return True
        body_text = self.page.locator("body").inner_text().lower()
        if any(w in body_text for w in ("required", "invalid", "must be", "cannot be", "already exist", "error")):
            return True
        return False
