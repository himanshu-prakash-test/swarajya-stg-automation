import time
from typing import Dict, List, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from vendor_pages.base_page import BasePage


class VendorPage(BasePage):
    """Page Object for Vendor Management (Create Vendor, List, Search, Validation)."""

    def __init__(self, page: Page):
        super().__init__(page)

    # ----------------- Navigation -----------------

    def open_vendor_list(self):
        """Navigate to Vendor Management list page."""
        # Try direct routes
        for route in ["/vendorManagement", "/vendorList", "/vendors", "/default"]:
            self.goto(route)
            self.wait_for_dom_ready()
            if self.is_visible("button:has-text('New Vendor'), button:has-text('Add Vendor'), button:has-text('Create Vendor'), table, mat-table"):
                return
        
        # Navigate via sidebar if direct route isn't sufficient
        sidebar_vendor = self.page.locator("a:has-text('Vendor'), [role='listitem']:has-text('Vendor'), a[href*='vendor']")
        if sidebar_vendor.count() and sidebar_vendor.first.is_visible():
            sidebar_vendor.first.click()
            self.wait_for_dom_ready()

    def open_create_vendor_form(self):
        """Open the Create / Add Vendor form."""
        for route in ["/addNewVendor", "/addVendor", "/createVendor", "/vendor/add"]:
            self.goto(route)
            self.wait_for_dom_ready()
            if self.is_visible("input[placeholder*='Vendor Name'], input[formcontrolname*='name'], input[name*='name'], button:has-text('Save')"):
                return

        # Fallback: go to list and click New Vendor button
        self.open_vendor_list()
        new_btn = self.page.locator("button:has-text('New Vendor'), button:has-text('Add Vendor'), button:has-text('Create Vendor'), a:has-text('New Vendor')").first
        if new_btn.is_visible():
            new_btn.click()
            self.wait_for_dom_ready()

    # ----------------- Form Field Interactions -----------------

    def fill_field(self, field_name: str, value: str) -> bool:
        """Fill a form input dynamically based on field name."""
        key = field_name.strip().lower()

        if "active" in key:
            checked = str(value).strip().lower() in ("ticked", "true", "yes", "1", "active")
            return self.set_active_checkbox(checked)

        if "country" in key:
            return self.select_country(value)

        # Field selector mapping
        selectors = {
            "vendor name": "input[placeholder*='Vendor Name'], input[formcontrolname*='vendorName'], input[formcontrolname*='name'], input[name*='name']",
            "name": "input[placeholder*='Vendor Name'], input[formcontrolname*='vendorName'], input[formcontrolname*='name']",
            "email": "input[type='email'], input[placeholder*='Email'], input[formcontrolname*='email'], input[name*='email']",
            "phone": "input[type='tel'], input[placeholder*='Phone'], input[formcontrolname*='phone'], input[placeholder*='Mobile'], input[name*='phone']",
            "address": "textarea[placeholder*='Address'], input[placeholder*='Address'], input[formcontrolname*='address']",
            "state": "input[placeholder*='State'], input[formcontrolname*='state'], mat-select[formcontrolname*='state']",
            "poc": "input[placeholder*='POC'], input[placeholder*='Contact Person'], input[placeholder*='Point of Contact'], input[formcontrolname*='poc']",
            "tax number": "input[placeholder*='Tax'], input[placeholder*='GST'], input[formcontrolname*='taxNumber'], input[formcontrolname*='tax']",
            "percentage": "input[placeholder*='Percentage'], input[placeholder*='%'], input[formcontrolname*='percentage']",
            "payment terms": "input[placeholder*='Payment Terms'], input[placeholder*='Days'], input[formcontrolname*='paymentTerms'], input[formcontrolname*='days']",
            "days": "input[placeholder*='Payment Terms'], input[placeholder*='Days'], input[formcontrolname*='paymentTerms'], input[formcontrolname*='days']",
        }

        sel = selectors.get(key)
        if not sel:
            for k, s in selectors.items():
                if k in key:
                    sel = s
                    break

        if not sel:
            sel = f"input[placeholder*='{field_name}'], input[formcontrolname*='{field_name}']"

        try:
            el = self.page.locator(sel).first
            el.wait_for(state="visible", timeout=4000)
            el.fill(str(value))
            self.log.info(f"Filled '{field_name}' = '{value}'")
            return True
        except Exception:
            # Fallback by generic index matching
            inputs = self.page.locator("input:not([type='hidden']), textarea").all()
            for inp in inputs:
                try:
                    ph = inp.get_attribute("placeholder") or ""
                    fcn = inp.get_attribute("formcontrolname") or ""
                    name = inp.get_attribute("name") or ""
                    if key in ph.lower() or key in fcn.lower() or key in name.lower():
                        inp.fill(str(value))
                        self.log.info(f"Filled '{field_name}' via attribute fallback = '{value}'")
                        return True
                except Exception:
                    pass
            self.log.warning(f"Could not locate field '{field_name}'")
            return False

    def select_country(self, country_name: str) -> bool:
        """Select country from dropdown or fill input."""
        dropdown_sel = "mat-select[formcontrolname*='country'], mat-select[placeholder*='Country'], select[name*='country']"
        try:
            el = self.page.locator(dropdown_sel).first
            if el.is_visible(timeout=2000):
                el.click()
                self.page.wait_for_selector("mat-option, option", state="visible", timeout=3000)
                opt = self.page.locator(f"mat-option:has-text('{country_name}'), option:has-text('{country_name}')").first
                if opt.is_visible():
                    opt.click()
                    return True
                first_opt = self.page.locator("mat-option, option").first
                first_opt.click()
                return True
        except Exception:
            pass

        # Text input fallback
        input_sel = "input[placeholder*='Country'], input[formcontrolname*='country']"
        try:
            self.fill(input_sel, country_name)
            return True
        except Exception:
            return False

    def set_active_checkbox(self, checked: bool = True) -> bool:
        """Toggle Active checkbox or slide-toggle."""
        chk_sel = "mat-checkbox, mat-slide-toggle, input[type='checkbox']"
        try:
            chk = self.page.locator(chk_sel).first
            chk.wait_for(state="visible", timeout=3000)
            is_checked = "mat-mdc-checkbox-checked" in (chk.get_attribute("class") or "") or chk.is_checked()
            if is_checked != checked:
                chk.click()
            self.log.info(f"Set Active status to {checked}")
            return True
        except Exception:
            return False

    # ----------------- Save, Modal & Cancel Actions -----------------

    def click_save(self):
        """Click Save / Submit button on form."""
        btn_sel = "button:has-text('Save'), button:has-text('Submit'), button[type='submit'], button.btn-save"
        self.click(btn_sel)
        self.log.info("Clicked Save button")

    def click_save_and_confirm(self, confirm: bool = True) -> str:
        """Click Save, handle confirmation popup modal, and return toast outcome."""
        self.click_save()

        # Handle confirmation dialog
        modal_sel = ".mat-mdc-dialog-container, .mat-dialog-container, .modal-dialog, [role='dialog']"
        try:
            self.page.locator(modal_sel).first.wait_for(state="visible", timeout=3000)
            if confirm:
                yes_btn = self.page.locator(
                    f"{modal_sel} button:has-text('Yes'), {modal_sel} button:has-text('Confirm'), {modal_sel} button:has-text('Save'), {modal_sel} button.btn-primary"
                ).first
                yes_btn.click()
                self.log.info("Confirmed Save popup (clicked Yes)")
            else:
                no_btn = self.page.locator(
                    f"{modal_sel} button:has-text('No'), {modal_sel} button:has-text('Cancel'), {modal_sel} button:has-text('Close')"
                ).first
                no_btn.click()
                self.log.info("Dismissed Save popup (clicked No)")
                return "Cancelled"
        except Exception:
            pass

        # Capture toast or confirmation outcome
        toast = self.get_toast(timeout=4000)
        self.log.info(f"Save confirmation outcome: '{toast}'")
        return toast

    def click_cancel(self) -> bool:
        """Click Cancel / Reset button."""
        btn_sel = "button:has-text('Cancel'), button:has-text('Reset'), button.btn-cancel, button:has-text('Back')"
        try:
            self.click(btn_sel)
            self.log.info("Clicked Cancel/Reset button")
            return True
        except Exception:
            return False

    # ----------------- List & Search Interactions -----------------

    def search_vendor(self, term: str) -> bool:
        """Search for a vendor in the vendor management list table."""
        search_sel = "input[placeholder*='Search'], input[type='search'], input.search-input"
        try:
            self.fill(search_sel, term)
            self.page.keyboard.press("Enter")
            self.wait_for_dom_ready()
            return True
        except Exception:
            return False

    def toggle_include_inactive(self, checked: bool = True) -> bool:
        """Toggle the Include Inactive checkbox."""
        chk_sel = "mat-checkbox:has-text('Inactive'), mat-checkbox:has-text('Include Inactive'), input[type='checkbox']"
        try:
            chk = self.page.locator(chk_sel).first
            chk.wait_for(state="visible", timeout=3000)
            is_checked = "mat-mdc-checkbox-checked" in (chk.get_attribute("class") or "") or chk.is_checked()
            if is_checked != checked:
                chk.click()
            self.wait_for_dom_ready()
            return True
        except Exception:
            return False

    def is_vendor_in_list(self, vendor_name: str) -> bool:
        """Check if vendor name is present in the table rows."""
        self.search_vendor(vendor_name)
        self.page.wait_for_timeout(1000)
        row_sel = f"tr:has-text('{vendor_name}'), mat-row:has-text('{vendor_name}'), td:has-text('{vendor_name}'), mat-cell:has-text('{vendor_name}')"
        return self.is_visible(row_sel, timeout=4000)

    # ----------------- Validation & Error Helpers -----------------

    def get_validation_errors(self) -> List[str]:
        """Collect visible inline validation error messages."""
        err_sel = "mat-error, .text-danger, .error-message, [role='alert'], .invalid-feedback"
        errors = []
        try:
            elements = self.page.locator(err_sel).all()
            for el in elements:
                if el.is_visible():
                    t = el.inner_text().strip()
                    if t and t not in errors:
                        errors.append(t)
        except Exception:
            pass
        return errors

    def is_form_invalid(self) -> bool:
        """Check if form or fields have ng-invalid or aria-invalid classes."""
        try:
            invalid_count = self.page.locator("form.ng-invalid, input.ng-invalid, mat-form-field.ng-invalid, [aria-invalid='true']").count()
            return invalid_count > 0
        except Exception:
            return False
