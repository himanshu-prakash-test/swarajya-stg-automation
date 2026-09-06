import time
from typing import Dict, List, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from shared.pages.base_page import BasePage


class VendorPage(BasePage):
    """Page Object for Vendor Management (Create Vendor, List, Search, Validation)."""

    def __init__(self, page: Page):
        super().__init__(page)

    # ----------------- Navigation -----------------

    # ----------------- Navigation -----------------

    def open_vendor_list(self):
        """Navigate to Vendor Management list page."""
        self.goto("/vendordetails")
        self.wait_for_dom_ready()
        try:
            self.page.locator("input[placeholder*='Search'], button:has-text('New Vendor'), table").first.wait_for(state="visible", timeout=8000)
        except Exception:
            pass

    def open_create_vendor_form(self):
        """Open the Create / Add Vendor form."""
        self.goto("/addvendor")
        self.wait_for_dom_ready()
        try:
            self.page.locator("input[name='vendor_name'], input#mat-input-0, button:has-text('Save')").first.wait_for(state="visible", timeout=8000)
        except Exception:
            pass

    # ----------------- Form Field Interactions -----------------

    def fill_field(self, field_name: str, value: str) -> bool:
        """Fill a form input dynamically based on field name."""
        key = field_name.strip().lower()

        if "active" in key:
            checked = str(value).strip().lower() in ("ticked", "true", "yes", "1", "active")
            return self.set_active_checkbox(checked)

        if "country" in key:
            return self.select_country(value)

        # Exact staging form field mapping
        selectors = {
            "vendor name": "input[name='vendor_name'], input#mat-input-0, input[placeholder*='Vendor Name']",
            "name": "input[name='vendor_name'], input#mat-input-0",
            "vendor address": "textarea[name='vendor_address'], textarea#mat-input-1",
            "address": "textarea[name='vendor_address'], textarea#mat-input-1",
            "vendor state": "input[name='vendor_state'], input#mat-input-2",
            "state": "input[name='vendor_state'], input#mat-input-2",
            "vendor phone": "input[name='vendor_phone'], input[type='tel'], input#mat-input-3",
            "phone": "input[name='vendor_phone'], input[type='tel'], input#mat-input-3",
            "vendor email": "input[name='vendor_email'], input[type='email'], input#mat-input-4",
            "email": "input[name='vendor_email'], input[type='email'], input#mat-input-4",
            "vendor poc": "input[name='vendor_poc'], input#mat-input-5",
            "poc": "input[name='vendor_poc'], input#mat-input-5",
            "vendor tax number": "input[name='vendor_tax_number'], input#mat-input-6",
            "tax number": "input[name='vendor_tax_number'], input#mat-input-6",
            "payment terms (days)": "input[name='payment_terms'], input#mat-input-7",
            "payment terms": "input[name='payment_terms'], input#mat-input-7",
            "days": "input[name='payment_terms'], input#mat-input-7",
            "tds percentage (%)": "input[name='tds_percentage'], input#mat-input-8",
            "percentage": "input[name='tds_percentage'], input#mat-input-8",
        }

        sel = selectors.get(key)
        if not sel:
            for k, s in selectors.items():
                if k in key:
                    sel = s
                    break

        if not sel:
            sel = f"input[name*='{field_name}'], input[placeholder*='{field_name}']"

        try:
            el = self.page.locator(sel).first
            el.wait_for(state="visible", timeout=3000)
            try:
                el.fill(str(value))
            except Exception:
                el.evaluate("(input, val) => { input.value = val; input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true })); }", str(value))
            self.log.info(f"Filled '{field_name}' = '{value}'")
            return True
        except Exception:
            # Fallback by input search
            inputs = self.page.locator("input:not([type='hidden']), textarea").all()
            for inp in inputs:
                try:
                    name = inp.get_attribute("name") or ""
                    ph = inp.get_attribute("placeholder") or ""
                    if key in name.lower() or key in ph.lower():
                        try:
                            inp.fill(str(value))
                        except Exception:
                            inp.evaluate("(input, val) => { input.value = val; input.dispatchEvent(new Event('input', { bubbles: true })); input.dispatchEvent(new Event('change', { bubbles: true })); }", str(value))
                        self.log.info(f"Filled '{field_name}' via attribute fallback = '{value}'")
                        return True
                except Exception:
                    pass
            self.log.warning(f"Could not locate field '{field_name}'")
            return False

    def select_country(self, country_name: str) -> bool:
        """Select country from Angular mat-select dropdown."""
        try:
            mat_select = self.page.locator("mat-select").first
            mat_select.wait_for(state="visible", timeout=3000)
            mat_select.click()
            self.page.wait_for_timeout(400)
            
            # Match option in dropdown overlay
            opt = self.page.locator(f"mat-option:has-text('{country_name}'), .mat-mdc-option:has-text('{country_name}')").first
            if opt.is_visible():
                opt.click()
                self.log.info(f"Selected country: '{country_name}'")
                return True
            
            # Default to first option (e.g. India) if exact country not listed
            first_opt = self.page.locator("mat-option, .mat-mdc-option").first
            if first_opt.is_visible():
                first_opt.click()
                self.log.info(f"Selected default country option")
                return True
        except Exception as exc:
            self.log.warning(f"Failed to select country '{country_name}': {exc}")
        return False

    def set_active_checkbox(self, checked: bool = True) -> bool:
        """Toggle Active checkbox."""
        try:
            chk = self.page.locator("mat-checkbox:has-text('Active'), input[name='isActive']").first
            chk.wait_for(state="visible", timeout=3000)
            input_chk = self.page.locator("input[name='isActive']").first
            is_checked = input_chk.is_checked() if input_chk.count() else "mat-mdc-checkbox-checked" in (chk.get_attribute("class") or "")
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
        """Click Save, handle confirmation popup modal if present, and return toast outcome."""
        self.click_save()

        # Handle confirmation dialog if present
        if not confirm:
            try:
                no_btn = self.page.locator("button:has-text('No')").first
                no_btn.wait_for(state="visible", timeout=2500)
                no_btn.click()
                self.log.info("Dismissed Save popup (clicked No)")
                self.page.wait_for_timeout(500)
                return "Cancelled"
            except Exception as exc:
                self.log.warning(f"No confirmation popup appeared after clicking Save (expected 'No' button): {exc}")
        else:
            try:
                yes_btn = self.page.locator("button:has-text('Yes'), button:has-text('Confirm')").first
                yes_btn.wait_for(state="visible", timeout=2500)
                yes_btn.click()
                self.log.info("Confirmed Save popup (clicked Yes)")
            except Exception as exc:
                self.log.warning(f"No confirmation popup appeared after clicking Save (expected 'Yes' button): {exc}")

        # Wait for the API to respond — either a toast appears or the URL changes
        toast = self._wait_for_post_save_response(timeout=8000)
        self.log.info(f"Save confirmation outcome: '{toast}'")
        return toast

    def _wait_for_post_save_response(self, timeout: int = 8000) -> str:
        """Wait for either a toast/snackbar to appear OR the URL to change from /addvendor."""
        toast_sel = "simple-snack-bar, .mat-mdc-snack-bar-container, .mat-snack-bar-container, .toast, [role='alert']"
        try:
            # Wait for either toast OR URL navigation away from addvendor
            self.page.wait_for_function(
                """(sel) => {
                    const toast = document.querySelector(sel);
                    const urlChanged = !window.location.href.toLowerCase().includes('addvendor');
                    return (toast && toast.offsetParent !== null) || urlChanged;
                }""",
                arg=toast_sel,
                timeout=timeout,
            )
        except Exception:
            pass

        # Now try to capture the toast text
        return self.get_toast(timeout=2000)

    def click_cancel(self) -> bool:
        """Click Cancel / Reset button."""
        btn_sel = "button:has-text('Cancel'), button.btn-cancel"
        try:
            self.click(btn_sel)
            self.wait_for_dom_ready()
            self.log.info("Clicked Cancel button")
            return True
        except Exception:
            return False

    # ----------------- List & Search Interactions -----------------

    def search_vendor(self, term: str) -> bool:
        """Search for a vendor in the vendor management list table."""
        self.open_vendor_list()
        search_sel = "input[placeholder*='Search vendor name'], input[type='search'], input[placeholder*='Search']"
        try:
            self.fill(search_sel, term)
            self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(500)
            self.wait_for_dom_ready()
            return True
        except Exception:
            return False

    def toggle_include_inactive(self, checked: bool = True) -> bool:
        """Toggle the Include Inactive Vendor checkbox."""
        self.open_vendor_list()
        chk_sel = "mat-checkbox:has-text('Include Inactive Vendor'), mat-checkbox:has-text('Inactive')"
        try:
            chk = self.page.locator(chk_sel).first
            chk.wait_for(state="visible", timeout=3000)
            input_chk = self.page.locator("mat-checkbox:has-text('Include Inactive Vendor') input[type='checkbox']").first
            is_checked = input_chk.is_checked() if input_chk.count() else "mat-mdc-checkbox-checked" in (chk.get_attribute("class") or "")
            if is_checked != checked:
                chk.click()
            self.page.wait_for_timeout(500)
            self.wait_for_dom_ready()
            return True
        except Exception:
            return False

    def is_vendor_in_list(self, vendor_name: str) -> bool:
        """Check if vendor name is present in the table rows."""
        self.search_vendor(vendor_name)
        self.page.wait_for_timeout(1000)
        row_sel = f"table tr:has-text('{vendor_name}'), mat-row:has-text('{vendor_name}'), td:has-text('{vendor_name}')"
        return self.is_visible(row_sel, timeout=3000)

    # ----------------- Validation & Error Helpers -----------------

    def get_validation_errors(self) -> List[str]:
        """Collect visible inline validation error messages."""
        err_sel = "mat-error, .text-danger, .error-message, [role='alert'], .invalid-feedback, .mat-mdc-form-field-error"
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
            invalid_count = self.page.locator("form.ng-invalid, input.ng-invalid, textarea.ng-invalid, mat-select.ng-invalid, mat-form-field.mat-form-field-invalid, [aria-invalid='true']").count()
            return invalid_count > 0
        except Exception:
            return False
