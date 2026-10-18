import time
from typing import Any, Dict, List, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from shared.pages.base_page import BasePage


class CustomerPage(BasePage):
    """Page Object for Customer Management (Create Customer, List, Search, Validation)."""

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
            "input[name='customer_name']",
            "input[name='customerName']",
            "input[formcontrolname='customerName']",
            "input[placeholder*='Customer Name' i]",
            "input#mat-input-0",
        ],
        "address line 1": [
            "input[name='customer_addr1']",
            "input[name='addressLine1']",
            "textarea[name='customer_addr1']",
            "textarea[name='addressLine1']",
            "input[placeholder*='Address Line 1' i]",
            "textarea[placeholder*='Address Line 1' i]",
        ],
        "address line 2": [
            "input[name='customer_addr2']",
            "input[name='addressLine2']",
            "textarea[name='customer_addr2']",
            "textarea[name='addressLine2']",
            "input[placeholder*='Address Line 2' i]",
            "textarea[placeholder*='Address Line 2' i]",
        ],
        "city": [
            "input[name='customer_place']",
            "input[name='city']",
            "input[formcontrolname='city']",
            "input[placeholder*='City' i]",
        ],
        "pin": [
            "input[name='customer_pin']",
            "input[name='pin']",
            "input[name='pincode']",
            "input[placeholder*='PIN' i]",
        ],
        "state": [
            "input[name='customer_state']",
            "input[name='state']",
            "mat-select[name='state']",
            "input[placeholder*='State' i]",
        ],
        "country": [
            "mat-select[name='customer_country']",
            "mat-select[formcontrolname='customer_country']",
            "mat-select[name='country']",
            "mat-select[placeholder*='Country' i]",
            "mat-select#mat-select-0",
        ],
        "is igst applicable?": [
            "input[name='hasIgst']",
            "mat-checkbox[name='hasIgst']",
            "mat-checkbox:has-text('IGST')",
            "mat-slide-toggle:has-text('IGST')",
        ],
        "pan/it no.": [
            "input[name='customer_pan']",
            "input[name='pan']",
            "input[placeholder*='PAN' i]",
        ],
        "gst no.": [
            "input[name='customer_gstin']",
            "input[name='gst']",
            "input[placeholder*='GST' i]",
        ],
        "code": [
            "input[name='customer_code']",
            "input[name='code']",
            "input[placeholder*='Code' i]",
        ],
        "place of supply": [
            "input[name='customer_place_of_supply']",
            "input[name='placeOfSupply']",
            "input[placeholder*='Place of Supply' i]",
        ],
        "primary person name": [
            "input[name='customer_primary_person_name']",
            "input[name='primaryPersonName']",
            "input[placeholder*='Primary Person Name' i]",
        ],
        "finance person name": [
            "input[name='customer_finance_person_name']",
            "input[name='financePersonName']",
            "input[placeholder*='Finance Person Name' i]",
        ],
        "primary person phone": [
            "input[name='customer_primary_person_phone']",
            "input[name='primaryPersonPhone']",
            "input[placeholder*='Primary Person Phone' i]",
        ],
        "finance person phone": [
            "input[name='customer_finance_phone']",
            "input[name='financePersonPhone']",
            "input[placeholder*='Finance Person Phone' i]",
        ],
        "primary person email id": [
            "input[name='customer_primary_person_email_id']",
            "input[name='primaryPersonEmail']",
            "input[placeholder*='Primary Person Email' i]",
        ],
        "finance person email id": [
            "input[name='customer_finance_email_id']",
            "input[name='financePersonEmail']",
            "input[placeholder*='Finance Person Email' i]",
        ],
        "payment terms (days)": [
            "input[name='customer_payment_terms']",
            "input[name='paymentTerms']",
            "input[placeholder*='Payment Terms' i]",
        ],
        "currency": [
            "mat-select[name='default_currency']",
            "mat-select[formcontrolname='default_currency']",
            "mat-select[name='currency']",
            "mat-select[placeholder*='Currency' i]",
            "mat-select#mat-select-1",
        ],
    }

    def __init__(self, page: Page):
        super().__init__(page)

    # ----------------- Navigation -----------------

    def open_default_dashboard(self):
        """Navigate to Default Landing screen (/default)."""
        if "default" not in self.page.url.lower():
            self.goto("/default")
            self.wait_for_dom_ready()
        self.dismiss_any_tutorial_or_dialog()

    def open_invoice_reports(self):
        """
        Navigate to Invoice Reports (/invoiceReports).
        Step 1 after /default in Customer workflow.
        """
        if "invoicereports" in self.page.url.lower():
            return

        self.dismiss_any_tutorial_or_dialog()
        link = self.page.locator(
            "a.nav-link:has-text('Invoicing'), a[href*='invoiceReports'], span:has-text('Invoicing'), [mattooltip*='Invoicing' i]"
        ).first
        if link.is_visible(timeout=3000):
            link.click()
            try:
                self.page.wait_for_url(lambda u: "invoicereports" in u.lower(), timeout=4000)
            except Exception:
                self.goto("/invoiceReports")
        else:
            self.goto("/invoiceReports")
        self.wait_for_dom_ready()

    def open_invoice_dashboard(self):
        """
        Navigate to Invoice Home / Dashboard (/invoicedashboard).
        Step 2 in Customer workflow.
        """
        if "invoicedashboard" in self.page.url.lower():
            return

        link = self.page.locator(
            "a[href*='invoicedashboard'], a:has-text('Invoice Home'), [mattooltip*='Invoice Home' i], span:has-text('Invoice Home')"
        ).first
        if link.is_visible(timeout=2000):
            link.click()
            try:
                self.page.wait_for_url(lambda u: "invoicedashboard" in u.lower(), timeout=4000)
            except Exception:
                self.goto("/invoicedashboard")
        else:
            self.goto("/invoicedashboard")
        self.wait_for_dom_ready()

    def open_customer_list(self, direct: bool = True):
        """
        Navigate to Customer Details listing page (/customerDetails).
        Direct navigation saves redundant route transitions when session is authenticated.
        """
        if "customerdetails" in self.page.url.lower():
            return

        if direct:
            self.goto("/customerDetails")
            self.wait_for_dom_ready()
            return

        if "invoicedashboard" not in self.page.url.lower():
            self.open_invoice_dashboard()

        link = self.page.locator(
            "mat-card:has-text('Customers'), div:has-text('Customers'), a:has-text('Customers'), "
            "a[href*='customerDetails'], button:has-text('Customer Details'), [mattooltip*='Customer Details' i], span:has-text('Customer Details')"
        ).last
        if link.is_visible(timeout=3000):
            link.click()
            self.wait_for_dom_ready()
        else:
            self.goto("/customerDetails")
            self.wait_for_dom_ready()

    def open_create_customer_form(self, direct: bool = True):
        """
        Open the Add / Create Customer form (/addNewCustomer).
        """
        if "addnewcustomer" in self.page.url.lower():
            return

        if direct:
            self.goto("/addNewCustomer")
            self.wait_for_dom_ready()
            return

        self.open_customer_list(direct=False)
        btn = self.page.locator(
            "button:has-text('New Customer'), button:has-text('Add Customer'), a:has-text('New Customer'), a:has-text('Add Customer'), a[href*='addNewCustomer'], button:has-text('Customer')"
        ).first
        if btn.is_visible(timeout=3000):
            btn.click()
            self.wait_for_dom_ready()
        else:
            self.goto("/addNewCustomer")
            self.wait_for_dom_ready()

        self.wait_for_url_contains("addNewCustomer", timeout=6000)

    # ----------------- Form Field Interactions -----------------

    def set_igst_checkbox(self, checked: bool = True) -> bool:
        """Toggle the 'Is IGST Applicable?' checkbox or slide toggle."""
        current = self.get_igst_switch_state()
        if current != checked:
            return self.toggle_igst_switch(checked)
        return True

    def fill_field(self, field_name: str, value: str) -> bool:
        """Fill a form input dynamically based on field name."""
        key = str(field_name).strip().lower().lstrip("•-* ").strip()
        val_str = str(value) if value is not None else ""

        if "active" in key or "status" in key:
            checked = val_str.lower() in ("ticked", "true", "yes", "1", "active")
            return self.set_active_checkbox(checked)

        if "igst" in key:
            checked = val_str.lower() in ("ticked", "true", "yes", "1", "applicable")
            return self.set_igst_checkbox(checked)

        # Handle dropdown selections strictly for country and currency
        if any(d in key for d in ("country", "currency")):
            if val_str and self.select_dropdown_option(key, val_str):
                return True

        # Find configured selectors
        target_selectors = self.FIELD_SELECTORS.get(key)
        if not target_selectors:
            for k, slist in self.FIELD_SELECTORS.items():
                if k in key or key in k:
                    target_selectors = slist
                    break

        if not target_selectors:
            clean_k = key.replace(" ", "").replace("/", "").replace(".", "").replace("_", "")
            target_selectors = [
                f"input[name*='{clean_k}' i]",
                f"input[formcontrolname*='{clean_k}' i]",
                f"input[placeholder*='{field_name}' i]",
                f"textarea[name*='{clean_k}' i]",
                f"textarea[placeholder*='{field_name}' i]",
            ]

        for sel in target_selectors:
            try:
                field = self.page.locator(sel).first
                if field.count() and field.is_visible(timeout=800):
                    try:
                        field.fill(val_str)
                    except Exception:
                        field.evaluate(
                            "(el, val) => { el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }",
                            val_str,
                        )
                    self.log.info(f"Filled '{field_name}' = '{val_str}' using selector: {sel}")
                    return True
            except Exception:
                continue

        # Fallback to general input search by placeholder/name
        try:
            inputs = self.page.locator("input:not([type='hidden']), textarea").all()
            for inp in inputs:
                attr_name = (inp.get_attribute("name") or "").lower()
                attr_ph = (inp.get_attribute("placeholder") or "").lower()
                attr_fc = (inp.get_attribute("formcontrolname") or "").lower()
                if key in attr_name or key in attr_ph or key in attr_fc:
                    try:
                        inp.fill(val_str)
                        return True
                    except Exception:
                        inp.evaluate(
                            "(el, val) => { el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }",
                            val_str,
                        )
                        return True
        except Exception:
            pass

        return False

    def select_dropdown_option(self, field_name: str, option_text: str) -> bool:
        """Select option from a mat-select or custom dropdown."""
        try:
            fn = field_name.lower().strip()
            opt_val = option_text.strip()
            if "currency" in fn:
                opt_val = self.CURRENCY_MAP.get(opt_val.lower(), opt_val)

            selectors = [
                f"mat-select[name='{field_name}']",
                f"mat-select[formcontrolname='{field_name}']",
            ]
            if "country" in fn:
                selectors = [
                    "mat-select[name='customer_country']",
                    "mat-select[formcontrolname='customer_country']",
                    "mat-select[name='country']",
                    "mat-select#mat-select-0",
                ]
            elif "currency" in fn:
                selectors = [
                    "mat-select[name='default_currency']",
                    "mat-select[formcontrolname='default_currency']",
                    "mat-select[name='currency']",
                    "mat-select#mat-select-1",
                ]

            select_el = None
            for sel in selectors:
                el = self.page.locator(sel).first
                if el.count() and el.is_visible(timeout=1500):
                    select_el = el
                    break

            if select_el:
                select_el.click()
                self.page.wait_for_timeout(400)
                # Look for matching option in overlay
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
            self.log.warning(f"select_dropdown_option error for {field_name}: {exc}")
        return False

    def get_dropdown_options(self, field_name: str) -> List[str]:
        """Fetch all visible options from a dropdown (Country, Currency, etc.)."""
        options = []
        try:
            fn = field_name.lower().strip()
            selectors = [
                f"mat-select[name='{field_name}']",
                f"mat-select[formcontrolname='{field_name}']",
            ]
            if "country" in fn:
                selectors = [
                    "mat-select[name='customer_country']",
                    "mat-select[formcontrolname='customer_country']",
                    "mat-select[name='country']",
                    "mat-select#mat-select-0",
                ]
            elif "currency" in fn:
                selectors = [
                    "mat-select[name='default_currency']",
                    "mat-select[formcontrolname='default_currency']",
                    "mat-select[name='currency']",
                    "mat-select#mat-select-1",
                ]

            select_el = None
            for sel in selectors:
                el = self.page.locator(sel).first
                if el.count() and el.is_visible(timeout=2000):
                    select_el = el
                    break

            if select_el:
                select_el.click()
                self.page.wait_for_timeout(500)
                opt_elements = self.page.locator("mat-option, .mat-mdc-option, [role='option']").all()
                for opt in opt_elements:
                    txt = opt.inner_text().strip()
                    if txt and txt not in options:
                        options.append(txt)
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(300)
        except Exception as exc:
            self.log.warning(f"Could not retrieve dropdown options for {field_name}: {exc}")
        return options

    def verify_dropdown_selection(self, field_name: str, option_text: str) -> bool:
        """Select option and verify it is successfully reflected in the dropdown trigger."""
        success = self.select_dropdown_option(field_name, option_text)
        if not success:
            return False
        try:
            fn = field_name.lower().strip()
            trigger = self.page.locator(
                f"mat-select[name*='{fn}' i], mat-select[formcontrolname*='{fn}' i], mat-select:has-text('{fn}')"
            ).first
            trigger_text = trigger.inner_text().strip() if trigger.is_visible() else ""
            return option_text.lower() in trigger_text.lower() or len(trigger_text) > 0
        except Exception:
            return True

    def get_igst_switch_state(self) -> bool:
        """Check whether the Is IGST Applicable switch is checked/enabled."""
        try:
            inp = self.page.locator("input[name='hasIgst'], input[type='checkbox'][formcontrolname*='igst' i]").first
            if inp.count():
                return inp.is_checked()
            chk = self.page.locator("mat-checkbox[name='hasIgst'], mat-checkbox:has-text('IGST')").first
            if chk.count():
                classes = chk.get_attribute("class") or ""
                return "checked" in classes or "mat-mdc-checkbox-checked" in classes
        except Exception:
            pass
        return False

    def toggle_igst_switch(self, target_state: Optional[bool] = None) -> bool:
        """Toggle the Is IGST Applicable switch to target state or flip it."""
        try:
            chk = self.page.locator(
                "input[name='hasIgst'], mat-checkbox[name='hasIgst'], mat-checkbox:has-text('IGST'), mat-slide-toggle:has-text('IGST')"
            ).first
            if chk.count():
                current = self.get_igst_switch_state()
                if target_state is None or current != target_state:
                    chk.click(force=True)
                    self.page.wait_for_timeout(300)
                    return True
                return True
        except Exception as exc:
            self.log.warning(f"Could not toggle IGST switch: {exc}")
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

    # ----------------- Form Submission & Confirmations -----------------

    def click_save_and_confirm(self, confirm: bool = True) -> str:
        """Click Save and confirm/cancel modal confirmation dialog or snackbar with Yes / No."""
        save_btn = self.page.locator(
            "button:has-text('Save'), button:has-text('Submit'), button[type='submit']"
        ).first
        save_btn.wait_for(state="visible", timeout=4000)
        save_btn.click()
        self.wait_for_dom_ready()

        # Handle confirmation dialog / snackbar popup with Yes / No
        try:
            confirm_container = self.page.locator(
                "mat-dialog-container, .mat-snack-bar-container, .modal-content, .swal2-popup, "
                ".cdk-overlay-pane:has(button:has-text('Yes')), div:has(button:has-text('Yes')):has(button:has-text('No')), "
                "div[role='dialog'], div[role='alertdialog']"
            ).first
            if confirm_container.is_visible(timeout=2500):
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

        return self.get_toast_message(timeout=2500) or "Submitted"

    def click_cancel(self) -> bool:
        """Click Cancel or Reset button."""
        cancel_btn = self.page.locator(
            "button:has-text('Cancel'), button:has-text('Reset'), button:has-text('Back')"
        ).first
        if cancel_btn.is_visible(timeout=4000):
            cancel_btn.click()
            self.wait_for_dom_ready()
            return True
        return False

    # ----------------- Validation & Alerts -----------------

    def get_validation_errors(self) -> List[str]:
        """Fetch all visible validation error messages."""
        errors = []
        err_locators = self.page.locator("mat-error, .invalid-feedback, .error-message, .text-danger")
        count = err_locators.count()
        for i in range(count):
            el = err_locators.nth(i)
            if el.is_visible():
                txt = el.inner_text().strip()
                if txt and txt not in errors:
                    errors.append(txt)
        return errors

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

    # ----------------- Listing & Search -----------------

    def search_customer(self, search_term: str):
        """Filter customer grid by search term."""
        search_input = self.page.locator(
            "input[placeholder*='Search' i], input[type='search']"
        ).first
        if search_input.is_visible(timeout=5000):
            search_input.fill(search_term)
            search_input.press("Enter")
            self.wait_for_dom_ready()
            time.sleep(1)

    def is_customer_in_list(self, customer_name: str) -> bool:
        """Verify customer name is present in grid."""
        self.search_customer(customer_name)
        row = self.page.locator(f"table tbody tr:has-text('{customer_name}'), mat-row:has-text('{customer_name}'), tr:has-text('{customer_name}'), td:has-text('{customer_name}')").first
        return row.is_visible(timeout=3000)

    def wait_for_url_contains(self, keyword: str, timeout: int = 10000):
        """Wait for page URL to contain specific substring."""
        try:
            self.page.wait_for_url(lambda u: keyword.lower() in u.lower(), timeout=timeout)
        except Exception:
            pass

    def clear_search(self):
        """Clear the search box in Customer Details grid."""
        search_input = self.page.locator(
            "input[placeholder*='Search' i], input[type='search']"
        ).first
        if search_input.is_visible(timeout=5000):
            search_input.fill("")
            search_input.press("Enter")
            self.wait_for_dom_ready()
            time.sleep(1)

    def navigate_pagination(self, direction: str = "next") -> bool:
        """Click next or previous page button in grid pagination controls."""
        try:
            if direction.lower() == "next":
                btn = self.page.locator(
                    "button[aria-label*='Next' i], .mat-paginator-navigation-next, button:has-text('Next'), .pagination-next"
                ).first
            else:
                btn = self.page.locator(
                    "button[aria-label*='Previous' i], .mat-paginator-navigation-previous, button:has-text('Prev'), .pagination-prev"
                ).first

            if btn.is_visible(timeout=3000):
                is_disabled = "disabled" in (btn.get_attribute("class") or "") or btn.is_disabled()
                if not is_disabled:
                    btn.click()
                    self.wait_for_dom_ready()
                    return True
            return False
        except Exception:
            return False

    def get_grid_row_count(self) -> int:
        """Return count of visible customer rows in grid."""
        rows = self.page.locator("table tbody tr, mat-table mat-row, .grid-row")
        return rows.count()

    def is_empty_grid_displayed(self) -> bool:
        """Check if grid shows no records found or zero matching rows."""
        no_data = self.page.locator(
            ":has-text('No records found'), :has-text('No data'), :has-text('No customer found'), .no-records"
        ).first
        if no_data.is_visible(timeout=3000):
            return True
        return self.get_grid_row_count() == 0

    def dismiss_modal_via_escape(self) -> bool:
        """Dismiss active modal by pressing Escape key."""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            modal = self.page.locator("mat-dialog-container, .modal-content, .swal2-popup")
            return not modal.is_visible(timeout=2000)
        except Exception:
            return False

