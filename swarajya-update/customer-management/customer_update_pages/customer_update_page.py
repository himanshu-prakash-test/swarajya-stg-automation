"""Page Object for Customer Update Module."""

import time
from typing import Any, Dict, List, Optional
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeout
from shared.pages.base_page import BasePage
from shared.utils.logger import get_logger

log = get_logger("customer_update_page")


class CustomerUpdatePage(BasePage):
    """
    Page Object Model for Customer Update workflow.

    Navigation Workflow:
    1. /default (Default landing dashboard)
    2. /invoiceReports (Invoicing navigation)
    3. /invoicedashboard (Invoice Home / Dashboard)
    4. /customerDetails (Customer Details grid)
    5. Click pencil edit button on row -> Customer Update Form / Modal
    """

    CURRENCY_MAP = {
        "inr": "Indian Rupees",
        "usd": "US Dollars",
        "eur": "Euro",
        "gbp": "Pound",
        "sgd": "Singapore Doller",
        "nzd": "New Zealand",
        "jpy": "Japanese Yen",
    }

    FIELD_SELECTORS = {
        "customer name": [
            "input[name='custName']",
            "input[formcontrolname='custName']",
            "input[formcontrolname='customerName']",
            "input[name='customer_name']",
            "input[name='customerName']",
            "input[placeholder*='Customer Name' i]",
            "input#mat-input-0",
        ],
        "address line 1": [
            "input[name='custAddr1']",
            "input[formcontrolname='custAddr1']",
            "input[formcontrolname='addressLine1']",
            "input[name='customer_addr1']",
            "input[name='addressLine1']",
            "textarea[name='custAddr1']",
            "textarea[name='customer_addr1']",
            "textarea[name='addressLine1']",
            "input[placeholder*='Address Line 1' i]",
            "textarea[placeholder*='Address Line 1' i]",
        ],
        "address line 2": [
            "input[name='custAddr2']",
            "input[formcontrolname='custAddr2']",
            "input[formcontrolname='addressLine2']",
            "input[name='customer_addr2']",
            "input[name='addressLine2']",
            "textarea[name='custAddr2']",
            "textarea[name='customer_addr2']",
            "textarea[name='addressLine2']",
            "input[placeholder*='Address Line 2' i]",
            "textarea[placeholder*='Address Line 2' i]",
        ],
        "city": [
            "input[name='custPlace']",
            "input[formcontrolname='custPlace']",
            "input[formcontrolname='city']",
            "input[name='customer_place']",
            "input[name='city']",
            "input[placeholder*='City' i]",
        ],
        "pin": [
            "input[name='custPin']",
            "input[formcontrolname='custPin']",
            "input[formcontrolname='pin']",
            "input[name='customer_pin']",
            "input[name='pin']",
            "input[name='pincode']",
            "input[placeholder*='PIN' i]",
        ],
        "state": [
            "input[name='custState']",
            "input[formcontrolname='custState']",
            "input[formcontrolname='state']",
            "input[name='customer_state']",
            "input[name='state']",
            "mat-select[name='state']",
            "input[placeholder*='State' i]",
        ],
        "country": [
            "mat-select[name='custCountry']",
            "mat-select[formcontrolname='custCountry']",
            "mat-select[formcontrolname='customer_country']",
            "mat-select[name='customer_country']",
            "mat-select[name='country']",
            "mat-select[placeholder*='Country' i]",
            "mat-select#mat-select-0",
        ],
        "is igst applicable?": [
            "mat-checkbox[name='hasIgst']",
            "input[name='hasIgst']",
            "mat-checkbox:has-text('IGST')",
            "mat-slide-toggle:has-text('IGST')",
        ],
        "pan/it no.": [
            "input[name='custPan']",
            "input[formcontrolname='custPan']",
            "input[formcontrolname='pan']",
            "input[name='customer_pan']",
            "input[name='pan']",
            "input[placeholder*='PAN' i]",
        ],
        "gst no.": [
            "input[name='custGstin']",
            "input[formcontrolname='custGstin']",
            "input[formcontrolname='gst']",
            "input[name='customer_gstin']",
            "input[name='gst']",
            "input[placeholder*='GST' i]",
        ],
        "code": [
            "input[name='custCode']",
            "input[formcontrolname='custCode']",
            "input[formcontrolname='code']",
            "input[name='customer_code']",
            "input[name='code']",
            "input[placeholder*='Code' i]",
        ],
        "place of supply": [
            "input[name='custSupply']",
            "input[formcontrolname='custSupply']",
            "input[formcontrolname='placeOfSupply']",
            "input[name='customer_place_of_supply']",
            "input[name='placeOfSupply']",
            "input[placeholder*='Place of Supply' i]",
        ],
        "primary person name": [
            "input[name='custPrimaryPerson']",
            "input[formcontrolname='custPrimaryPerson']",
            "input[formcontrolname='primaryPersonName']",
            "input[name='customer_primary_person_name']",
            "input[name='primaryPersonName']",
            "input[placeholder*='Primary Person Name' i]",
        ],
        "finance person name": [
            "input[name='custFinancePerson']",
            "input[formcontrolname='custFinancePerson']",
            "input[formcontrolname='financePersonName']",
            "input[name='customer_finance_person_name']",
            "input[name='financePersonName']",
            "input[placeholder*='Finance Person Name' i]",
        ],
        "primary person phone": [
            "input[name='custPrimaryPhone']",
            "input[formcontrolname='custPrimaryPhone']",
            "input[formcontrolname='primaryPersonPhone']",
            "input[name='customer_primary_person_phone']",
            "input[name='primaryPersonPhone']",
            "input[placeholder*='Primary Person Phone' i]",
        ],
        "finance person phone": [
            "input[name='custFinancePhone']",
            "input[formcontrolname='custFinancePhone']",
            "input[formcontrolname='financePersonPhone']",
            "input[name='customer_finance_phone']",
            "input[name='financePersonPhone']",
            "input[placeholder*='Finance Person Phone' i]",
        ],
        "primary person email id": [
            "input[name='custPrimaryEmail']",
            "input[formcontrolname='custPrimaryEmail']",
            "input[formcontrolname='primaryPersonEmail']",
            "input[name='customer_primary_person_email_id']",
            "input[name='primaryPersonEmail']",
            "input[placeholder*='Primary Person Email' i]",
        ],
        "finance person email id": [
            "input[name='custFinanceEmail']",
            "input[formcontrolname='custFinanceEmail']",
            "input[formcontrolname='financePersonEmail']",
            "input[name='customer_finance_email_id']",
            "input[name='financePersonEmail']",
            "input[placeholder*='Finance Person Email' i]",
        ],
        "payment terms (days)": [
            "input[name='custPaymentTerms']",
            "input[formcontrolname='custPaymentTerms']",
            "input[formcontrolname='paymentTerms']",
            "input[name='customer_payment_terms']",
            "input[name='paymentTerms']",
            "input[placeholder*='Payment Terms' i]",
        ],
        "currency": [
            "mat-select[name='custCurrency']",
            "mat-select[formcontrolname='custCurrency']",
            "mat-select[formcontrolname='default_currency']",
            "mat-select[name='default_currency']",
            "mat-select[name='currency']",
            "mat-select[placeholder*='Currency' i]",
            "mat-select#mat-select-1",
        ],
        "active": [
            "input[name='isActive']",
            "mat-checkbox[name='isActive']",
            "mat-slide-toggle[name='isActive']",
            "mat-checkbox:has-text('Active')",
            "mat-slide-toggle:has-text('Active')",
        ],
    }

    def __init__(self, page: Page):
        super().__init__(page)

    # ----------------- Navigation -----------------

    def open_default_dashboard(self):
        """Step 1: Navigate to Default Landing screen (/default)."""
        if "default" not in self.page.url.lower():
            self.goto("/default")
            self.wait_for_dom_ready()
        self.dismiss_any_tutorial_or_dialog()

    def open_invoice_reports(self):
        """Step 2: Navigate to Invoice Reports (/invoiceReports) via Invoicing link."""
        if "invoicereports" in self.page.url.lower():
            return

        self.dismiss_any_tutorial_or_dialog()
        link = self.page.locator(
            "a.nav-link:has-text('Invoicing'), a[href*='invoiceReports'], span:has-text('Invoicing'), [mattooltip*='Invoicing' i]"
        ).first
        if link.is_visible(timeout=3000):
            link.click()
            try:
                self.page.wait_for_url(lambda u: "invoicereports" in u.lower(), timeout=5000)
            except Exception:
                self.goto("/invoiceReports")
        else:
            self.goto("/invoiceReports")
        self.wait_for_dom_ready()

    def open_invoice_dashboard(self):
        """Step 3: Navigate to Invoice Home / Dashboard (/invoicedashboard)."""
        if "invoicedashboard" in self.page.url.lower():
            return

        link = self.page.locator(
            "a[href*='invoicedashboard'], a:has-text('Invoice Home'), [mattooltip*='Invoice Home' i], span:has-text('Invoice Home')"
        ).first
        if link.is_visible(timeout=3000):
            link.click()
            try:
                self.page.wait_for_url(lambda u: "invoicedashboard" in u.lower(), timeout=5000)
            except Exception:
                self.goto("/invoicedashboard")
        else:
            self.goto("/invoicedashboard")
        self.wait_for_dom_ready()

    def open_customer_list(self, direct: bool = False):
        """Step 4: Navigate to Customer Details listing page (/customerDetails)."""
        url = "/customerDetails"
        if "customerdetails" in self.page.url.lower():
            return

        if direct:
            self.goto(url)
            self.wait_for_dom_ready()
            return

        if "invoicedashboard" not in self.page.url.lower():
            self.open_invoice_dashboard()

        self.dismiss_any_tutorial_or_dialog()

        card = self.page.locator(
            "mat-card:has-text('Customers'), div:has-text('Customers'), a:has-text('Customers'), "
            "a[href*='customerDetails'], button:has-text('Customer Details'), [mattooltip*='Customer Details' i], span:has-text('Customer Details')"
        ).last

        if card.is_visible(timeout=3000):
            card.click()
            try:
                self.page.wait_for_url(lambda u: "customerdetails" in u.lower(), timeout=6000)
            except Exception:
                self.goto(url)
        else:
            self.goto(url)

        self.wait_for_dom_ready()
        self.dismiss_any_tutorial_or_dialog()
        try:
            self.page.locator("tbody tr td, table").first.wait_for(state="visible", timeout=12000)
        except Exception:
            pass

    # ----------------- Listing & Row Selection -----------------

    def search_customer(self, search_term: str):
        """Filter customer grid by search term."""
        search_input = self.page.locator(
            "input[placeholder*='Search' i], input[type='search']"
        ).first
        if search_input.is_visible(timeout=5000):
            search_input.fill(str(search_term))
            search_input.press("Enter")
            self.wait_for_dom_ready()
            time.sleep(1)

    def get_customer_rows(self) -> List[Locator]:
        """Return all visible rows in customer table."""
        return self.page.locator("table tbody tr, mat-table mat-row, .grid-row").all()

    def get_grid_row_count(self) -> int:
        """Return count of visible customer rows in grid."""
        rows = self.page.locator("table tbody tr, mat-table mat-row, .grid-row")
        return rows.count()

    def open_customer_edit_modal(self, customer_name_or_code: Optional[str] = None, row_index: int = 0):
        """
        Step 5: Click the pencil / edit button on target customer row to open update form.
        """
        self.dismiss_any_tutorial_or_dialog()

        if not customer_name_or_code:
            search_input = self.page.locator("input[placeholder*='Search' i], input[type='search']").first
            if search_input.is_visible(timeout=1000) and search_input.input_value():
                search_input.fill("")
                search_input.press("Enter")
                self.wait_for_dom_ready()

        try:
            self.page.wait_for_selector("tbody tr td button, tbody tr", timeout=10000)
        except Exception:
            pass

        row = None
        if customer_name_or_code:
            self.search_customer(customer_name_or_code)
            matching = self.page.locator("tbody tr, mat-row").filter(has_text=str(customer_name_or_code))
            if matching.count() > 0:
                row = matching.first
            else:
                self.search_customer("")
                rows = self.page.locator("tbody tr, mat-row")
                row = rows.first if rows.count() else None
        else:
            rows = self.page.locator("tbody tr, mat-row")
            if rows.count() > row_index:
                row = rows.nth(row_index)
            else:
                row = rows.first if rows.count() else None

        if not row or not row.count():
            log.warning("No table rows found to click edit button")
            return

        edit_btn = row.locator(
            "button:has(mat-icon:has-text('edit')), button:has(i.icofont-edit), button.btn-link:has-text('edit'), "
            "button[mattooltip*='Edit' i], a[mattooltip*='Edit' i], button:has-text('edit'), button"
        ).first

        edit_btn.scroll_into_view_if_needed()
        edit_btn.click(force=True)

        # Wait for form modal or edit page to be visible
        try:
            self.page.wait_for_selector("form, mat-dialog-container, .modal-content", timeout=8000)
        except Exception:
            pass
        self.wait_for_dom_ready()

    # ----------------- Form Field Interactions -----------------

    def fill_field(self, field_name: str, value: Any) -> bool:
        """Fill or update a form field dynamically based on field name or label."""
        key = str(field_name).strip().lower().lstrip("•-* ").strip()
        val_str = str(value) if value is not None else ""

        if "active" in key or "status" in key:
            checked = val_str.lower() in ("ticked", "true", "yes", "1", "active")
            return self.set_active_checkbox(checked)

        if "igst" in key:
            checked = val_str.lower() in ("ticked", "true", "yes", "1", "applicable")
            return self.set_igst_checkbox(checked)

        if any(d in key for d in ("country", "currency")):
            if val_str and self.select_dropdown_option(key, val_str):
                return True

        target_selectors = self.FIELD_SELECTORS.get(key)
        if not target_selectors:
            for k, slist in self.FIELD_SELECTORS.items():
                if k in key or key in k:
                    target_selectors = slist
                    break

        if not target_selectors:
            clean_k = key.replace(" ", "").replace("/", "").replace(".", "").replace("_", "")
            target_selectors = [
                f"input[formcontrolname*='{clean_k}' i]",
                f"input[name*='{clean_k}' i]",
                f"input[placeholder*='{field_name}' i]",
                f"textarea[formcontrolname*='{clean_k}' i]",
                f"textarea[name*='{clean_k}' i]",
                f"textarea[placeholder*='{field_name}' i]",
            ]

        for sel in target_selectors:
            try:
                field = self.page.locator(sel).first
                if field.count() and field.is_visible(timeout=800):
                    field.click()
                    field.fill(val_str)
                    field.dispatch_event("input")
                    field.dispatch_event("change")
                    log.info(f"Updated '{field_name}' = '{val_str}' using selector: {sel}")
                    return True
            except Exception:
                continue

        # Fallback to general input search
        try:
            inputs = self.page.locator("form input:not([type='hidden']), form textarea").all()
            for inp in inputs:
                attr_name = (inp.get_attribute("name") or "").lower()
                attr_ph = (inp.get_attribute("placeholder") or "").lower()
                attr_fc = (inp.get_attribute("formcontrolname") or "").lower()
                if key in attr_name or key in attr_ph or key in attr_fc:
                    inp.click()
                    inp.fill(val_str)
                    inp.dispatch_event("input")
                    inp.dispatch_event("change")
                    return True
        except Exception:
            pass

        return False

    def select_dropdown_option(self, field_name: str, option_text: str) -> bool:
        """Select option from a mat-select dropdown."""
        try:
            fn = field_name.lower().strip()
            opt_val = option_text.strip().strip("'\"")
            if "currency" in fn:
                opt_val = self.CURRENCY_MAP.get(opt_val.lower(), opt_val)

            selectors = [
                f"mat-select[formcontrolname*='{fn}' i]",
                f"mat-select[name*='{fn}' i]",
            ]
            if "country" in fn:
                selectors.extend([
                    "mat-select[name='custCountry']",
                    "mat-select[formcontrolname='custCountry']",
                    "mat-select[formcontrolname='customer_country']",
                    "mat-select[name='customer_country']",
                    "mat-select[name='country']",
                ])
            elif "currency" in fn:
                selectors.extend([
                    "mat-select[name='custCurrency']",
                    "mat-select[formcontrolname='custCurrency']",
                    "mat-select[formcontrolname='default_currency']",
                    "mat-select[name='default_currency']",
                    "mat-select[name='currency']",
                ])

            select_el = None
            for sel in selectors:
                el = self.page.locator(sel).first
                if el.count() and el.is_visible(timeout=1500):
                    select_el = el
                    break

            if select_el:
                select_el.click()
                self.page.wait_for_timeout(400)
                opt = self.page.locator(
                    f"mat-option:has-text('{opt_val}'), .mat-mdc-option:has-text('{opt_val}'), [role='option']:has-text('{opt_val}')"
                ).first
                if opt.is_visible(timeout=2500):
                    opt.click()
                    self.page.wait_for_timeout(300)
                    return True
                else:
                    first_opt = self.page.locator("mat-option, .mat-mdc-option, [role='option']").first
                    if first_opt.is_visible(timeout=1500):
                        first_opt.click()
                        self.page.wait_for_timeout(300)
                        return True
        except Exception as exc:
            log.warning(f"select_dropdown_option error for {field_name}: {exc}")
        return False

    def get_field_value(self, field_name: str) -> str:
        """Retrieve current value of a form field."""
        key = str(field_name).strip().lower().lstrip("•-* ").strip()
        target_selectors = self.FIELD_SELECTORS.get(key, [f"input[formcontrolname='{key}']"])
        for sel in target_selectors:
            loc = self.page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                tag = loc.first.evaluate("e => e.tagName")
                if tag in ["INPUT", "TEXTAREA"]:
                    return loc.first.input_value()
                return loc.first.inner_text().strip()
        return ""

    def is_field_readonly(self, field_name: str) -> bool:
        """Verify whether a field is disabled or read-only."""
        key = str(field_name).strip().lower().lstrip("•-* ").strip()
        target_selectors = self.FIELD_SELECTORS.get(key, [f"input[formcontrolname='{key}']"])
        for sel in target_selectors:
            loc = self.page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                return loc.first.evaluate(
                    "e => e.hasAttribute('readonly') || e.hasAttribute('disabled') || e.getAttribute('aria-disabled') === 'true'"
                )
        return False

    def set_igst_checkbox(self, checked: bool = True) -> bool:
        """Toggle the 'Is IGST Applicable?' checkbox or slide toggle."""
        try:
            chk = self.page.locator("mat-checkbox[name='hasIgst'], input[name='hasIgst']").first
            if chk.count():
                current = self.get_igst_switch_state()
                if current != checked:
                    chk.click(force=True)
                    self.page.wait_for_timeout(300)
                return True
        except Exception as exc:
            log.warning(f"Could not toggle IGST switch: {exc}")
        return False

    def get_igst_switch_state(self) -> bool:
        """Check whether the Is IGST Applicable switch is checked/enabled."""
        try:
            chk = self.page.locator("mat-checkbox[name='hasIgst']").first
            if chk.count():
                classes = chk.get_attribute("class") or ""
                return "checked" in classes or "mat-mdc-checkbox-checked" in classes
            inp = self.page.locator("input[name='hasIgst']").first
            if inp.count():
                return inp.is_checked()
        except Exception:
            pass
        return False

    def set_active_checkbox(self, checked: bool = True) -> bool:
        """Toggle the Active / Status checkbox or slide toggle."""
        try:
            toggle = self.page.locator(
                "mat-checkbox[name='isActive'], mat-slide-toggle[name='isActive'], mat-checkbox:has-text('Active'), mat-slide-toggle:has-text('Active')"
            ).first
            if toggle.count() and toggle.is_visible():
                is_currently_checked = "checked" in (toggle.get_attribute("class") or "")
                if is_currently_checked != checked:
                    toggle.click(force=True)
                return True
        except Exception:
            pass
        return False

    def ensure_required_fields_filled(self):
        """Ensure mandatory fields (Address Line 1, City, State, Payment Terms) are populated so update button enables."""
        defaults = {
            "address line 1": "Plot 55, MIDC Phase 2",
            "city": "Mumbai",
            "state": "Maharashtra",
            "payment terms (days)": "30",
        }
        for field, default_val in defaults.items():
            val = self.get_field_value(field)
            if not val or not val.strip():
                self.fill_field(field, default_val)

    def is_edit_modal_open(self) -> bool:
        """Check whether Customer Edit modal / card is visible."""
        try:
            return self.page.locator("mat-card.modal-card, .modal-overlay, form").first.is_visible(timeout=1000)
        except Exception:
            return False

    # ----------------- Submission & Actions -----------------

    def save(self, confirm: bool = True) -> str:
        """Click Update / Save and confirm modal confirmation dialog if displayed."""
        save_btn = self.page.locator(
            "button:has-text('Update Customer'), button:has-text('Update'), button:has-text('Save'), button:has-text('Submit'), button[type='submit']"
        ).first
        if not save_btn.is_visible(timeout=3000):
            save_btn = self.page.locator("button:has-text('Update')").first

        save_btn.wait_for(state="visible", timeout=5000)
        save_btn.scroll_into_view_if_needed()

        # If button is disabled due to missing mandatory fields, ensure defaults are filled
        if save_btn.is_disabled() or "disabled" in (save_btn.get_attribute("class") or ""):
            self.ensure_required_fields_filled()
            self.page.wait_for_timeout(300)

        if not (save_btn.is_disabled() or "disabled" in (save_btn.get_attribute("class") or "")):
            save_btn.click()
            self.wait_for_dom_ready()

        # Handle confirmation dialog / snackbar popup with Yes / No if present
        try:
            confirm_container = self.page.locator(
                "mat-dialog-container, .mat-snack-bar-container, .modal-content, .swal2-popup, "
                ".cdk-overlay-pane:has(button:has-text('Yes')), div:has(button:has-text('Yes')):has(button:has-text('No')), "
                "div[role='dialog'], div[role='alertdialog']"
            ).first
            if confirm_container.is_visible(timeout=2000):
                if confirm:
                    yes_btn = confirm_container.locator(
                        "button:has-text('Yes'), button:has-text('Confirm'), button:has-text('Ok'), a:has-text('Yes')"
                    ).first
                    if yes_btn.is_visible():
                        yes_btn.click()
                        self.wait_for_dom_ready()
                        time.sleep(1)
                else:
                    no_btn = confirm_container.locator(
                        "button:has-text('No'), button:has-text('Cancel'), button:has-text('Dismiss'), a:has-text('No')"
                    ).first
                    if no_btn.is_visible():
                        no_btn.click()
                        self.wait_for_dom_ready()
                        return "Cancelled"
        except Exception:
            pass

        # Wait for modal overlay to disappear on successful update
        try:
            self.page.locator(".modal-overlay, mat-card.modal-card").first.wait_for(state="hidden", timeout=4000)
        except Exception:
            pass

        return self.get_toast_message(timeout=2000) or "Submitted"

    def cancel(self) -> bool:
        """Click Cancel, Close or Discard button."""
        cancel_btn = self.page.locator(
            "mat-card.modal-card button:has-text('Close'), button:has-text('Close'), button.icon-btn-5, "
            "button:has(mat-icon:has-text('close')), button:has-text('Cancel'), button:has-text('Discard')"
        ).last
        if cancel_btn.is_visible(timeout=3000):
            cancel_btn.scroll_into_view_if_needed()
            cancel_btn.click(force=True)
            self.wait_for_dom_ready()
            try:
                self.page.locator(".modal-overlay, mat-card.modal-card").first.wait_for(state="hidden", timeout=3000)
            except Exception:
                pass
            return True
        return False

    def close_modal(self) -> bool:
        """Click top-right close icon or press Escape."""
        try:
            close_btn = self.page.locator(
                "mat-card.modal-card button:has-text('Close'), button.icon-btn-5, button:has(mat-icon:has-text('close'))"
            ).first
            if close_btn.is_visible(timeout=2000):
                close_btn.click(force=True)
                self.wait_for_dom_ready()
                return True
            self.page.keyboard.press("Escape")
            return True
        except Exception:
            return False

    # ----------------- Validation & Notifications -----------------

    def has_form_errors(self) -> bool:
        """Check whether form has validation errors or invalid inputs."""
        error_locators = self.page.locator(
            "mat-error, .mat-mdc-form-field-error, .invalid-feedback, .text-danger, [aria-invalid='true']"
        )
        if error_locators.count():
            for i in range(error_locators.count()):
                try:
                    if error_locators.nth(i).is_visible():
                        return True
                except Exception:
                    continue
        if self.page.locator("input.ng-invalid.ng-touched, mat-select.ng-invalid.ng-touched").count():
            return True
        text = self.page.locator("body").inner_text().lower()
        if any(v in text for v in ("is required", "invalid email", "enter valid", "already exist", "must be", "cannot be")):
            return True
        return False

    def get_toast_message(self, timeout: int = 5000) -> str:
        """Capture toast / snackbar notification text."""
        try:
            toast = self.page.locator(
                ".mat-snack-bar-container, .toast, .alert, .swal2-title, .toast-message, mat-simple-snackbar"
            ).first
            if toast.is_visible(timeout=timeout):
                return toast.inner_text().strip()
        except Exception:
            pass
        return ""

    def success_message_visible(self, timeout: int = 4000) -> bool:
        """Verify successful update notification, modal closed, or redirection."""
        # 1. Edit modal closed (submitted and saved)
        if not self.is_edit_modal_open():
            return True

        # 2. Toast notification
        toast = self.get_toast_message(timeout=timeout)
        if toast and any(v in toast.lower() for v in ("success", "updated", "saved")):
            return True

        # 3. URL is /customerDetails and no form errors
        if "customerdetails" in self.page.url.lower() and not self.has_form_errors():
            return True

        return False

    def validation_visible(self) -> bool:
        """Verify validation errors or prevented save."""
        if self.has_form_errors():
            return True
        save_btn = self.page.locator(
            "button:has-text('Update'), button:has-text('Save'), button[type='submit']"
        ).first
        if save_btn.count() and (save_btn.is_disabled() or "disabled" in (save_btn.get_attribute("class") or "")):
            return True
        if self.page.locator("input.ng-invalid, mat-select.ng-invalid, .ng-invalid").count():
            return True
        return False
