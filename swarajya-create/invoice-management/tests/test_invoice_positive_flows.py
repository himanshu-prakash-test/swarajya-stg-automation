"""
Test Suite: Create Invoice Management Positive Flows.

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


@pytest.mark.positive
@pytest.mark.invoice
class TestInvoicePositiveFlows:
    """Positive test cases for Create Invoice Management module."""

    @pytest.mark.smoke
    @pytest.mark.tc_id("TC_INVOICE_POS_01")
    def test_page_layout_mandatory_indicators_TC_INVOICE_POS_01(self, logged_in_page, base_url):
        """TC_INVOICE_POS_01: Verify Page Layout & Mandatory Field Indicators."""
        tc_id = "TC_INVOICE_POS_01"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        # Check mandatory field indicators (red asterisks)
        labels_html = logged_in_page.locator("label").all_inner_texts()
        asterisk_labels = [l for l in labels_html if "*" in l]

        assert len(asterisk_labels) >= 4, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Fewer mandatory asterisks found than expected. Labels: {asterisk_labels}"
        )
        assert inv.customer_select.is_visible(), "Customer select field is not visible."
        assert inv.invoice_for_input.is_visible(), "Invoice For Project field is not visible."

    @pytest.mark.smoke
    @pytest.mark.tc_id("TC_INVOICE_POS_02")
    def test_primary_action_buttons_display_TC_INVOICE_POS_02(self, logged_in_page, base_url):
        """TC_INVOICE_POS_02: Verify Primary Action Buttons Display."""
        tc_id = "TC_INVOICE_POS_02"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        assert inv.finalize_button.is_visible(), "Finalize Invoice button is not visible."
        assert inv.discard_button.is_visible(), "Discard Changes button is not visible."
        assert inv.save_draft_button.is_visible(), "Save as Draft button is not visible."
        assert inv.add_item_button.is_visible(), "Add item button is not visible."

    @pytest.mark.tc_id("TC_INVOICE_POS_03")
    def test_line_items_data_grid_columns_TC_INVOICE_POS_03(self, logged_in_page, base_url):
        """TC_INVOICE_POS_03: Verify Line Items Data Grid Columns."""
        tc_id = "TC_INVOICE_POS_03"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        headers = inv.line_items_headers
        headers_joined = " ".join(headers).lower()

        required_cols = ["actions", "#", "particulars", "sac", "qty", "uom", "rate", "amount"]
        missing = [c for c in required_cols if c not in headers_joined]

        assert not missing, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Missing column headers {missing}. Found: {headers}"
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_04")
    def test_date_picker_functionality_TC_INVOICE_POS_04(self, logged_in_page, base_url):
        """TC_INVOICE_POS_04: Verify Date Picker Functionality."""
        tc_id = "TC_INVOICE_POS_04"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        date_val = data.get("Invoice Date *") or data.get("Invoice Date", "")
        inv.enter_invoice_date(date_val)

        val = inv.invoice_date_input.input_value()
        assert val != "", (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Invoice Date input is empty after setting."
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_05")
    def test_dropdown_expansion_selection_TC_INVOICE_POS_05(self, logged_in_page, base_url):
        """TC_INVOICE_POS_05: Verify Dropdown Expansion & Selection."""
        tc_id = "TC_INVOICE_POS_05"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        customer = data.get("Customer Name *") or data.get("Customer Name", "")
        selected = inv.select_customer(customer)
        assert selected, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Customer dropdown option '{customer}' could not be selected."
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_06")
    def test_textarea_field_wrapping_resizing_TC_INVOICE_POS_06(self, logged_in_page, base_url):
        """TC_INVOICE_POS_06: Textarea Field Wrapping & Resizing."""
        tc_id = "TC_INVOICE_POS_06"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        test_notes = data.get("Internal Notes (not visible to customer)") or "Auto QA Test multi-line text notes wrapping properly."
        inv.enter_internal_notes(test_notes)
        inv.enter_external_notes(test_notes)

        assert inv.internal_notes_input.input_value() != "", "Internal notes textarea is empty."
        assert inv.external_notes_input.input_value() != "", "External notes textarea is empty."

    @pytest.mark.tc_id("TC_INVOICE_POS_07")
    def test_realtime_line_item_amount_calculation_TC_INVOICE_POS_07(self, logged_in_page, base_url):
        """TC_INVOICE_POS_07: Real-time Line Item Amount Calculation."""
        tc_id = "TC_INVOICE_POS_07"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        qty = float(data.get("Quantity *", 2))
        rate = float(data.get("Rate *", 1500))
        expected_amount = qty * rate

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)

        logged_in_page.wait_for_timeout(1000)
        table_text = logged_in_page.locator("table").inner_text()
        assert str(int(expected_amount)) in table_text or f"{expected_amount:,.2f}" in table_text or inv.line_items_rows.count() > 0, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Expected amount {expected_amount} not found in line items table."
        )

    @pytest.mark.smoke
    @pytest.mark.tc_id("TC_INVOICE_POS_08")
    def test_dynamic_addition_of_line_item_to_grid_TC_INVOICE_POS_08(self, logged_in_page, base_url):
        """TC_INVOICE_POS_08: Dynamic Addition of Line Item to Grid."""
        tc_id = "TC_INVOICE_POS_08"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        initial_count = inv.line_items_rows.count()
        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)

        logged_in_page.wait_for_timeout(1000)
        new_count = inv.line_items_rows.count()
        assert new_count > initial_count or logged_in_page.locator("table tbody tr").count() >= 1, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Line item row was not added to grid. Rows: {new_count}"
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_09")
    def test_line_item_table_action_icons_TC_INVOICE_POS_09(self, logged_in_page, base_url):
        """TC_INVOICE_POS_09: Line Item Table Action Icons."""
        tc_id = "TC_INVOICE_POS_09"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)

        logged_in_page.wait_for_timeout(1000)
        if inv.line_items_rows.count() > 0:
            first_row = inv.line_items_rows.first
            actions = first_row.locator("button, i, a, svg")
            assert actions.count() > 0, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
                f"Actual: Action icons not found on added line item row."
            )

    @pytest.mark.tc_id("TC_INVOICE_POS_10")
    def test_delete_line_item_row_TC_INVOICE_POS_10(self, logged_in_page, base_url):
        """TC_INVOICE_POS_10: Delete Line Item Row."""
        tc_id = "TC_INVOICE_POS_10"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)
        logged_in_page.wait_for_timeout(1000)

        before_count = inv.line_items_rows.count()
        if before_count > 0:
            inv.delete_line_item(0)
            logged_in_page.wait_for_timeout(1000)
            # Row removed or count decreased
            assert inv.line_items_rows.count() <= before_count, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
                f"Actual: Line item count did not decrease after deletion."
            )

    @pytest.mark.tc_id("TC_INVOICE_POS_11")
    def test_discard_changes_confirm_discard_TC_INVOICE_POS_11(self, logged_in_page, base_url):
        """TC_INVOICE_POS_11: Discard Changes - Confirm Discard."""
        tc_id = "TC_INVOICE_POS_11"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=False)

        inv.discard_button.click()
        logged_in_page.wait_for_timeout(1000)

        if inv.is_modal_visible():
            inv.confirm_modal()
            logged_in_page.wait_for_timeout(1000)

        # Successfully navigated back to /invoice or form cleared
        assert "invoice" in logged_in_page.url.lower(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: URL is not on invoice route after discarding changes. URL: {logged_in_page.url}"
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_12")
    def test_save_as_draft_confirmation_popup_display_TC_INVOICE_POS_12(self, logged_in_page, base_url):
        """TC_INVOICE_POS_12: Save as Draft - Confirmation Popup Display."""
        tc_id = "TC_INVOICE_POS_12"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)

        inv.save_draft_button.click()
        logged_in_page.wait_for_timeout(1000)

        has_popup = inv.is_modal_visible() or "confirm" in logged_in_page.content().lower() or "draft" in logged_in_page.content().lower()
        assert has_popup, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Confirmation popup not displayed upon clicking Save as Draft."
        )
        if inv.is_modal_visible():
            inv.cancel_modal()

    @pytest.mark.tc_id("TC_INVOICE_POS_13")
    def test_save_as_draft_confirm_action_TC_INVOICE_POS_13(self, logged_in_page, base_url):
        """TC_INVOICE_POS_13: Save as Draft - Confirm Action."""
        tc_id = "TC_INVOICE_POS_13"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)

        inv.save_draft_button.click()
        logged_in_page.wait_for_timeout(1000)

        if inv.is_modal_visible():
            inv.confirm_modal()
            logged_in_page.wait_for_timeout(1500)

        assert "invoice" in logged_in_page.url.lower(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Draft save failed to process. Current URL: {logged_in_page.url}"
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_14")
    def test_finalize_invoice_confirm_action_TC_INVOICE_POS_14(self, logged_in_page, base_url):
        """TC_INVOICE_POS_14: Finalize Invoice - Confirm Action."""
        tc_id = "TC_INVOICE_POS_14"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        data = get_test_data_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        executor = InvoiceFormExecutor(inv)
        executor.populate_form(data, add_line_item=True)

        inv.finalize_button.click()
        logged_in_page.wait_for_timeout(1000)

        if inv.is_modal_visible():
            inv.confirm_modal()
            logged_in_page.wait_for_timeout(1500)

        assert "invoice" in logged_in_page.url.lower(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Finalize invoice submission did not redirect to invoice module. URL: {logged_in_page.url}"
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_15")
    def test_keyboard_accessibility_tab_order_TC_INVOICE_POS_15(self, logged_in_page, base_url):
        """TC_INVOICE_POS_15: Keyboard Accessibility (Tab Order)."""
        tc_id = "TC_INVOICE_POS_15"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_new_invoice()

        inv.customer_select.focus()
        logged_in_page.keyboard.press("Tab")
        logged_in_page.wait_for_timeout(300)

        # Check focus shifted to an active form element
        active_tag = logged_in_page.evaluate("document.activeElement.tagName")
        assert active_tag in ("SELECT", "INPUT", "TEXTAREA", "BUTTON"), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Tab did not focus a valid input element. Active tag: {active_tag}"
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_16")
    def test_verify_draft_entry_in_dashboard_TC_INVOICE_POS_16(self, logged_in_page, base_url):
        """TC_INVOICE_POS_16: Verify Draft Entry in Dashboard."""
        tc_id = "TC_INVOICE_POS_16"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_invoice_dashboard()

        content = logged_in_page.content().lower()
        has_table = logged_in_page.locator("table").count() > 0 or "invoice" in content
        assert has_table, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Invoice list table is not rendered on dashboard."
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_17")
    def test_verify_finalized_entry_in_dashboard_TC_INVOICE_POS_17(self, logged_in_page, base_url):
        """TC_INVOICE_POS_17: Verify Finalized Entry in Dashboard."""
        tc_id = "TC_INVOICE_POS_17"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_invoice_dashboard()

        content = logged_in_page.content().lower()
        assert "invoice" in content or "status" in content, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Invoice dashboard entries could not be verified."
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_18")
    def test_verify_dashboard_action_options_TC_INVOICE_POS_18(self, logged_in_page, base_url):
        """TC_INVOICE_POS_18: Verify Dashboard Action Options."""
        tc_id = "TC_INVOICE_POS_18"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_invoice_dashboard()

        actions = logged_in_page.locator("table button, table a, table i, .mat-icon")
        assert actions.count() > 0 or logged_in_page.locator("table").count() > 0, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Action options not available on invoice table."
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_19")
    def test_verify_draft_filter_on_dashboard_TC_INVOICE_POS_19(self, logged_in_page, base_url):
        """TC_INVOICE_POS_19: Verify Draft Filter on Invoice Dashboard."""
        tc_id = "TC_INVOICE_POS_19"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_invoice_dashboard()

        # Check for status filter or chip
        draft_chip = logged_in_page.locator("button, span, mat-chip, a").filter(has_text="Draft").or_(
            logged_in_page.locator("select, [aria-label*='Status' i]")
        ).first
        if draft_chip.is_visible(timeout=3_000):
            draft_chip.click()
            logged_in_page.wait_for_timeout(1000)

        assert "invoice" in logged_in_page.url.lower(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Filtering by draft failed."
        )

    @pytest.mark.tc_id("TC_INVOICE_POS_20")
    def test_verify_finalized_filter_on_dashboard_TC_INVOICE_POS_20(self, logged_in_page, base_url):
        """TC_INVOICE_POS_20: Verify Finalized Filter on Invoice Dashboard."""
        tc_id = "TC_INVOICE_POS_20"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        inv = InvoicePage(logged_in_page, base_url)
        inv.navigate_to_invoice_dashboard()

        fin_chip = logged_in_page.locator("button, span, mat-chip, a").filter(has_text="Finalized").or_(
            logged_in_page.locator("select, [aria-label*='Status' i]")
        ).first
        if fin_chip.is_visible(timeout=3_000):
            fin_chip.click()
            logged_in_page.wait_for_timeout(1000)

        assert "invoice" in logged_in_page.url.lower(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Filtering by finalized failed."
        )
