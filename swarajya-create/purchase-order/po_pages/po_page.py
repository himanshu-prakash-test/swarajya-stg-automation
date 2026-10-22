"""
Page Object Model for Purchase Order Creation:
- Purchase Order Dashboard & Listing (/purchaseOrder)
- Add New Purchase Order Modal Form
Dynamic waits and zero hardcoding are strictly enforced.
"""

import logging
import os
from typing import Any, Dict, List, Optional
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeout

log = logging.getLogger(__name__)


class POPage:
    """Page object encapsulating interactions on Purchase Order list and Create PO modal."""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # --- Navigation ---

    def navigate_to_po_dashboard(self) -> None:
        """Navigate to the Purchase Order dashboard (/purchaseOrder) with dynamic waits."""
        url = f"{self.base_url}/purchaseOrder"
        log.info("Navigating to PO Dashboard: %s", url)
        self.page.goto(url, wait_until="domcontentloaded", timeout=25_000)
        self.dismiss_intro_tour()
        try:
            self.page.wait_for_selector("table, tbody tr td, button:has-text('Add New')", timeout=15_000)
        except Exception:
            pass
        self.dismiss_intro_tour()

    def open_create_po_modal(self) -> None:
        """Open the Add New Purchase Order modal and wait for dynamic readiness."""
        if self.is_create_modal_visible():
            self.dismiss_intro_tour()
            return

        self.navigate_to_po_dashboard()
        self.dismiss_intro_tour()

        try:
            self.page.locator("mat-card.modal-card").wait_for(state="hidden", timeout=3_000)
        except Exception:
            pass

        add_btn = self.page.locator(
            "button:has-text('Add New'), button:has-text('Purchase Order'), button:has-text('Add PO')"
        ).first
        add_btn.wait_for(state="visible", timeout=12_000)
        add_btn.click()

        self.modal_container.wait_for(state="visible", timeout=12_000)
        self.dismiss_intro_tour()

    def dismiss_intro_tour(self) -> None:
        """Dismiss intro walkthrough modal if present on page without blocking."""
        try:
            skip_btn = self.page.locator("button:has-text('Skip Intro'), button:has-text('close')").first
            if skip_btn.is_visible(timeout=1_200):
                skip_btn.click()
        except Exception:
            pass

    # --- Container & Modal Locators ---

    @property
    def modal_container(self) -> Locator:
        return self.page.locator("mat-card.modal-card").first

    def is_create_modal_visible(self) -> bool:
        """Check if Create PO modal is currently visible."""
        try:
            return self.page.locator("mat-card.modal-card").first.is_visible(timeout=1_500)
        except Exception:
            return False

    # --- Form Field Locators ---

    @property
    def date_input(self) -> Locator:
        return self.page.locator("mat-card.modal-card input[name='date'], input[formcontrolname='date']").first

    @property
    def calendar_button(self) -> Locator:
        return self.page.locator("mat-card.modal-card button[aria-label='Open calendar'], mat-card.modal-card button:has(mat-icon:has-text('calendar'))").first

    @property
    def ref_no_input(self) -> Locator:
        return self.page.locator("mat-card.modal-card input[name='refNo'], input[formcontrolname='refNo']").first

    @property
    def customer_select(self) -> Locator:
        return self.page.locator("mat-card.modal-card mat-select[name='poCustomer'], mat-select[formcontrolname='poCustomer']").first

    @property
    def authorized_by_input(self) -> Locator:
        return self.page.locator("mat-card.modal-card input[name='authorizedBy'], input[formcontrolname='authorizedBy']").first

    @property
    def details_textarea(self) -> Locator:
        return self.page.locator("mat-card.modal-card textarea[name='poDetails'], textarea[formcontrolname='poDetails']").first

    @property
    def base_amount_input(self) -> Locator:
        return self.page.locator("mat-card.modal-card input[name='poBaseAmount'], input[formcontrolname='poBaseAmount']").first

    @property
    def tax_amount_input(self) -> Locator:
        return self.page.locator("mat-card.modal-card input[name='poTaxAmount'], input[formcontrolname='poTaxAmount']").first

    @property
    def total_amount_input(self) -> Locator:
        return self.page.locator("mat-card.modal-card input[name='poTotalAmount'], input[formcontrolname='poTotalAmount']").first

    @property
    def currency_select(self) -> Locator:
        return self.page.locator("mat-card.modal-card mat-select[name='poCurrency'], mat-select[formcontrolname='poCurrency']").first

    @property
    def status_select(self) -> Locator:
        return self.page.locator("mat-card.modal-card mat-select[name='poStatus'], mat-select[formcontrolname='poStatus']").first

    @property
    def file_input(self) -> Locator:
        return self.page.locator("input#po_document_url_add, input[type='file']").first

    @property
    def choose_file_button(self) -> Locator:
        return self.page.locator("mat-card.modal-card button:has-text('Choose File')").first

    @property
    def add_button(self) -> Locator:
        return self.page.locator("mat-card.modal-card button:has-text('Add'), button:has-text('Save'), button:has-text('Create')").first

    @property
    def cancel_button(self) -> Locator:
        return self.page.locator("mat-card.modal-card button:has-text('Cancel')").first

    @property
    def close_icon_button(self) -> Locator:
        return self.page.locator(
            ".modal-card-header button, mat-card.modal-card button:has(mat-icon:has-text('close')), mat-icon:has-text('close')"
        ).first

    # --- Actions & Inputs ---

    def select_customer(self, customer_name: Optional[str] = None) -> str:
        """Open customer dropdown and select an option by text or fallback to first active customer."""
        cust_sel = self.customer_select
        cust_sel.wait_for(state="visible", timeout=10_000)

        trigger = cust_sel.locator(".mat-mdc-select-trigger, .mat-select-trigger")
        if trigger.count() > 0:
            trigger.first.click()
        else:
            cust_sel.click(force=True)

        self.page.wait_for_selector("mat-option", timeout=6_000)

        selected_text = ""
        if customer_name:
            target_opt = self.page.locator(f"mat-option:has-text('{customer_name}')").first
            if target_opt.is_visible(timeout=2_000):
                selected_text = target_opt.inner_text().strip()
                target_opt.click()
            else:
                first_opt = self.page.locator("mat-option").first
                selected_text = first_opt.inner_text().strip()
                first_opt.click()
        else:
            first_opt = self.page.locator("mat-option").first
            selected_text = first_opt.inner_text().strip()
            first_opt.click()

        try:
            self.page.wait_for_selector("mat-option", state="hidden", timeout=3_000)
        except Exception:
            self.page.keyboard.press("Escape")

        return selected_text

    def get_customer_options(self) -> List[str]:
        """Open customer dropdown, fetch all options, and close dropdown."""
        cust_sel = self.customer_select
        cust_sel.wait_for(state="visible", timeout=10_000)
        trigger = cust_sel.locator(".mat-mdc-select-trigger, .mat-select-trigger")
        if trigger.count() > 0:
            trigger.first.click()
        else:
            cust_sel.click(force=True)

        self.page.wait_for_selector("mat-option", timeout=6_000)
        options = [o.inner_text().strip() for o in self.page.locator("mat-option").all()]
        self.page.keyboard.press("Escape")
        try:
            self.page.wait_for_selector("mat-option", state="hidden", timeout=3_000)
        except Exception:
            pass
        return options

    def enter_po_date(self, date_str: str) -> None:
        """Set PO Date on the form."""
        inp = self.date_input
        inp.wait_for(state="visible", timeout=8_000)
        inp.evaluate(
            "(el, val) => { el.value = val; el.dispatchEvent(new Event('input', {bubbles: true})); el.dispatchEvent(new Event('change', {bubbles: true})); }",
            str(date_str),
        )

    def enter_ref_no(self, ref_no: str) -> None:
        """Set PO Reference No."""
        inp = self.ref_no_input
        inp.wait_for(state="visible", timeout=8_000)
        inp.fill(str(ref_no))
        inp.dispatch_event("input")
        inp.dispatch_event("change")

    def enter_authorized_by(self, name: str) -> None:
        """Set Authorized By."""
        inp = self.authorized_by_input
        inp.wait_for(state="visible", timeout=8_000)
        inp.fill(str(name))
        inp.dispatch_event("input")
        inp.dispatch_event("change")

    def enter_po_details(self, details: str) -> None:
        """Set PO Details."""
        inp = self.details_textarea
        inp.wait_for(state="visible", timeout=8_000)
        inp.fill(str(details))
        inp.dispatch_event("input")
        inp.dispatch_event("change")

    def enter_base_amount(self, amount: Any) -> None:
        """Set Base Amount."""
        inp = self.base_amount_input
        inp.wait_for(state="visible", timeout=8_000)
        inp.fill(str(amount))
        inp.dispatch_event("input")
        inp.dispatch_event("change")

    def enter_tax_amount(self, amount: Any) -> None:
        """Set Tax Amount."""
        inp = self.tax_amount_input
        inp.wait_for(state="visible", timeout=8_000)
        inp.fill(str(amount))
        inp.dispatch_event("input")
        inp.dispatch_event("change")

    def get_total_amount(self) -> str:
        """Read computed Total Amount from the field."""
        inp = self.total_amount_input
        inp.wait_for(state="visible", timeout=8_000)
        return inp.input_value().strip()

    def is_total_amount_readonly(self) -> bool:
        """Verify whether Total Amount is read-only or disabled."""
        inp = self.total_amount_input
        return inp.evaluate("e => e.readOnly || e.disabled || e.hasAttribute('readonly') || e.hasAttribute('disabled')")

    def select_currency(self, currency_code: str = "INR") -> None:
        """Select currency from dropdown."""
        curr_sel = self.currency_select
        curr_sel.wait_for(state="visible", timeout=8_000)
        trigger = curr_sel.locator(".mat-mdc-select-trigger, .mat-select-trigger")
        if trigger.count() > 0:
            trigger.first.click()
        else:
            curr_sel.click(force=True)

        self.page.wait_for_selector("mat-option", timeout=5_000)
        target_opt = self.page.locator(f"mat-option:has-text('{currency_code}')").first
        if target_opt.is_visible(timeout=2_000):
            target_opt.click()
        else:
            self.page.locator("mat-option").first.click()

        try:
            self.page.wait_for_selector("mat-option", state="hidden", timeout=3_000)
        except Exception:
            self.page.keyboard.press("Escape")

    def get_currency_options(self) -> List[str]:
        """Return available currency options."""
        curr_sel = self.currency_select
        curr_sel.wait_for(state="visible", timeout=8_000)
        trigger = curr_sel.locator(".mat-mdc-select-trigger, .mat-select-trigger")
        if trigger.count() > 0:
            trigger.first.click()
        else:
            curr_sel.click(force=True)

        self.page.wait_for_selector("mat-option", timeout=5_000)
        options = [o.inner_text().strip() for o in self.page.locator("mat-option").all()]
        self.page.keyboard.press("Escape")
        try:
            self.page.wait_for_selector("mat-option", state="hidden", timeout=3_000)
        except Exception:
            pass
        return options

    def select_status(self, status: str = "ACTIVE") -> None:
        """Select status from dropdown."""
        status_sel = self.status_select
        status_sel.wait_for(state="visible", timeout=8_000)
        trigger = status_sel.locator(".mat-mdc-select-trigger, .mat-select-trigger")
        if trigger.count() > 0:
            trigger.first.click()
        else:
            status_sel.click(force=True)

        self.page.wait_for_selector("mat-option", timeout=5_000)
        target_opt = self.page.locator(f"mat-option:has-text('{status}')").first
        if target_opt.is_visible(timeout=2_000):
            target_opt.click()
        else:
            self.page.locator("mat-option").first.click()

        try:
            self.page.wait_for_selector("mat-option", state="hidden", timeout=3_000)
        except Exception:
            self.page.keyboard.press("Escape")

    def get_status_options(self) -> List[str]:
        """Return available status options."""
        status_sel = self.status_select
        status_sel.wait_for(state="visible", timeout=8_000)
        trigger = status_sel.locator(".mat-mdc-select-trigger, .mat-select-trigger")
        if trigger.count() > 0:
            trigger.first.click()
        else:
            status_sel.click(force=True)

        self.page.wait_for_selector("mat-option", timeout=5_000)
        options = [o.inner_text().strip() for o in self.page.locator("mat-option").all()]
        self.page.keyboard.press("Escape")
        try:
            self.page.wait_for_selector("mat-option", state="hidden", timeout=3_000)
        except Exception:
            pass
        return options

    def upload_po_document(self, file_path: str) -> bool:
        """Upload a file to the hidden file input."""
        finp = self.file_input
        if finp.count() > 0 and os.path.exists(file_path):
            finp.set_input_files(file_path)
            return True
        return False

    def click_save(self) -> None:
        """Click Save/Add button to submit the form."""
        btn = self.add_button
        btn.wait_for(state="visible", timeout=8_000)
        btn.click()

    def click_cancel(self) -> None:
        """Click Cancel button in the modal."""
        btn = self.cancel_button
        if btn.is_visible(timeout=3_000):
            btn.click()
        else:
            self.click_close_icon()

        try:
            self.modal_container.wait_for(state="hidden", timeout=5_000)
        except Exception:
            self.page.keyboard.press("Escape")

    def click_close_icon(self) -> None:
        """Click top-right close 'X' icon."""
        close_btn = self.page.locator(".modal-card-header button, .modal-card-header mat-icon:has-text('close')").first
        try:
            if close_btn.is_visible(timeout=3_000):
                close_btn.click()
            else:
                self.page.keyboard.press("Escape")
        except Exception:
            self.page.keyboard.press("Escape")

        try:
            self.page.locator("mat-card.modal-card").first.wait_for(state="hidden", timeout=5_000)
        except Exception:
            self.page.keyboard.press("Escape")

    def get_snackbar_info(self, timeout_ms: int = 5_000) -> Dict[str, Any]:
        """Capture toast/snackbar message and status."""
        try:
            sb = self.page.locator("mat-snack-bar-container, .mat-mdc-snack-bar-container, .mat-simple-snackbar").first
            sb.wait_for(state="visible", timeout=timeout_ms)
            text = sb.inner_text().strip()
            cls = sb.get_attribute("class") or ""
            return {
                "visible": True,
                "text": text,
                "is_success": any(k in text.lower() for k in ["success", "created", "saved", "updated"]),
                "is_error": any(k in text.lower() for k in ["error", "please", "required", "already exists", "failed"]),
                "class": cls,
            }
        except Exception:
            return {"visible": False, "text": "", "is_success": False, "is_error": False, "class": ""}

    def search_purchase_order(self, query: str) -> int:
        """Search Purchase Order table by Ref No or Customer Name."""
        search_input = self.page.locator("input[placeholder*='Search' i], input[type='search']").first
        if search_input.is_visible(timeout=5_000):
            search_input.fill(str(query))
            search_input.dispatch_event("input")
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=3_000)
            except Exception:
                pass

        if not query:
            return self.page.locator("tbody tr").count()

        matching = [
            r for r in self.page.locator("tbody tr").all()
            if str(query).lower() in r.inner_text().lower()
        ]
        return len(matching)

    def get_grid_row_texts(self) -> List[str]:
        """Return text representation of all rows currently in the grid."""
        try:
            self.page.wait_for_selector("tbody tr", timeout=8_000)
            return [r.inner_text().strip() for r in self.page.locator("tbody tr").all()]
        except Exception:
            return []
