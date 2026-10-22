"""
Page Object Model for Consultant Management:
- Consultant Dashboard (/consultantdetails)
- Create New Consultant Form (/addfreelancer)
- Edit Consultant Form
"""

import logging
import re
from typing import Any, Dict, List, Optional
from playwright.sync_api import Page, Locator

log = logging.getLogger(__name__)


class ConsultantPage:
    """Page object encapsulating interactions on Consultant List and Create Consultant pages."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # --- Navigation ---

    def navigate_to_finance(self) -> None:
        """Navigate to Finance module (/finance)."""
        url = f"{self.base_url}/finance"
        log.info("Navigating to Finance: %s", url)
        self.page.goto(url, wait_until="domcontentloaded", timeout=25_000)
        self.dismiss_intro_tour()
        try:
            self.page.wait_for_selector("text=Consultant Management, .card, mat-card", timeout=15_000)
        except Exception:
            pass

    def navigate_to_consultant_dashboard(self) -> None:
        """Navigate to Consultant Dashboard (/consultantdetails)."""
        # If an edit or modal dialog is currently open, dismiss it
        try:
            if self.page.locator("mat-dialog-container, .modal-dialog").count() > 0:
                self.click_cancel()
        except Exception:
            pass

        if "consultantdetails" in self.page.url and self.table_rows.count() > 0:
            self.dismiss_intro_tour()
            return

        url = f"{self.base_url}/consultantdetails"
        log.info("Navigating to Consultant Dashboard: %s", url)
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=25_000)
            self.dismiss_intro_tour()
            self.page.wait_for_selector(
                "button:has-text('New Consultant'), table, .mat-mdc-table, tbody tr",
                timeout=15_000,
            )
        except Exception:
            # Fallback: navigate via Finance page
            log.info("Direct navigation slow, routing via Finance page...")
            self.navigate_to_finance()
            cm_link = self.page.locator("text=Consultant Management").first
            if cm_link.is_visible(timeout=5_000):
                cm_link.click()
                self.page.wait_for_url(lambda u: "consultantdetails" in u, timeout=15_000)
                self.dismiss_intro_tour()

        try:
            self.table_rows.first.wait_for(state="visible", timeout=6_000)
        except Exception:
            pass
        self.dismiss_intro_tour()

    def navigate_to_add_consultant(self) -> None:
        """Navigate directly or via 'New Consultant' button to the creation form (/addfreelancer)."""
        if "addfreelancer" in self.page.url and self.first_name_input.is_visible():
            self.dismiss_intro_tour()
            return

        self.navigate_to_consultant_dashboard()
        new_btn = self.new_consultant_button
        try:
            if new_btn.is_visible(timeout=5_000):
                new_btn.click()
                self.page.wait_for_url(lambda u: "addfreelancer" in u, timeout=12_000)
        except Exception:
            pass

        if "addfreelancer" not in self.page.url:
            self.page.goto(f"{self.base_url}/addfreelancer", wait_until="domcontentloaded", timeout=25_000)

        try:
            self.first_name_input.wait_for(state="visible", timeout=15_000)
        except Exception:
            pass

        self.dismiss_intro_tour()

    def dismiss_intro_tour(self) -> None:
        """Dismiss intro walkthrough modal if present on page."""
        try:
            skip_btn = self.page.locator("button:has-text('Skip Intro'), button:has-text('close')").first
            if skip_btn.is_visible(timeout=1_500):
                skip_btn.click()
                self.page.wait_for_timeout(400)
        except Exception:
            pass

    # --- Locators: Form Fields ---

    @property
    def first_name_input(self) -> Locator:
        return self.page.locator("input[name='firstname']")

    @property
    def middle_name_input(self) -> Locator:
        return self.page.locator("input[name='middlename']")

    @property
    def last_name_input(self) -> Locator:
        return self.page.locator("input[name='lastname']")

    @property
    def phone_input(self) -> Locator:
        return self.page.locator("input[name='phone']")

    @property
    def personal_email_input(self) -> Locator:
        return self.page.locator("input[name='personal_email']")

    @property
    def address_textarea(self) -> Locator:
        return self.page.locator("textarea[name='address']")

    @property
    def monthly_fees_input(self) -> Locator:
        return self.page.locator("input[name='monthly_fees']")

    @property
    def tds_percentage_input(self) -> Locator:
        return self.page.locator("input[name='tds_percentage']")

    @property
    def bank_name_input(self) -> Locator:
        return self.page.locator("input[name='bank_name']")

    @property
    def account_number_input(self) -> Locator:
        return self.page.locator("input[name='account_number']")

    @property
    def ifsc_code_input(self) -> Locator:
        return self.page.locator("input[name='ifsc'], input[name='ifsc_code']")

    @property
    def bank_branch_input(self) -> Locator:
        return self.page.locator("input[name='bank_branch']")

    @property
    def account_type_select(self) -> Locator:
        return self.page.locator("mat-select[name='account_type']")

    @property
    def active_checkbox(self) -> Locator:
        return self.page.locator("mat-checkbox[name='isActive'], input[name='isActive']").first

    @property
    def save_button(self) -> Locator:
        return self.page.locator("button:has-text('Save'), button[type='submit']").first

    @property
    def cancel_button(self) -> Locator:
        return self.page.locator("button:has-text('Cancel'), button:has-text('Close'), button:has(mat-icon:has-text('close'))").first

    @property
    def new_consultant_button(self) -> Locator:
        return self.page.locator("button:has-text('New Consultant')").first

    @property
    def search_input(self) -> Locator:
        return self.page.locator("input[placeholder*='Search' i]").first

    @property
    def include_inactive_checkbox(self) -> Locator:
        return self.page.locator("mat-checkbox:has-text('Inactive'), mat-checkbox:has-text('Include Inactive'), input[type='checkbox']").first

    @property
    def table_rows(self) -> Locator:
        return self.page.locator("tbody tr")

    # --- Actions: Field Inputs ---

    def enter_first_name(self, value: Any) -> None:
        self.first_name_input.fill(str(value) if value is not None else "")

    def enter_middle_name(self, value: Any) -> None:
        self.middle_name_input.fill(str(value) if value is not None else "")

    def enter_last_name(self, value: Any) -> None:
        self.last_name_input.fill(str(value) if value is not None else "")

    def enter_phone(self, value: Any) -> None:
        self.phone_input.fill(str(value) if value is not None else "")

    def enter_personal_email(self, value: Any) -> None:
        self.personal_email_input.fill(str(value) if value is not None else "")

    def enter_address(self, value: Any) -> None:
        self.address_textarea.fill(str(value) if value is not None else "")

    def enter_monthly_fees(self, value: Any) -> None:
        val_str = str(value) if value is not None else ""
        try:
            self.monthly_fees_input.fill(val_str)
        except Exception:
            try:
                self.monthly_fees_input.evaluate(
                    "(el, val) => { el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }",
                    val_str,
                )
            except Exception:
                pass

    def enter_tds_percentage(self, value: Any) -> None:
        val_str = str(value) if value is not None else ""
        try:
            self.tds_percentage_input.fill(val_str)
        except Exception:
            try:
                self.tds_percentage_input.evaluate(
                    "(el, val) => { el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }",
                    val_str,
                )
            except Exception:
                pass

    def enter_bank_name(self, value: Any) -> None:
        self.bank_name_input.fill(str(value) if value is not None else "")

    def enter_account_number(self, value: Any) -> None:
        self.account_number_input.fill(str(value) if value is not None else "")

    def enter_ifsc_code(self, value: Any) -> None:
        self.ifsc_code_input.fill(str(value) if value is not None else "")

    def enter_bank_branch(self, value: Any) -> None:
        self.bank_branch_input.fill(str(value) if value is not None else "")

    def select_account_type(self, account_type: str) -> None:
        """Select Account Type from dropdown (Savings / Current)."""
        sel = self.account_type_select
        sel.scroll_into_view_if_needed()
        sel.click()
        try:
            opt = self.page.locator(f"mat-option:has-text('{account_type}')").first
            opt.wait_for(state="visible", timeout=3_000)
            opt.click()
        except Exception:
            # Fallback to first option
            fallback = self.page.locator("mat-option").first
            if fallback.is_visible(timeout=2_000):
                fallback.click()
        self.page.wait_for_timeout(300)

    def set_active_checkbox(self, is_active: bool) -> None:
        """Set the Active checkbox state."""
        chk = self.active_checkbox
        if not chk.count():
            return
        classes = chk.get_attribute("class") or ""
        is_checked = "mat-mdc-checkbox-checked" in classes or "mat-checked" in classes or chk.is_checked()
        if is_checked != is_active:
            chk.click()
            self.page.wait_for_timeout(300)

    # --- Actions: Form Submission & Confirmation ---

    def is_save_button_enabled(self) -> bool:
        """Check if Save button is currently enabled."""
        btn = self.save_button
        if not btn.count() or not btn.is_visible():
            return False
        disabled_attr = btn.get_attribute("disabled") is not None
        classes = btn.get_attribute("class") or ""
        is_mat_disabled = "mat-mdc-button-disabled" in classes or "disabled" in classes
        return not (disabled_attr or is_mat_disabled)

    def click_save_and_confirm(self, confirm: bool = True) -> str:
        """
        Click Save and handle confirmation modal.
        Returns status string: 'Confirmed', 'Cancelled', 'Save Disabled', or toast message.
        """
        if not self.is_save_button_enabled():
            log.info("Save button is disabled; form validation in effect.")
            return "Save Disabled"

        save_btn = self.save_button
        save_btn.scroll_into_view_if_needed()
        save_btn.click()

        # Check for confirmation popup / modal
        modal_btn_selector = f"button:has-text('{'Yes' if confirm else 'No'}')"
        try:
            confirm_btn = self.page.locator(modal_btn_selector).first
            confirm_btn.wait_for(state="visible", timeout=4_000)
            confirm_btn.click()
            self.page.wait_for_timeout(600)
            return "Confirmed" if confirm else "Cancelled"
        except Exception:
            pass

        # Check for toast / snackbar notification
        toast = self.get_toast_text(timeout=3_000)
        if toast:
            return toast

        return "Saved" if confirm else "Cancelled"

    def click_cancel(self) -> bool:
        """Click Cancel or Close button and return to dashboard."""
        cancel_btn = self.cancel_button
        try:
            if cancel_btn.is_visible(timeout=3_000):
                cancel_btn.click()
                self.page.wait_for_timeout(600)
                try:
                    self.page.locator("mat-dialog-container, .cdk-overlay-backdrop").wait_for(state="hidden", timeout=3_000)
                except Exception:
                    pass
                return True
        except Exception:
            pass
        return False

    def get_toast_text(self, timeout: int = 3_000) -> Optional[str]:
        """Fetch toast or snackbar notification message."""
        toast_loc = self.page.locator(".mat-mdc-snack-bar-label, simple-snack-bar, .toast, .swal2-title").first
        try:
            toast_loc.wait_for(state="visible", timeout=timeout)
            return toast_loc.inner_text().strip()
        except Exception:
            return None

    # --- Actions: Table & Dashboard ---

    def search_consultant(self, query: str) -> None:
        """Search for consultant by query string."""
        self.navigate_to_consultant_dashboard()
        s_input = self.search_input
        s_input.wait_for(state="visible", timeout=5_000)
        s_input.fill(query)
        s_input.press("Enter")
        self.page.wait_for_timeout(800)

    def is_consultant_in_list(self, name: str) -> bool:
        """Check if consultant name appears in table."""
        self.navigate_to_consultant_dashboard()
        self.search_consultant(name)
        rows = self.table_rows
        count = rows.count()
        if count == 0:
            return False
        for i in range(count):
            row_text = rows.nth(i).inner_text().lower()
            if name.lower() in row_text:
                return True
        return False

    def toggle_include_inactive(self, checked: bool = True) -> None:
        """Toggle 'Include Inactive Consultant' checkbox/filter."""
        self.navigate_to_consultant_dashboard()
        chk = self.include_inactive_checkbox
        try:
            chk.wait_for(state="visible", timeout=3_000)
            classes = chk.get_attribute("class") or ""
            is_checked = "mat-mdc-checkbox-checked" in classes or "mat-checked" in classes or chk.is_checked()
            if is_checked != checked:
                chk.click()
                self.page.wait_for_timeout(800)
        except Exception:
            pass

    def is_account_number_masked(self) -> bool:
        """Check if account numbers in table rows contain masking characters (* or X)."""
        self.navigate_to_consultant_dashboard()
        try:
            self.table_rows.first.wait_for(state="visible", timeout=6_000)
        except Exception:
            pass
        tbody = self.page.locator("tbody")
        if not tbody.count():
            return False
        text = tbody.inner_text()
        return "*" in text or "X" in text

    def click_edit_first_consultant(self) -> bool:
        """Click edit action on the first table row."""
        self.navigate_to_consultant_dashboard()
        edit_btn = self.page.locator("tbody tr button:has-text('edit'), tbody tr mat-icon:has-text('edit'), tbody tr .icofont-edit").first
        try:
            edit_btn.wait_for(state="visible", timeout=4_000)
            edit_btn.click()
            self.page.wait_for_timeout(800)
            return True
        except Exception:
            return False

    def get_validation_errors(self) -> List[str]:
        """Collect all visible validation errors and hints."""
        errors = []
        error_locs = self.page.locator("mat-error, .error-message, .invalid-feedback, .text-danger, .mat-mdc-snack-bar-label")
        for i in range(error_locs.count()):
            loc = error_locs.nth(i)
            if loc.is_visible():
                txt = loc.inner_text().strip()
                if txt and txt not in errors:
                    errors.append(txt)
        return errors

    def has_validation_errors(self) -> bool:
        """Determine if validation errors, invalid states, or disabled save exists."""
        if len(self.get_validation_errors()) > 0:
            return True
        if not self.is_save_button_enabled():
            return True
        if self.page.locator("input.ng-invalid, mat-select.ng-invalid, textarea.ng-invalid").count() > 0:
            return True
        return False
