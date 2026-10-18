"""
Page Object Model for Invoice Management:
- Invoice Dashboard & List (/invoice)
- Create New Invoice Form (/generateNewInvoice)
"""

import logging
from typing import List, Optional
from playwright.sync_api import Page, Locator

log = logging.getLogger(__name__)


class InvoicePage:
    """Page object encapsulating interactions on Invoice List and Create Invoice pages."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # --- Navigation ---

    def navigate_to_invoice_dashboard(self) -> None:
        """Navigate to the main Invoice dashboard (/invoice)."""
        url = f"{self.base_url}/invoice"
        log.info("Navigating to Invoice Dashboard: %s", url)
        self.page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        try:
            self.page.wait_for_selector("table, button:has-text('New Invoice')", timeout=15_000)
            self.page.wait_for_timeout(1000)
        except Exception:
            pass
        self.dismiss_intro_tour()


    def navigate_to_new_invoice(self) -> None:
        """Navigate directly or via 'New Invoice' button to the creation form."""
        self.navigate_to_invoice_dashboard()
        new_inv_btn = self.page.locator("button, a").filter(has_text="New Invoice").first
        if new_inv_btn.is_visible(timeout=5_000):
            new_inv_btn.click()
            self.page.wait_for_url(lambda u: "generateNewInvoice" in u or "invoice" in u, timeout=10_000)
        else:
            self.page.goto(f"{self.base_url}/generateNewInvoice", wait_until="domcontentloaded", timeout=20_000)
        self.dismiss_intro_tour()

    def dismiss_intro_tour(self) -> None:
        """Dismiss intro walkthrough modal if present on page."""
        try:
            skip_btn = self.page.locator("button:has-text('Skip Intro'), button:has-text('close')").first
            if skip_btn.is_visible(timeout=1_500):
                skip_btn.click()
                self.page.wait_for_timeout(500)
        except Exception:
            pass

    # --- Locators: Header & Meta Fields ---

    @property
    def customer_select(self) -> Locator:
        return self.page.locator("select[name='vendor']")

    @property
    def po_select(self) -> Locator:
        return self.page.locator("select[name='purchase']")

    @property
    def invoice_date_input(self) -> Locator:
        return self.page.locator("input[name='po_date']")

    @property
    def due_date_input(self) -> Locator:
        return self.page.locator("input[name='po_due_date']")

    @property
    def invoice_for_input(self) -> Locator:
        return self.page.locator("input#invoiceFor, input[name='invoiceFor']")

    @property
    def internal_notes_input(self) -> Locator:
        return self.page.locator("textarea#invoiceComments, textarea[name='invoiceComments']")

    @property
    def external_notes_input(self) -> Locator:
        return self.page.locator("textarea#notesForCustomer, textarea[name='notesForCustomer']")

    # --- Locators: Line Items Input Block ---

    @property
    def item_particulars_input(self) -> Locator:
        return self.page.locator("input[formcontrolname='item_particulars']")

    @property
    def item_sac_input(self) -> Locator:
        return self.page.locator("input[formcontrolname='item_sac']")

    @property
    def item_quantity_input(self) -> Locator:
        return self.page.locator("input[formcontrolname='item_quantity']")

    @property
    def item_uom_input(self) -> Locator:
        return self.page.locator("input[formcontrolname='item_uom']")

    @property
    def item_rate_input(self) -> Locator:
        return self.page.locator("input[formcontrolname='item_rate']")

    @property
    def add_item_button(self) -> Locator:
        return self.page.locator("button:has-text('Add')").first

    # --- Locators: Primary Action Buttons ---

    @property
    def finalize_button(self) -> Locator:
        return self.page.locator("button:has-text('Finalize Invoice')").first

    @property
    def discard_button(self) -> Locator:
        return self.page.locator("button:has-text('Discard Changes')").first

    @property
    def save_draft_button(self) -> Locator:
        return self.page.locator("button:has-text('Save as Draft')").first

    # --- Locators: Line Items Table ---

    @property
    def line_items_headers(self) -> List[str]:
        return self.page.locator("table thead th").all_inner_texts()

    @property
    def line_items_rows(self) -> Locator:
        return self.page.locator("table tbody tr")

    # --- Interactions ---

    def select_customer(self, customer_name: str) -> bool:
        """Select customer by visible text from dropdown."""
        if not customer_name:
            return False
        try:
            self.customer_select.select_option(label=customer_name.strip())
            return True
        except Exception:
            # Fallback search option value
            options = self.customer_select.locator("option").all()
            for opt in options:
                txt = opt.inner_text().strip()
                if customer_name.strip().lower() in txt.lower():
                    val = opt.get_attribute("value")
                    if val:
                        self.customer_select.select_option(value=val)
                        return True
            return False

    def select_po(self, po_text: str) -> bool:
        """Select purchase order reference if present."""
        if not po_text:
            return False
        try:
            self.po_select.select_option(label=po_text.strip())
            return True
        except Exception:
            return False

    def enter_invoice_date(self, date_str: str) -> None:
        """Set invoice date."""
        if date_str:
            self.invoice_date_input.fill(str(date_str).strip())

    def enter_due_date(self, date_str: str) -> None:
        """Set payment due date."""
        if date_str:
            self.due_date_input.fill(str(date_str).strip())

    def enter_project(self, project_name: str) -> None:
        """Enter invoice project title."""
        if project_name:
            self.invoice_for_input.fill(str(project_name).strip())

    def enter_internal_notes(self, notes: str) -> None:
        """Enter internal confidential notes."""
        if notes:
            self.internal_notes_input.fill(str(notes).strip())

    def enter_external_notes(self, notes: str) -> None:
        """Enter customer-facing notes."""
        if notes:
            self.external_notes_input.fill(str(notes).strip())

    def fill_line_item(
        self,
        particulars: str,
        sac: str = "",
        quantity: str = "1",
        uom: str = "Hours",
        rate: str = "1000",
    ) -> None:
        """Fill line item input controls."""
        if particulars:
            self.item_particulars_input.fill(str(particulars).strip())
        if sac:
            self.item_sac_input.fill(str(sac).strip())
        if quantity:
            self.item_quantity_input.fill(str(quantity).strip())
        if uom:
            self.item_uom_input.fill(str(uom).strip())
        if rate:
            self.item_rate_input.fill(str(rate).strip())

    def click_add_item(self) -> None:
        """Click the Add button to append the line item."""
        self.add_item_button.click()
        self.page.wait_for_timeout(800)

    def delete_line_item(self, index: int = 0) -> None:
        """Delete line item row at given index."""
        del_btn = self.line_items_rows.nth(index).locator("button, i, a").filter(has_text="Delete").or_(
            self.line_items_rows.nth(index).locator(".fa-trash, .mat-icon:has-text('delete')")
        ).first
        if del_btn.is_visible():
            del_btn.click()
            self.page.wait_for_timeout(500)

    # --- Modal Confirmation Dialog Handlers ---

    def is_modal_visible(self) -> bool:
        """Check if confirmation modal / alert dialog is open."""
        return self.page.locator(".modal, mat-dialog-container, .swal2-container, .cdk-overlay-pane").first.is_visible()

    def confirm_modal(self) -> None:
        """Click confirm/OK button on modal."""
        btn = self.page.locator(
            "button:has-text('Yes'), button:has-text('Confirm'), button:has-text('OK'), button:has-text('Discard')"
        ).first
        if btn.is_visible():
            btn.click()
            self.page.wait_for_timeout(1000)

    def cancel_modal(self) -> None:
        """Click cancel/dismiss button on modal."""
        btn = self.page.locator(
            "button:has-text('No'), button:has-text('Cancel'), button:has-text('Close'), .close"
        ).first
        if btn.is_visible():
            btn.click()
            self.page.wait_for_timeout(1000)

    def dismiss_modal_via_backdrop_or_esc(self) -> None:
        """Dismiss modal using ESC key or clicking outside."""
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(800)
