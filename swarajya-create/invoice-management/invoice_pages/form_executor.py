"""
Form Executor helper for Create Invoice Management:
Orchestrates form population strictly from dynamic Excel test data dictionaries.
"""

import logging
from typing import Dict, Any, Optional
from invoice_pages.invoice_page import InvoicePage

log = logging.getLogger(__name__)


class InvoiceFormExecutor:
    """Automates form filling using key-value pairs from Excel test data."""

    def __init__(self, invoice_page: InvoicePage):
        self.inv = invoice_page

    def populate_form(self, data: Dict[str, Any], add_line_item: bool = True) -> None:
        """Populate header fields and line item fields from Excel record."""
        log.info("Populating Invoice Form for Test Case [%s]", data.get("Test Case ID"))

        # Customer Name
        customer = data.get("Customer Name *") or data.get("Customer Name")
        if customer:
            self.inv.select_customer(str(customer))

        # Project
        project = data.get("Invoice For Project *") or data.get("Invoice For Project")
        if project:
            self.inv.enter_project(str(project))

        # Invoice Date & Due Date
        inv_date = data.get("Invoice Date *") or data.get("Invoice Date")
        if inv_date:
            self.inv.enter_invoice_date(str(inv_date))

        due_date = data.get("Due Date *") or data.get("Due Date")
        if due_date:
            self.inv.enter_due_date(str(due_date))

        # Notes
        internal_notes = data.get("Internal Notes (not visible to customer)")
        if internal_notes:
            self.inv.enter_internal_notes(str(internal_notes))

        external_notes = data.get("External Notes (Added on Invoice)")
        if external_notes:
            self.inv.enter_external_notes(str(external_notes))

        # Line Item
        particulars = data.get("Particulars/Description of Services *") or data.get("Particulars")
        sac = data.get("SAC *") or data.get("SAC", "")
        qty = data.get("Quantity *") or data.get("Quantity", "1")
        uom = data.get("UOM *") or data.get("UOM", "Hours")
        rate = data.get("Rate *") or data.get("Rate", "1000")

        if particulars:
            self.inv.fill_line_item(
                particulars=str(particulars),
                sac=str(sac) if sac else "",
                quantity=str(qty),
                uom=str(uom),
                rate=str(rate),
            )
            if add_line_item:
                self.inv.click_add_item()
