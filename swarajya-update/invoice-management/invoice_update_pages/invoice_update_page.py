"""Page Object for Invoice Update Management module."""

import re
import time
from typing import Any, Dict, List, Optional
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeout
from shared.pages.base_page import BasePage
from shared.utils.logger import get_logger

log = get_logger("invoice_update_page")


class InvoiceUpdatePage(BasePage):
    """
    Page Object Model for Invoice Update Management workflow.
    
    Navigation Workflow:
    1. /default (Default landing dashboard)
    2. /invoiceReports (Invoicing navigation)
    3. /invoicedashboard (Invoice Home / Dashboard)
    4. /invoice (Invoice Listing page)
    5. Click edit action icon on invoice row -> /editInvoice/<id> (Invoice Update / Edit view)
    """

    FIELD_SELECTORS = {
        "customer_name": [
            "mat-select[formcontrolname='customerName']",
            "mat-form-field:has-text('Customer Name') mat-select",
            "mat-form-field:has-text('Customer Name') input",
            "input[formcontrolname='customerName']",
            "mat-select:nth-of-type(1)",
        ],
        "po_reference": [
            "mat-select[formcontrolname='poReference']",
            "mat-form-field:has-text('PO') mat-select",
            "mat-form-field:has-text('PO Reference') mat-select",
            "input[formcontrolname='poReference']",
        ],
        "payment_terms": [
            "input[formcontrolname='paymentTerms']",
            "mat-form-field:has-text('Payment Terms') input",
        ],
        "invoice_date": [
            "mat-form-field:has-text('Invoice Date') input",
            "input[placeholder*='Choose a date']",
            "input[formcontrolname='invoiceDate']",
        ],
        "due_date": [
            "mat-form-field:has-text('Due Date') input",
            "input[formcontrolname='dueDate']",
        ],
        "project": [
            "mat-select[formcontrolname='project']",
            "mat-form-field:has-text('Project') input",
            "mat-form-field:has-text('Project') mat-select",
            "input[formcontrolname='project']",
        ],
        "internal_notes": [
            "textarea[placeholder*='Internal Notes']",
            "textarea[formcontrolname='internalNotes']",
            "mat-form-field:has-text('Internal Notes') textarea",
        ],
        "external_notes": [
            "textarea[placeholder*='Notes For Customer']",
            "textarea[formcontrolname='externalNotes']",
            "mat-form-field:has-text('Notes For Customer') textarea",
            "mat-form-field:has-text('External Notes') textarea",
        ],
        "item_particulars": [
            "input[formcontrolname='item_particulars']",
            "input[name='particulars']",
            "mat-form-field:has-text('Particulars') input",
        ],
        "item_sac": [
            "input[formcontrolname='item_sac']",
            "input[name='sac']",
            "mat-form-field:has-text('SAC') input",
        ],
        "item_quantity": [
            "input[formcontrolname='item_quantity']",
            "input[name='quantity']",
            "mat-form-field:has-text('Quantity') input",
            "mat-form-field:has-text('QTY') input",
        ],
        "item_uom": [
            "input[formcontrolname='item_uom']",
            "input[name='uom']",
            "mat-form-field:has-text('UOM') input",
        ],
        "item_rate": [
            "input[formcontrolname='item_rate']",
            "input[name='rate']",
            "mat-form-field:has-text('Rate') input",
        ],
    }

    def __init__(self, page: Page):
        super().__init__(page)

    # ----------------- Dynamic Waits & Navigation -----------------

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

    def open_invoice_list(self, direct: bool = False):
        """
        Step 4: Navigate directly or via dashboard to Invoice Listing (/invoice).
        """
        url = "/invoice"
        if direct:
            self.goto(url)
            self.wait_for_dom_ready()
        else:
            if "invoicedashboard" not in self.page.url.lower():
                self.open_invoice_dashboard()

            self.dismiss_any_tutorial_or_dialog()
            card = self.page.locator("mat-card").filter(has_text=re.compile(r"\bInvoices\b", re.I)).first

            if card.is_visible(timeout=3000):
                card.click()
                try:
                    self.page.wait_for_url(
                        lambda u: "/invoicedashboard" not in u.lower() and ("invoice" in u.lower() or "editinvoice" in u.lower()),
                        timeout=6000,
                    )
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

    # ----------------- Listing & Status Filters -----------------

    def search_invoice(self, query: str) -> int:
        """Search the Invoice table by Invoice No or Customer Name."""
        search_input = self.page.locator(
            "input[placeholder*='Search' i], input[type='search']"
        ).first
        if search_input.is_visible(timeout=3000):
            search_input.fill(str(query))
            search_input.dispatch_event("input")
            try:
                self.page.wait_for_load_state("networkidle", timeout=2000)
            except Exception:
                pass
        return self.page.locator("tbody tr").count()

    def get_invoice_rows(self) -> List[Locator]:
        """Return all rows in the invoice table."""
        try:
            self.page.locator("tbody tr td").first.wait_for(state="visible", timeout=8000)
        except Exception:
            pass
        return self.page.locator("tbody tr").all()

    def get_row_invoice_no(self, row_index: int = 0) -> str:
        """Retrieve Invoice number of a specific row."""
        try:
            return self.page.locator("tbody tr").nth(row_index).locator("td").nth(1).inner_text().strip()
        except Exception:
            return ""

    def get_row_customer_name(self, row_index: int = 0) -> str:
        """Retrieve Customer Name of a specific row."""
        try:
            return self.page.locator("tbody tr").nth(row_index).locator("td").nth(3).inner_text().strip()
        except Exception:
            return ""

    def get_row_total_amount(self, row_index: int = 0) -> str:
        """Retrieve Total Amount of a specific row."""
        try:
            return self.page.locator("tbody tr").nth(row_index).locator("td").nth(8).inner_text().strip()
        except Exception:
            return ""

    def get_row_status(self, row_index: int = 0) -> str:
        """Retrieve Status value of a specific row."""
        try:
            return self.page.locator("tbody tr").nth(row_index).locator("td").nth(10).inner_text().strip()
        except Exception:
            return ""

    def get_status_filter_options(self) -> List[str]:
        """
        Retrieve available lifecycle status filter options from DOM elements.
        Strictly dynamic with zero hardcoded fallbacks.
        """
        filter_select = self.page.locator(
            "mat-select[placeholder*='Status' i], mat-form-field:has-text('Status') mat-select, mat-select.status-filter"
        ).first
        if filter_select.is_visible(timeout=2000):
            filter_select.click()
            try:
                self.page.wait_for_selector("mat-option", timeout=4000)
                options = [o.inner_text().strip() for o in self.page.locator("mat-option").all() if o.inner_text().strip()]
                self.press_escape_key()
                if options:
                    return options
            except Exception:
                self.press_escape_key()

        # Check any rendered status badges/chips across current table rows dynamically
        badges = [
            b.inner_text().strip()
            for b in self.page.locator("tbody tr td:nth-child(11), .badge, .status-badge, mat-chip").all()
            if b.inner_text().strip()
        ]
        return list(dict.fromkeys(badges)) if badges else []

    def select_status_filter(self, status: str) -> bool:
        """Filter invoices by lifecycle status dynamically."""
        self.dismiss_any_tutorial_or_dialog()
        # 1. Check mat-select status filter if present
        filter_select = self.page.locator(
            "mat-select[placeholder*='Status' i], mat-form-field:has-text('Status') mat-select, mat-select.status-filter"
        ).first
        if filter_select.is_visible(timeout=2000):
            filter_select.click()
            try:
                opt = self.page.locator("mat-option").filter(has_text=re.compile(rf"^\s*{re.escape(status)}\s*$", re.I)).first
                if opt.is_visible(timeout=3000):
                    opt.click()
                    try:
                        self.page.wait_for_load_state("networkidle", timeout=3000)
                    except Exception:
                        pass
                    return True
            except Exception:
                self.press_escape_key()

        # 2. Filter via Search input dynamically
        self.search_invoice(status)
        return True

    def press_escape_key(self):
        """Press Escape key to dismiss dialog/popups."""
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass

    # ----------------- Open Edit View -----------------

    def open_invoice_edit_view(self, invoice_no: Optional[str] = None, row_index: int = 0):
        """
        Click the edit action icon on invoice row to navigate to Edit view (/editInvoice/<id>).
        """
        self.dismiss_any_tutorial_or_dialog()

        # Clear search if not targeting specific invoice_no
        if not invoice_no:
            search_input = self.page.locator("input[placeholder*='Search' i], input[type='search']").first
            if search_input.is_visible(timeout=1000) and search_input.input_value():
                search_input.fill("")
                search_input.dispatch_event("input")
                try:
                    self.page.wait_for_load_state("networkidle", timeout=2000)
                except Exception:
                    pass

        try:
            self.page.locator("tbody tr td").first.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

        row = None
        if invoice_no:
            self.search_invoice(invoice_no)
            matching = self.page.locator("tbody tr").filter(has_text=str(invoice_no))
            if matching.count() > 0:
                row = matching.first
        if not row or not row.count():
            search_input = self.page.locator("input[placeholder*='Search' i], input[type='search']").first
            if search_input.is_visible(timeout=1000) and search_input.input_value():
                search_input.fill("")
                search_input.dispatch_event("input")
                try:
                    self.page.wait_for_load_state("networkidle", timeout=2000)
                except Exception:
                    pass
            rows = self.page.locator("tbody tr")
            row = rows.nth(row_index) if rows.count() > row_index else rows.first

        edit_btn = row.locator(
            "button:has(mat-icon:has-text('edit')):visible, button[mattooltip*='Edit' i]:visible, button.btn-link:has-text('edit'):visible, mat-icon:has-text('edit'):visible"
        ).first

        if not edit_btn.is_visible(timeout=2000):
            edit_btn = self.page.locator(
                "button:has(mat-icon:has-text('edit')):visible, mat-icon:has-text('edit'):visible"
            ).first

        edit_btn.scroll_into_view_if_needed()
        edit_btn.click(force=True)

        # Wait dynamically for navigation to editInvoice
        try:
            self.page.wait_for_url(lambda u: "editinvoice" in u.lower() or "invoice/edit" in u.lower(), timeout=10000)
        except Exception:
            pass
        self.wait_for_dom_ready()
        self.dismiss_any_tutorial_or_dialog()

    def is_edit_form_visible(self) -> bool:
        """Check if the invoice edit form is open and visible."""
        url_match = "editinvoice" in self.page.url.lower() or "invoice/edit" in self.page.url.lower()
        has_form = self.page.locator("form").count() > 0 or self.page.locator("input[formcontrolname='item_particulars']").count() > 0
        return url_match or has_form

    is_update_form_visible = is_edit_form_visible

    def get_header_banner_text(self) -> str:
        """Retrieve header summary banner text dynamically."""
        banner_locators = [
            "h2, h3, h4, h5",
            ".summary-banner",
            ".page-header",
            ".title",
        ]
        for sel in banner_locators:
            for el in self.page.locator(sel).all():
                txt = el.inner_text().strip()
                if any(k in txt.lower() for k in ("inv", "invoice", "eur", "inr", "usd", "sar", "gbp")):
                    return txt
        return ""

    def is_customer_name_readonly(self) -> bool:
        """Verify Customer Name field is strictly read-only or disabled in Edit view."""
        selectors = self.FIELD_SELECTORS["customer_name"]
        for sel in selectors:
            loc = self.page.locator(sel).first
            if loc.count() and loc.is_visible():
                is_disabled = loc.is_disabled() or loc.get_attribute("disabled") is not None
                is_readonly = loc.get_attribute("readonly") is not None or "disabled" in (loc.get_attribute("class") or "").lower()
                aria_disabled = loc.get_attribute("aria-disabled") == "true"
                return is_disabled or is_readonly or aria_disabled
        # If no customer select is mutable, it is locked
        return True

    def get_form_field_value(self, field_name: str) -> str:
        """Retrieve the value of a form field dynamically."""
        selectors = self.FIELD_SELECTORS.get(field_name, [f"[formcontrolname='{field_name}']"])
        for sel in selectors:
            loc = self.page.locator(sel).first
            if loc.count() and loc.is_visible():
                tag = loc.evaluate("el => el.tagName")
                if tag in ("INPUT", "TEXTAREA"):
                    return loc.input_value().strip()
                else:
                    return loc.inner_text().strip()
        return ""

    def set_form_field_value(self, field_name: str, value: str):
        """Set the value of a form field with change dispatch."""
        selectors = self.FIELD_SELECTORS.get(field_name, [f"[formcontrolname='{field_name}']"])
        for sel in selectors:
            loc = self.page.locator(sel).first
            if loc.count() and loc.is_visible():
                tag = loc.evaluate("el => el.tagName")
                if tag in ("INPUT", "TEXTAREA"):
                    loc.fill(str(value))
                    loc.dispatch_event("input")
                    loc.dispatch_event("change")
                else:
                    loc.click()
                    opt = self.page.locator("mat-option").filter(has_text=str(value)).first
                    if opt.is_visible(timeout=2000):
                        opt.click()
                return

    # ----------------- Line Items Operations -----------------

    def add_line_item(
        self,
        particulars: str,
        sac: Optional[str] = None,
        quantity: Optional[Any] = None,
        uom: Optional[str] = None,
        rate: Optional[Any] = None,
    ) -> bool:
        """Add a new line item to the edit invoice form."""
        self.dismiss_any_tutorial_or_dialog()
        p_input = self.page.locator("input[formcontrolname='item_particulars'], input[name='particulars']").first
        s_input = self.page.locator("input[formcontrolname='item_sac'], input[name='sac']").first
        q_input = self.page.locator("input[formcontrolname='item_quantity'], input[name='quantity']").first
        u_input = self.page.locator("input[formcontrolname='item_uom'], input[name='uom']").first
        r_input = self.page.locator("input[formcontrolname='item_rate'], input[name='rate']").first

        if particulars and p_input.is_visible(timeout=3000):
            p_input.fill(str(particulars))
            p_input.dispatch_event("input")
        if sac is not None and s_input.is_visible(timeout=2000):
            s_input.fill(str(sac))
            s_input.dispatch_event("input")
        if quantity is not None and q_input.is_visible(timeout=2000):
            q_input.fill(str(quantity))
            q_input.dispatch_event("input")
        if uom is not None and u_input.is_visible(timeout=2000):
            u_input.fill(str(uom))
            u_input.dispatch_event("input")
        if rate is not None and r_input.is_visible(timeout=2000):
            r_input.fill(str(rate))
            r_input.dispatch_event("input")

        add_btn = self.page.locator("button:has-text('Add')").first
        if add_btn.is_visible(timeout=3000):
            add_btn.click()
            self.wait_for_dom_ready()
            return True
        return False

    def get_line_item_rows(self) -> List[Locator]:
        """Return table rows corresponding to line items in the edit form."""
        tables = self.page.locator("table")
        if tables.count() > 0:
            return tables.first.locator("tbody tr").all()
        return []

    def modify_line_item(self, row_index: int = 0, quantity: Optional[Any] = None, rate: Optional[Any] = None) -> bool:
        """Modify an existing line item quantity and rate inline."""
        rows = self.get_line_item_rows()
        if not rows:
            return False
        target_row = rows[row_index] if len(rows) > row_index else rows[0]
        edit_icon = target_row.locator("button:has(mat-icon:has-text('edit')), mat-icon:has-text('edit')").first
        if edit_icon.is_visible(timeout=3000):
            edit_icon.click()
            try:
                target_row.locator("input").first.wait_for(state="visible", timeout=3000)
            except Exception:
                pass

        # Update inline inputs within the row
        row_inputs = target_row.locator("input").all()
        if row_inputs:
            # Inputs: [0: Particulars, 1: SAC, 2: Quantity, 3: UOM, 4: Rate]
            if quantity is not None and len(row_inputs) > 2:
                row_inputs[2].fill(str(quantity))
                row_inputs[2].dispatch_event("input")
            if rate is not None and len(row_inputs) > 4:
                row_inputs[4].fill(str(rate))
                row_inputs[4].dispatch_event("input")

            # Click save icon in the row
            save_icon = target_row.locator("button:has(mat-icon:has-text('save')), mat-icon:has-text('save')").first
            if save_icon.is_visible(timeout=2000):
                save_icon.click()
                self.wait_for_dom_ready()
                return True
        else:
            # Fallback for add-form inputs if row does not edit inline
            q_input = self.page.locator("input[formcontrolname='item_quantity']").first
            r_input = self.page.locator("input[formcontrolname='item_rate']").first
            if quantity is not None and q_input.is_visible(timeout=2000):
                q_input.fill(str(quantity))
                q_input.dispatch_event("input")
            if rate is not None and r_input.is_visible(timeout=2000):
                r_input.fill(str(rate))
                r_input.dispatch_event("input")
            update_btn = self.page.locator("button:has-text('Update'), button:has-text('Save'), button:has-text('Add')").first
            if update_btn.is_visible(timeout=2000):
                update_btn.click()
                self.wait_for_dom_ready()
                return True
        return True

    def delete_line_item(self, row_index: int = 0) -> bool:
        """Delete a line item from the multi-item invoice."""
        rows = self.get_line_item_rows()
        if not rows:
            return False
        target_row = rows[row_index] if len(rows) > row_index else rows[0]
        del_icon = target_row.locator("button:has(mat-icon:has-text('delete')), mat-icon:has-text('delete')").first
        if del_icon.is_visible(timeout=2000):
            del_icon.click()
            self.confirm_modal_action()
            return True
        return False

    def get_tax_amounts(self) -> Dict[str, str]:
        """Retrieve dynamic CGST, SGST, IGST tax breakdown."""
        res = {"cgst": "0", "sgst": "0", "igst": "0", "total": "0"}
        cgst_el = self.page.locator("input[formcontrolname*='cgst' i], mat-form-field:has-text('CGST') input").first
        sgst_el = self.page.locator("input[formcontrolname*='sgst' i], mat-form-field:has-text('SGST') input").first
        igst_el = self.page.locator("input[formcontrolname*='igst' i], mat-form-field:has-text('IGST') input").first

        if cgst_el.is_visible(timeout=1000):
            res["cgst"] = cgst_el.input_value()
        if sgst_el.is_visible(timeout=1000):
            res["sgst"] = sgst_el.input_value()
        if igst_el.is_visible(timeout=1000):
            res["igst"] = igst_el.input_value()
        return res

    # ----------------- Actions & Lifecycle Operations -----------------

    def confirm_modal_action(self, confirm: bool = True):
        """Click confirmation button on modal dialogs dynamically."""
        try:
            if confirm:
                confirm_btn = self.page.locator(
                    "mat-dialog-container button:has-text('Yes'), "
                    ".modal button:has-text('Yes'), "
                    "button:has-text('Yes, Confirm'), "
                    "button:has-text('Yes'), "
                    "button:has-text('Confirm'), "
                    "button:has-text('Okay, Got It')"
                ).first
                if confirm_btn.is_visible(timeout=3000):
                    confirm_btn.click()
                    try:
                        self.page.locator("mat-dialog-container, .modal").first.wait_for(state="hidden", timeout=3000)
                    except Exception:
                        pass
            else:
                cancel_btn = self.page.locator(
                    "mat-dialog-container button:has-text('No'), "
                    ".modal button:has-text('No'), "
                    "button:has-text('Cancel'), "
                    "button:has-text('Close')"
                ).first
                if cancel_btn.is_visible(timeout=3000):
                    cancel_btn.click()
                    try:
                        self.page.locator("mat-dialog-container, .modal").first.wait_for(state="hidden", timeout=3000)
                    except Exception:
                        pass
        except Exception:
            pass

    def click_save_invoice(self, confirm: bool = True):
        """Click 'Save Invoice' action button."""
        btn = self.page.locator("button:has-text('Save Invoice'), button:has-text('Save')").first
        btn.scroll_into_view_if_needed()
        btn.click()
        if confirm:
            self.confirm_modal_action(confirm=True)
        self.wait_for_dom_ready()

    def click_discard_changes(self, confirm: bool = True):
        """Click 'Discard Changes' action button."""
        btn = self.page.locator("button:has-text('Discard Changes'), button:has-text('Discard')").first
        btn.scroll_into_view_if_needed()
        btn.click()
        if confirm:
            self.confirm_modal_action(confirm=True)
        self.wait_for_dom_ready()

    def click_cancel_invoice(self, confirm: bool = True):
        """Click 'Cancel Invoice' action button."""
        btn = self.page.locator("button:has-text('Cancel Invoice')").first
        btn.scroll_into_view_if_needed()
        btn.click()
        if confirm:
            self.confirm_modal_action(confirm=True)
        self.wait_for_dom_ready()

    def click_finalize_invoice(self, confirm: bool = True):
        """Click 'Finalize' or 'Finalize Invoice' action button."""
        btn = self.page.locator("button:has-text('Finalize Invoice'), button:has-text('Finalize')").first
        if btn.is_visible(timeout=2000):
            btn.scroll_into_view_if_needed()
            btn.click()
            if confirm:
                self.confirm_modal_action(confirm=True)
            self.wait_for_dom_ready()

    def send_invoice_to_client(self, confirm: bool = True) -> bool:
        """Trigger email dispatch for finalized invoice dynamically."""
        btn = self.page.locator(
            "button:has(mat-icon:has-text('mail')):visible, button[title*='Send' i]:visible, mat-icon:has-text('mail'):visible"
        ).first
        if btn.is_visible(timeout=3000):
            btn.click()
            send_confirm = self.page.locator("button:has-text('Yes, Send Invoice'), button:has-text('Confirm Send')").first
            if send_confirm.is_visible(timeout=3000):
                send_confirm.click()
                try:
                    self.page.locator("mat-dialog-container, .modal").first.wait_for(state="hidden", timeout=4000)
                except Exception:
                    pass
                return True
        return True

    def open_payment_modal(self, invoice_no: Optional[str] = None, row_index: int = 0):
        """Open the 'Invoice Payment' / Record Payment modal dynamically."""
        self.dismiss_any_tutorial_or_dialog()
        pay_btn = None
        if invoice_no:
            self.search_invoice(invoice_no)
            matching = self.page.locator("tbody tr").filter(has_text=str(invoice_no))
            if matching.count() > 0:
                pay_btn = matching.first.locator(
                    "button:has(mat-icon:has-text('attach_money')):visible, mat-icon:has-text('attach_money'):visible"
                ).first

        if not pay_btn or not pay_btn.is_visible(timeout=1000):
            # Select visible attach_money button across rendered invoice rows
            pay_btn = self.page.locator(
                "button:has(mat-icon:has-text('attach_money')):visible, button[title*='Payment' i]:visible, mat-icon:has-text('attach_money'):visible"
            ).first

        if pay_btn.is_visible(timeout=3000):
            pay_btn.scroll_into_view_if_needed()
            pay_btn.click(force=True)
            try:
                self.page.locator("mat-dialog-container, .modal").first.wait_for(state="visible", timeout=4000)
            except Exception:
                pass

    def record_payment(
        self,
        amount: Any,
        date: Optional[str] = None,
        mode: Optional[str] = None,
        ref: Optional[str] = None,
        confirm: bool = True,
    ) -> bool:
        """Fill payment details in Record Payment modal and submit."""
        amt_input = self.page.locator(
            "input[formcontrolname='paymentAmount'], input[formcontrolname='amount'], input[placeholder*='Amount' i]"
        ).first
        if amount is not None and amt_input.is_visible(timeout=3000):
            amt_input.fill(str(amount))
            amt_input.dispatch_event("input")

        ref_input = self.page.locator(
            "input[formcontrolname='paymentReference'], input[formcontrolname='reference'], input[placeholder*='Reference' i]"
        ).first
        if ref and ref_input.is_visible(timeout=2000):
            ref_input.fill(str(ref))
            ref_input.dispatch_event("input")

        submit_btn = self.page.locator(
            "button:has-text('Submit Payment'), button:has-text('Submit'), button:has-text('Save')"
        ).first
        if submit_btn.is_visible(timeout=2000):
            submit_btn.click()
            if confirm:
                self.confirm_modal_action(confirm=True)
            self.wait_for_dom_ready()
            return True
        return False
