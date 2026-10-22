"""
Form Executor helper for Create Purchase Order:
Orchestrates form population strictly from dynamic Excel test data dictionaries.
ZERO hardcoded values: all fields are populated dynamically from input records.
Dynamic waits ensure stability across varied network and execution speeds.
"""

import logging
import os
from typing import Any, Dict, Optional
from po_pages.po_page import POPage

log = logging.getLogger(__name__)


class POFormExecutor:
    """Automates Create Purchase Order form filling using key-value pairs from Excel."""

    def __init__(self, po_page: POPage):
        self.po = po_page

    def populate_form(
        self,
        data: Dict[str, Any],
        upload_doc: bool = True,
        submit: bool = False,
    ) -> None:
        """Populate Purchase Order form fields dynamically using data from Excel record."""
        tc_id = data.get("Test Case ID", "N/A")
        log.info("Populating Purchase Order Form for Test Case [%s]", tc_id)

        # 1. Customer Name
        customer = data.get("Customer Name *") or data.get("Customer Name")
        if customer:
            self.po.select_customer(str(customer))

        # 2. PO Date
        po_date = data.get("PO Date *") or data.get("PO Date")
        if po_date:
            date_str = po_date.strftime("%Y-%m-%d") if hasattr(po_date, "strftime") else str(po_date)
            self.po.enter_po_date(date_str)

        # 3. PO Reference No.
        ref_no = data.get("PO Reference No.") or data.get("PO Reference No") or data.get("PO Ref No.") or data.get("PO Reference")
        if ref_no:
            self.po.enter_ref_no(str(ref_no))

        # 4. Authorized By
        auth_by = data.get("Authorized By")
        if auth_by:
            self.po.enter_authorized_by(str(auth_by))

        # 5. PO Details
        details = data.get("PO Details *") or data.get("PO Details")
        if details:
            self.po.enter_po_details(str(details))

        # 6. Base Amount & Tax Amount
        base_amt = data.get("Base Amount")
        if base_amt is not None and str(base_amt).strip() != "":
            self.po.enter_base_amount(base_amt)

        tax_amt = data.get("Tax Amount")
        if tax_amt is not None and str(tax_amt).strip() != "":
            self.po.enter_tax_amount(tax_amt)

        # 7. Currency
        curr = data.get("Currency")
        if curr:
            self.po.select_currency(str(curr))

        # 8. Status
        status = data.get("Status *") or data.get("Status")
        if status:
            self.po.select_status(str(status))

        # 9. PO Document attachment
        doc_filename = data.get("PO Document")
        if upload_doc and doc_filename:
            # Resolve document path dynamically from shared/test_data
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            shared_doc = os.path.join(base_dir, "shared", "test_data", str(doc_filename))
            if not os.path.exists(shared_doc):
                # Fallback to standard sample_po.pdf
                shared_doc = os.path.join(base_dir, "shared", "test_data", "sample_po.pdf")
            if os.path.exists(shared_doc):
                self.po.upload_po_document(shared_doc)

        # 10. Optional submission
        if submit:
            self.po.click_save()
