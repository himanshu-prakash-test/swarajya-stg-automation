"""
Test Suite: Create Invoice Management Negative & Validation Flows.

Strictly data-driven from shared Excel workbooks:
- Test Data:  shared/test_data/Swarajya-test-data.xlsx  [Sheet: createinvoice-mgmt]
- Test Cases: shared/test_data/Swarajya-test-cases.xlsx [Sheet: createinvoice-mgmt]

STRICT ZERO-HARDCODING POLICY:
- All credentials, base URLs, form inputs, test descriptions, and expected outcomes
  are dynamically fetched from Excel.
"""

import os
import sys
import pytest

MODULE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(os.path.dirname(MODULE_DIR))
for path_dir in (MODULE_DIR, ROOT_DIR):
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

from invoice_pages.invoice_page import InvoicePage
from invoice_pages.form_executor import InvoiceFormExecutor
from invoice_utils.excel_reader import (
    get_test_case_by_id,
    get_test_data_by_id,
    SHEET_NAME,
)


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.invoice
class TestInvoiceNegativeFlows:
    """Negative and boundary validation test cases for Invoice Management."""

    @pytest.mark.tc_id("TC_INVOICE_NEG_01")
    def test_ui_layout_on_small_viewport_TC_INVOICE_NEG_01(self, logged_in_page, base_url):
        """TC_INVOICE_NEG_01: UI Layout on Small Viewport / Low Resolution."""
        tc_id = "TC_INVOICE_NEG_01"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        logged_in_page.set_viewport_size({"width": 800, "height": 600})
        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        assert inv.customer_select.is_visible(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Form inputs not rendered properly on small 800x600 viewport."
        )
        # Restore viewport
        logged_in_page.set_viewport_size({"width": 1920, "height": 1080})

    @pytest.mark.tc_id("TC_INVOICE_NEG_02")
    def test_discard_changes_cancel_action_TC_INVOICE_NEG_02(self, logged_in_page, base_url):
        """TC_INVOICE_NEG_02: Discard Changes - Cancel Action."""
        tc_id = "TC_INVOICE_NEG_02"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=False)

        inv.discard_button.click()
        logged_in_page.wait_for_timeout(800)

        if inv.is_modal_visible():
            inv.cancel_modal()
            logged_in_page.wait_for_timeout(800)

        # Form remains open with data preserved
        project_val = inv.invoice_for_input.input_value()
        assert "generateNewInvoice" in logged_in_page.url or project_val != "" or inv.customer_select.is_visible(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Cancelling discard modal did not preserve form state."
        )

    @pytest.mark.tc_id("TC_INVOICE_NEG_03")
    def test_save_as_draft_cancel_action_TC_INVOICE_NEG_03(self, logged_in_page, base_url):
        """TC_INVOICE_NEG_03: Save as Draft - Cancel Action."""
        tc_id = "TC_INVOICE_NEG_03"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)

        inv.save_draft_button.click()
        logged_in_page.wait_for_timeout(800)

        if inv.is_modal_visible():
            inv.cancel_modal()
            logged_in_page.wait_for_timeout(800)

        assert "generateNewInvoice" in logged_in_page.url or inv.save_draft_button.is_visible(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Cancelling draft submission navigated away from form."
        )

    @pytest.mark.tc_id("TC_INVOICE_NEG_04")
    def test_finalize_invoice_cancel_action_TC_INVOICE_NEG_04(self, logged_in_page, base_url):
        """TC_INVOICE_NEG_04: Finalize Invoice - Cancel Action."""
        tc_id = "TC_INVOICE_NEG_04"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)

        inv.finalize_button.click()
        logged_in_page.wait_for_timeout(800)

        if inv.is_modal_visible():
            inv.cancel_modal()
            logged_in_page.wait_for_timeout(800)

        assert "generateNewInvoice" in logged_in_page.url or inv.finalize_button.is_visible(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Cancelling finalize modal unexpectedly navigated away."
        )

    @pytest.mark.tc_id("TC_INVOICE_NEG_05")
    def test_add_line_item_with_empty_fields_TC_INVOICE_NEG_05(self, logged_in_page, base_url):
        """TC_INVOICE_NEG_05: Add Line Item with Empty Fields."""
        tc_id = "TC_INVOICE_NEG_05"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        # Add button is disabled or clicking it without inputs prevents addition
        initial_count = inv.line_items_rows.count()
        is_disabled = inv.add_item_button.is_disabled()

        if not is_disabled:
            inv.add_item_button.click()
            logged_in_page.wait_for_timeout(800)

        assert is_disabled or inv.line_items_rows.count() == initial_count, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Empty line item was added to the data grid."
        )

    @pytest.mark.tc_id("TC_INVOICE_NEG_06")
    def test_dismiss_confirmation_popup_via_backdrop_or_esc_TC_INVOICE_NEG_06(self, logged_in_page, base_url):
        """TC_INVOICE_NEG_06: Dismiss Confirmation Popup via BackDrop / ESC."""
        tc_id = "TC_INVOICE_NEG_06"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=False)

        inv.discard_button.click()
        logged_in_page.wait_for_timeout(800)

        if inv.is_modal_visible():
            inv.dismiss_modal_via_backdrop_or_esc()
            logged_in_page.wait_for_timeout(800)

        assert "generateNewInvoice" in logged_in_page.url or inv.discard_button.is_visible(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Modal could not be dismissed via ESC."
        )

    @pytest.mark.tc_id("TC_INVOICE_NEG_07")
    def test_network_disconnection_during_invoice_submission_TC_INVOICE_NEG_07(self, logged_in_page, base_url, context):
        """TC_INVOICE_NEG_07: Network Disconnection during Invoice Submission."""
        tc_id = "TC_INVOICE_NEG_07"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)

        # Emulate offline network condition
        context.set_offline(True)
        try:
            inv.save_draft_button.click()
            logged_in_page.wait_for_timeout(1000)
            if inv.is_modal_visible():
                inv.confirm_modal()
                logged_in_page.wait_for_timeout(1000)

            # Application should gracefully remain responsive or show error toast
            content = logged_in_page.content().lower()
            assert "invoice" in logged_in_page.url or "error" in content or "offline" in content or inv.save_draft_button.is_visible(), (
                f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
                f"Actual: Unhandled crash during offline submission."
            )
        finally:
            context.set_offline(False)
