"""Page Object for Purchase Order Update module."""

import time
from typing import Any, Dict, List, Optional
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeout
from shared.pages.base_page import BasePage
from shared.utils.logger import get_logger

log = get_logger("po_update_page")


class POUpdatePage(BasePage):
    """
    Page Object Model for Purchase Order Update workflow.
    
    Navigation Workflow:
    1. /default (Default landing dashboard)
    2. /invoiceReports (Invoicing navigation)
    3. /invoicedashboard (Invoice Home / Dashboard)
    4. /purchaseOrder (Purchase Orders card directly from Invoice Dashboard - bypassing customerDetails)
    5. Click pencil edit button on row -> Purchase Order Update Form
    """

    FIELD_SELECTORS = {
        "po_date": ["input[formcontrolname='date']", "input[name='date']", "mat-form-field:has-text('PO Date') input"],
        "po_ref_no": ["input[formcontrolname='refNo']", "input[name='refNo']", "mat-form-field:has-text('PO Reference No') input"],
        "customer_name": ["mat-select[formcontrolname='poCustomer']", "mat-form-field:has-text('Customer Name') mat-select"],
        "authorized_by": ["input[formcontrolname='authorizedBy']", "input[name='authorizedBy']", "mat-form-field:has-text('Authorized By') input"],
        "po_details": ["textarea[formcontrolname='poDetails']", "textarea[name='poDetails']", "mat-form-field:has-text('PO Details') textarea"],
        "base_amount": ["input[formcontrolname='poBaseAmount']", "input[name='poBaseAmount']", "mat-form-field:has-text('Base Amount') input"],
        "tax_amount": ["input[formcontrolname='poTaxAmount']", "input[name='poTaxAmount']", "mat-form-field:has-text('Tax Amount') input"],
        "total_amount": ["input[formcontrolname='poTotalAmount']", "input[name='poTotalAmount']", "mat-form-field:has-text('Total Amount') input"],
        "currency": ["mat-select[formcontrolname='poCurrency']", "mat-form-field:has-text('Currency') mat-select"],
        "status": ["mat-select[formcontrolname='poStatus']", "mat-form-field:has-text('Status') mat-select"],
        "document_url": ["input#po_document_url", "input[type='file']"],
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

    def open_purchase_order_list(self, direct: bool = False):
        """
        Step 4: Navigate directly to Purchase Order Listing (/purchaseOrder).
        Bypasses the 4th Customer Management step (/customerDetails) and
        navigates straight to /purchaseOrder from Invoice Dashboard.
        """
        url = "/purchaseOrder"
        if direct:
            self.goto(url)
            self.wait_for_dom_ready()
        else:
            if "invoicedashboard" not in self.page.url.lower():
                self.open_invoice_dashboard()

            self.dismiss_any_tutorial_or_dialog()

            card = self.page.locator(
                "h4:has-text('Purchase Orders'), mat-card:has-text('Purchase Orders'), "
                "div.text-wrapper:has-text('Purchase Orders'), [mattooltip*='Purchase Orders' i]"
            ).first

            if card.is_visible(timeout=4000):
                card.click()
                try:
                    self.page.wait_for_url(lambda u: "purchaseorder" in u.lower(), timeout=6000)
                except Exception:
                    self.goto(url)
            else:
                self.goto(url)
            self.wait_for_dom_ready()

        self.dismiss_any_tutorial_or_dialog()
        try:
            self.page.locator("tbody tr td, table").first.wait_for(state="visible", timeout=12000)
        except Exception:
            self.goto(url)
            self.wait_for_dom_ready()
            self.dismiss_any_tutorial_or_dialog()
            self.page.locator("tbody tr td, table").first.wait_for(state="visible", timeout=15000)

    # ----------------- Listing & Row Selection -----------------

    def search_purchase_order(self, query: str) -> int:
        """Search the Purchase Order table by Ref No or Customer Name."""
        search_input = self.page.locator(
            "input[placeholder*='Search' i], input[type='search']"
        ).first
        if search_input.is_visible(timeout=3000):
            search_input.fill(str(query))
            search_input.dispatch_event("input")
            self.page.wait_for_timeout(1000)
        return self.page.locator("tbody tr").count()

    def toggle_include_fully_used_po(self, check: bool = True) -> int:
        """Toggle the 'Include Fully Used PO' checkbox and return new row count."""
        try:
            self.page.wait_for_selector("div.modal-overlay", state="hidden", timeout=5000)
        except Exception:
            pass

        cb_input = self.page.locator("mat-checkbox:has-text('Include Fully Used PO') input[type='checkbox']").first
        cb_container = self.page.locator("mat-checkbox:has-text('Include Fully Used PO')").first
        
        is_checked = cb_input.is_checked() if cb_input.count() else False
        if is_checked != check:
            cb_container.click(force=True)
            self.page.wait_for_timeout(2000)
        return self.page.locator("tbody tr").count()

    def get_purchase_order_rows(self) -> List[Locator]:
        """Return all rows in the purchase order table."""
        return self.page.locator("tbody tr").all()

    def get_first_row_po_ref(self) -> str:
        """Retrieve a non-empty PO Reference number from the first rows."""
        try:
            self.page.locator("tbody tr td").first.wait_for(state="visible", timeout=15000)
            rows = self.page.locator("tbody tr")
            for i in range(min(10, rows.count())):
                ref = rows.nth(i).locator("td").nth(2).inner_text().strip()
                if ref:
                    return ref
            return ""
        except Exception:
            return ""

    def get_row_ref_no(self, row_index: int = 0) -> str:
        """Retrieve PO Reference number of a specific row."""
        try:
            return self.page.locator("tbody tr").nth(row_index).locator("td").nth(2).inner_text().strip()
        except Exception:
            return ""

    def get_row_currency(self, row_index: int = 0) -> str:
        """Retrieve Currency value of a specific row."""
        try:
            return self.page.locator("tbody tr").nth(row_index).locator("td").nth(4).inner_text().strip()
        except Exception:
            return ""

    def get_row_total_amount(self, row_index: int = 0) -> str:
        """Retrieve Total Amount value of a specific row."""
        try:
            return self.page.locator("tbody tr").nth(row_index).locator("td").nth(5).inner_text().strip()
        except Exception:
            return ""

    def get_row_status(self, row_index: int = 0) -> str:
        """Retrieve Status value of a specific row."""
        try:
            return self.page.locator("tbody tr").nth(row_index).locator("td").nth(6).inner_text().strip()
        except Exception:
            return ""

    def press_escape_key(self):
        """Press Escape key to dismiss dialog/popups."""
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def open_po_edit_modal(self, po_ref: Optional[str] = None, row_index: int = 0):
        """
        Step 5: Click the pencil/edit button on target PO row to open the update form.
        """
        self.dismiss_any_tutorial_or_dialog()

        # If no specific po_ref requested, ensure search input is cleared so table is populated
        if not po_ref:
            search_input = self.page.locator("input[placeholder*='Search' i], input[type='search']").first
            if search_input.is_visible(timeout=1000) and search_input.input_value():
                search_input.fill("")
                search_input.dispatch_event("input")
                self.page.wait_for_timeout(1000)

        try:
            self.page.wait_for_selector("tbody tr td button", timeout=10000)
        except Exception:
            pass

        row = None
        if po_ref:
            self.search_purchase_order(po_ref)
            row = self.page.locator("tbody tr").filter(has_text=str(po_ref)).first
        else:
            rows = self.page.locator("tbody tr")
            if rows.count() > row_index:
                row = rows.nth(row_index)
            else:
                row = rows.first

        edit_btn = row.locator(
            "button:has(mat-icon:has-text('edit')), button.btn-link:has-text('edit'), button:has-text('edit'), button"
        ).last
        edit_btn.scroll_into_view_if_needed()
        edit_btn.click(force=True)

        self.page.wait_for_selector("form", timeout=8000)
        self.page.wait_for_timeout(500)

    # ----------------- Update Form Operations -----------------

    def is_update_form_visible(self) -> bool:
        """Check if the PO update form is open and visible."""
        form = self.page.locator("form")
        return form.count() > 0 and form.first.is_visible()

    def is_customer_name_readonly(self) -> bool:
        """Verify Customer Name dropdown/input is disabled or read-only."""
        cust = self.page.locator("mat-form-field:has-text('Customer Name') mat-select, mat-select[formcontrolname='poCustomer']").first
        if cust.count() > 0:
            return cust.evaluate(
                "e => e.hasAttribute('disabled') || e.getAttribute('aria-disabled') === 'true' || e.classList.contains('mat-mdc-select-disabled')"
            )
        return False

    def open_calendar_picker(self) -> bool:
        """Click calendar toggle button on PO Date and verify popup opens."""
        dp_btn = self.page.locator("mat-form-field:has-text('PO Date') mat-datepicker-toggle button, mat-form-field:has-text('PO Date') button").first
        if dp_btn.is_visible(timeout=3000):
            dp_btn.click()
            self.page.wait_for_timeout(500)
            calendar = self.page.locator("mat-calendar, .mat-datepicker-content")
            is_open = calendar.count() > 0 and calendar.first.is_visible()
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(300)
            return is_open
        return False

    def get_currency_options(self) -> List[str]:
        """Open Currency dropdown, get all options, and close dropdown."""
        curr_select = self.page.locator("mat-form-field:has-text('Currency') mat-select, mat-select[formcontrolname='poCurrency']").first
        curr_select.click()
        self.page.wait_for_selector("mat-option", timeout=5000)
        options = [opt.inner_text().strip() for opt in self.page.locator("mat-option").all()]
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(400)
        return options

    def select_currency(self, currency_code: str):
        """Select a currency from the dropdown."""
        curr_select = self.page.locator("mat-form-field:has-text('Currency') mat-select, mat-select[formcontrolname='poCurrency']").first
        curr_select.click()
        self.page.wait_for_selector("mat-option", timeout=5000)
        opt = self.page.locator(f"mat-option:has-text('{currency_code}')").first
        if opt.is_visible(timeout=3000):
            opt.click()
        else:
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def get_status_options(self) -> List[str]:
        """Open Status dropdown, get all options, and close dropdown."""
        status_select = self.page.locator("mat-form-field:has-text('Status') mat-select, mat-select[formcontrolname='poStatus']").first
        status_select.click()
        self.page.wait_for_selector("mat-option", timeout=5000)
        options = [opt.inner_text().strip() for opt in self.page.locator("mat-option").all()]
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(400)
        return options

    def select_status(self, status_name: str):
        """Select a status from the dropdown."""
        status_select = self.page.locator("mat-form-field:has-text('Status') mat-select, mat-select[formcontrolname='poStatus']").first
        status_select.click()
        self.page.wait_for_selector("mat-option", timeout=5000)
        opt = self.page.locator(f"mat-option:has-text('{status_name}')").first
        if opt.is_visible(timeout=3000):
            opt.click()
        else:
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)

    def upload_po_document(self, file_path: str) -> bool:
        """Upload a file using the hidden file input."""
        file_input = self.page.locator("input#po_document_url, input[type='file']").first
        if file_input.count() > 0:
            file_input.set_input_files(file_path)
            self.page.wait_for_timeout(1000)
            return True
        return False

    def get_uploaded_document_text(self) -> str:
        """Return the text inside the PO Document section."""
        doc_section = self.page.locator("form").filter(has_text="PO Document")
        return doc_section.inner_text().strip() if doc_section.count() else ""

    def get_view_current_document_link(self) -> Optional[str]:
        """Check if 'View Current Document' link is present and return its href."""
        link = self.page.locator("a:has-text('View Current Document')").first
        if link.count() > 0 and link.is_visible():
            return link.get_attribute("href")
        return None

    def get_form_field_value(self, field_key: str) -> str:
        """Get the current value of a form field."""
        selectors = self.FIELD_SELECTORS.get(field_key, [f"input[formcontrolname='{field_key}']"])
        for sel in selectors:
            loc = self.page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                tag = loc.first.evaluate("e => e.tagName")
                if tag in ["INPUT", "TEXTAREA"]:
                    return loc.first.input_value()
                return loc.first.inner_text().strip()
        return ""

    def set_form_field(self, field_key: str, value: Any):
        """Set a value in the PO update form."""
        selectors = self.FIELD_SELECTORS.get(field_key, [f"input[formcontrolname='{field_key}']"])
        for sel in selectors:
            loc = self.page.locator(sel)
            if loc.count() > 0 and loc.first.is_visible():
                tag = loc.first.evaluate("e => e.tagName")
                if tag in ["INPUT", "TEXTAREA"]:
                    loc.first.fill(str(value))
                    loc.first.dispatch_event("input")
                    loc.first.dispatch_event("change")
                    return
                elif tag == "MAT-SELECT":
                    loc.first.click()
                    self.page.wait_for_timeout(300)
                    opt = self.page.locator(f"mat-option:has-text('{value}')").first
                    if opt.is_visible(timeout=2000):
                        opt.click()
                    self.page.wait_for_timeout(400)
                    return
        log.warning(f"Could not find field selector for: {field_key}")

    def fill_po_update_form(self, data: Dict[str, Any]):
        """Fill multiple fields in the PO update form."""
        for k, v in data.items():
            self.set_form_field(k, v)

    def click_update(self):
        """Click the Update button in the PO form."""
        btn = self.page.locator("button:has-text('Update')").first
        btn.wait_for(state="visible", timeout=5000)
        self.page.wait_for_timeout(200)
        btn.click()
        self.page.wait_for_timeout(300)

    def click_cancel(self):
        """Click the Cancel button in the PO form."""
        btn = self.page.locator("button:has-text('Cancel')").first
        if btn.is_visible(timeout=3000):
            btn.click()
        else:
            close_btn = self.page.locator("button:has(mat-icon:has-text('close'))").filter(has=self.page.locator(":visible")).first
            close_btn.click()
        try:
            self.page.wait_for_selector("div.modal-overlay, form", state="hidden", timeout=5000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def click_close_icon(self):
        """Click the top-right 'X' close icon on the modal."""
        close_btn = self.page.locator("button:has(mat-icon[color='warn']:has-text('close')), mat-icon[color='warn']:has-text('close')").first
        if close_btn.is_visible(timeout=3000):
            close_btn.click()
        try:
            self.page.wait_for_selector("div.modal-overlay, form", state="hidden", timeout=5000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def get_snackbar_info(self, timeout_ms: int = 7000) -> Dict[str, Any]:
        """Capture snackbar text and whether it's success (green) or error (red)."""
        try:
            sb = self.page.locator("mat-snack-bar-container, .mat-simple-snackbar").first
            sb.wait_for(state="visible", timeout=timeout_ms)
            text = sb.inner_text().strip()
            cls = sb.get_attribute("class") or ""
            return {
                "visible": True,
                "text": text,
                "is_success": "snackbar-success" in cls or "Success" in text or "Updated" in text,
                "is_error": "snackbar-error" in cls or "Error" in text or "Please" in text,
                "class": cls,
            }
        except Exception:
            return {"visible": False, "text": "", "is_success": False, "is_error": False, "class": ""}
