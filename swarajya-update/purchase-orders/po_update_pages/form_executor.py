"""Form Executor for Purchase Order Update positive and negative test suites."""

import os
import re
import pytest
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from po_update_pages.po_update_page import POUpdatePage
from shared.utils.logger import get_logger

log = get_logger("po_form_executor")

_MODULE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_PDF = os.path.join(_MODULE_ROOT, "test_data", "sample_po.pdf")


def _clean_val(val: str) -> str:
    """Strip quotes and surrounding whitespace from test data values."""
    s = str(val).strip()
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        s = s[1:-1].strip()
    return s


def _parse_key_values(text: str) -> dict:
    """Parse newline, comma, pipe, or semicolon separated Key: Value pairs from Excel test data."""
    if not text:
        return {}
    res = {}
    matches = re.findall(r"([^:,|\n]+)\s*:\s*([^,\n|]+)", str(text))
    if matches:
        for k, v in matches:
            res[k.strip()] = _clean_val(v)
    else:
        for line in str(text).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                res[k.strip()] = _clean_val(v)
    return res


class POUpdateFormExecutor:
    """Dispatches and executes data-driven purchase order update test scenarios."""

    def __init__(self, page: Page):
        self.page = page
        self.po_page = POUpdatePage(page)

    def prepare_po_edit(self, po_ref: str = "", row_index: int = 0) -> POUpdatePage:
        """Navigate to /purchaseOrder and open target PO edit form."""
        self.po_page.open_purchase_order_list(direct=True)
        self.po_page.open_po_edit_modal(po_ref=po_ref or None, row_index=row_index)
        return self.po_page

    def execute_positive_case(self, case: dict):
        """Execute a data-driven positive purchase order update scenario."""
        tc_id = str(case.get("Test Case ID", "")).strip()
        scenario = str(case.get("Scenario", "")).strip()
        raw_data = str(case.get("Test Data", "") or "")
        data = _parse_key_values(raw_data)

        log.info(f"Executing Positive PO Update Test [{tc_id}]: {scenario}")

        # TC_PO_POS_01: Verify Purchase Order Edit Form opens with pre-populated existing PO details
        if tc_id == "TC_PO_POS_01":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            assert self.po_page.is_update_form_visible(), (
                "Expected Result NOT met: Purchase Order update form modal is not visible."
            )
            try:
                po_date = self.po_page.get_form_field_value("po_date")
                ref_no = self.po_page.get_form_field_value("po_ref_no")
                cust_name = self.po_page.get_form_field_value("customer_name")
                status = self.po_page.get_form_field_value("status")

                assert len(po_date) > 0, "Expected Result NOT met: PO Date field is empty in edit modal."
                assert len(ref_no) > 0, "Expected Result NOT met: PO Reference No field is empty in edit modal."
                assert len(cust_name) > 0, "Expected Result NOT met: Customer Name field is empty in edit modal."
                assert len(status) > 0, "Expected Result NOT met: Status dropdown is empty in edit modal."
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_POS_02: Verify Customer Name is read-only / disabled and cannot be changed
        if tc_id == "TC_PO_POS_02":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                is_disabled = self.po_page.is_customer_name_readonly()
                assert is_disabled, (
                    "Expected Result NOT met: Customer Name should be strictly disabled/read-only in update form."
                )
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_POS_03: Verify PO Date field calendar toggle button opens datepicker calendar popup
        if tc_id == "TC_PO_POS_03":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                calendar_opened = self.po_page.open_calendar_picker()
                assert calendar_opened, (
                    "Expected Result NOT met: PO Date calendar toggle button failed to open calendar picker popup."
                )
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_POS_04: Verify Currency dropdown contains all specified options and permits selection
        if tc_id == "TC_PO_POS_04":
            expected_currencies = ["INR", "USD", "SAR", "EUR", "GBP", "NZD", "JYN"]
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                options = self.po_page.get_currency_options()
                missing = [c for c in expected_currencies if c not in options]
                assert not missing, (
                    f"Expected Result NOT met: Missing currency options: {missing}. Available: {options}"
                )
                self.po_page.select_currency("EUR")
                selected = self.po_page.get_form_field_value("currency")
                assert "EUR" in selected, (
                    f"Expected Result NOT met: Failed to select currency 'EUR'. Current value: '{selected}'"
                )
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_POS_05: Verify Status dropdown contains all specified options and permits selection
        if tc_id == "TC_PO_POS_05":
            expected_statuses = ["ACTIVE", "FULLY_USED", "PARTIALLY_USED", "CANCELLED"]
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                options = self.po_page.get_status_options()
                missing = [s for s in expected_statuses if s not in options]
                assert not missing, (
                    f"Expected Result NOT met: Missing status options: {missing}. Available: {options}"
                )
                self.po_page.select_status("ACTIVE")
                selected = self.po_page.get_form_field_value("status")
                assert "ACTIVE" in selected, (
                    f"Expected Result NOT met: Failed to select status 'ACTIVE'. Current value: '{selected}'"
                )
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_POS_06: Verify uploading a document via 'Choose File' attaches file and validates 'View Current Document'
        if tc_id == "TC_PO_POS_06":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                uploaded = self.po_page.upload_po_document(SAMPLE_PDF)
                assert uploaded, "Expected Result NOT met: File upload failed to target file input."

                doc_text = self.po_page.get_uploaded_document_text()
                assert "sample_po.pdf" in doc_text, (
                    f"Expected Result NOT met: Uploaded filename 'sample_po.pdf' not reflected. Found: '{doc_text}'"
                )

                doc_link = self.po_page.get_view_current_document_link()
                assert doc_link is not None, (
                    "Expected Result NOT met: 'View Current Document' link is not accessible after file selection."
                )
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_POS_07: Verify Cancel button dismisses edit form and returns to PO list without modifying record
        if tc_id == "TC_PO_POS_07":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.set_form_field("authorized_by", "Temporary Cancel Author")
            self.po_page.click_cancel()
            assert not self.po_page.is_update_form_visible(), (
                "Expected Result NOT met: Edit form modal did not close upon clicking Cancel."
            )
            return

        # TC_PO_POS_08: Verify successful update of Purchase Order with green snackbar notification
        if tc_id == "TC_PO_POS_08":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            po_details_val = data.get("PO Details", "test@1234")
            self.po_page.set_form_field("po_details", po_details_val)
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            assert snackbar["visible"], (
                "Expected Result NOT met: Expected snackbar notification did not appear after clicking Update."
            )
            assert snackbar["is_success"], (
                f"Expected Result NOT met: Expected green success snackbar. Class: '{snackbar['class']}', message: '{snackbar['text']}'"
            )
            assert "updated successfully" in snackbar["text"].lower(), (
                f"Expected Result NOT met: Unexpected success message: '{snackbar['text']}'"
            )
            return

        # TC_PO_POS_09: Verify searching PO by Reference Number or Customer Name in the list view
        if tc_id == "TC_PO_POS_09":
            self.po_page.open_purchase_order_list(direct=True)
            first_ref = self.po_page.get_first_row_po_ref()
            assert len(first_ref) > 0, (
                "Expected Result NOT met: No PO records found in listing table to perform search."
            )
            count = self.po_page.search_purchase_order(first_ref)
            assert count > 0, f"Expected Result NOT met: Search by Ref No '{first_ref}' yielded 0 rows."
            self.po_page.search_purchase_order("")
            return

        # TC_PO_POS_10: Verify 'Include Fully Used PO' checkbox filter toggles visibility of FULLY_USED records
        if tc_id == "TC_PO_POS_10":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.toggle_include_fully_used_po(check=True)
            statuses_with_cb = [
                td.inner_text().strip()
                for td in self.page.locator("tbody tr td:nth-child(7)").all()
            ]
            self.po_page.toggle_include_fully_used_po(check=False)
            assert "FULLY_USED" in statuses_with_cb, (
                "Expected Result NOT met: Checking 'Include Fully Used PO' should retrieve records with FULLY_USED status."
            )
            return

        # TC_PO_POS_11: Verify Status transition to PARTIALLY_USED reflects in listing table
        if tc_id == "TC_PO_POS_11":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.select_status("PARTIALLY_USED")
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            assert snackbar["is_success"], (
                "Expected Result NOT met: Success snackbar did not appear on updating status to PARTIALLY_USED."
            )
            try:
                self.page.wait_for_function(
                    "() => document.querySelector('tbody tr td:nth-child(7)')?.innerText.includes('PARTIALLY_USED')",
                    timeout=6000,
                )
            except Exception:
                self.page.wait_for_timeout(1500)

            row_status = self.po_page.get_row_status(0)
            assert "PARTIALLY_USED" in row_status, (
                f"Expected Result NOT met: Listing row status was not updated. Found: '{row_status}'"
            )
            # Restore to ACTIVE
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.select_status("ACTIVE")
            self.po_page.click_update()
            self.page.wait_for_timeout(1000)
            return

        # TC_PO_POS_12: Verify Status transition to CANCELLED reflects in listing table
        if tc_id == "TC_PO_POS_12":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.select_status("CANCELLED")
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            assert snackbar["is_success"], (
                "Expected Result NOT met: Success snackbar did not appear on updating status to CANCELLED."
            )
            try:
                self.page.wait_for_function(
                    "() => document.querySelector('tbody tr td:nth-child(7)')?.innerText.includes('CANCELLED')",
                    timeout=6000,
                )
            except Exception:
                self.page.wait_for_timeout(1500)

            row_status = self.po_page.get_row_status(0)
            assert "CANCELLED" in row_status, (
                f"Expected Result NOT met: Listing row status was not updated to CANCELLED. Found: '{row_status}'"
            )
            # Restore to ACTIVE
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.select_status("ACTIVE")
            self.po_page.click_update()
            self.page.wait_for_timeout(1000)
            return

        # TC_PO_POS_13: Verify Status transition to FULLY_USED and filter interplay
        if tc_id == "TC_PO_POS_13":
            self.po_page.open_purchase_order_list(direct=True)
            po_ref = self.po_page.get_first_row_po_ref()
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.select_status("FULLY_USED")
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            assert snackbar["is_success"], (
                "Expected Result NOT met: Success snackbar did not appear on updating status to FULLY_USED."
            )
            # Enable Include Fully Used PO to locate and restore
            self.po_page.toggle_include_fully_used_po(check=True)
            self.po_page.open_po_edit_modal(po_ref=po_ref)
            self.po_page.select_status("ACTIVE")
            self.po_page.click_update()
            self.page.wait_for_timeout(1000)
            self.po_page.toggle_include_fully_used_po(check=False)
            return

        # TC_PO_POS_14: Verify Currency update persists and reflects in listing table
        if tc_id == "TC_PO_POS_14":
            curr_code = data.get("Currency", "USD")
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.select_currency(curr_code)
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            assert snackbar["is_success"], (
                "Expected Result NOT met: Success snackbar did not appear on updating currency."
            )
            try:
                self.page.wait_for_function(
                    f"() => document.querySelector('tbody tr td:nth-child(5)')?.innerText.includes('{curr_code}')",
                    timeout=6000,
                )
            except Exception:
                self.page.wait_for_timeout(1500)

            row_curr = self.po_page.get_row_currency(0)
            assert curr_code in row_curr, (
                f"Expected Result NOT met: Listing table row did not reflect updated currency '{curr_code}'. Found: '{row_curr}'"
            )
            # Restore to INR
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.select_currency("INR")
            self.po_page.click_update()
            self.page.wait_for_timeout(1000)
            return

        # TC_PO_POS_15: Verify PO Reference Number modification persists and is searchable
        if tc_id == "TC_PO_POS_15":
            self.po_page.open_purchase_order_list(direct=True)
            orig_ref = self.po_page.get_first_row_po_ref()
            new_ref = f"{orig_ref}9" if len(orig_ref) < 15 else orig_ref[:-1]

            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.set_form_field("po_ref_no", new_ref)
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            assert snackbar["is_success"], (
                "Expected Result NOT met: Success snackbar did not appear on updating PO Reference No."
            )
            count = self.po_page.search_purchase_order(new_ref)
            assert count > 0, (
                f"Expected Result NOT met: Search by updated reference '{new_ref}' yielded no rows."
            )
            # Restore original ref
            self.po_page.open_po_edit_modal(po_ref=new_ref)
            self.po_page.set_form_field("po_ref_no", orig_ref)
            self.po_page.click_update()
            self.po_page.search_purchase_order("")
            return

        # TC_PO_POS_16: Verify Amount fields update and reflection in listing Total Amount
        if tc_id == "TC_PO_POS_16":
            base_raw = str(data.get("Base Amount", "2000"))
            total_raw = str(data.get("Total Amount", "2000"))
            base_m = re.search(r"\d+", base_raw)
            total_m = re.search(r"\d+", total_raw)
            base_amt = base_m.group(0) if base_m else "2000"
            total_amt = total_m.group(0) if total_m else base_amt

            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.set_form_field("base_amount", base_amt)
            self.po_page.set_form_field("total_amount", total_amt)
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            assert snackbar["is_success"], (
                "Expected Result NOT met: Success snackbar did not appear on updating amounts."
            )
            row_total = self.po_page.get_row_total_amount(0)
            assert str(total_amt) in row_total, (
                f"Expected Result NOT met: Total amount was not updated to {total_amt} in listing. Found: '{row_total}'"
            )
            return

        # TC_PO_POS_17: Verify Document replacement / re-upload updates attachment
        if tc_id == "TC_PO_POS_17":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                uploaded = self.po_page.upload_po_document(SAMPLE_PDF)
                assert uploaded, "Expected Result NOT met: File upload failed to target file input."

                doc_text = self.po_page.get_uploaded_document_text()
                assert "sample_po.pdf" in doc_text, (
                    f"Expected Result NOT met: Uploaded document not reflected. Found: '{doc_text}'"
                )
                link = self.po_page.get_view_current_document_link()
                assert link is not None, (
                    "Expected Result NOT met: View Current Document link should be accessible."
                )
            finally:
                self.po_page.click_cancel()
            return

        # Fallback generic positive case
        log.warning(f"No specific handler for positive test case {tc_id}, running generic update")
        self.po_page.open_purchase_order_list(direct=True)
        self.po_page.open_po_edit_modal(row_index=0)
        if data:
            self.po_page.fill_po_update_form(data)
        self.po_page.click_update()
        snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
        assert snackbar["is_success"], f"Generic positive update failed for {tc_id}: {snackbar['text']}"

    def execute_negative_case(self, case: dict):
        """Execute a data-driven negative purchase order update scenario."""
        tc_id = str(case.get("Test Case ID", "")).strip()
        scenario = str(case.get("Scenario", "")).strip()
        raw_data = str(case.get("Test Data", "") or "")
        data = _parse_key_values(raw_data)

        log.info(f"Executing Negative PO Update Test [{tc_id}]: {scenario}")

        # TC_PO_NEG_01: Verify updating PO with empty mandatory PO Details displays error snackbar
        if tc_id == "TC_PO_NEG_01":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                self.po_page.set_form_field("po_details", "")
                self.po_page.click_update()

                snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
                assert snackbar["visible"], (
                    "Expected Result NOT met: Validation snackbar did not appear for empty PO Details."
                )
                assert snackbar["is_error"], (
                    f"Expected Result NOT met: Expected error snackbar (class snackbar-error). Class: '{snackbar['class']}', text: '{snackbar['text']}'"
                )
                assert "please enter po details" in snackbar["text"].lower(), (
                    f"Expected Result NOT met: Unexpected error message. Expected 'Please Enter PO Details', found: '{snackbar['text']}'"
                )
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_NEG_02: Verify Customer Name field rejects manual alteration or selection change
        if tc_id == "TC_PO_NEG_02":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                cust_field = self.page.locator(
                    "mat-form-field:has-text('Customer Name') mat-select, mat-select[formcontrolname='poCustomer']"
                ).first

                is_disabled = cust_field.evaluate(
                    "e => e.hasAttribute('disabled') || e.getAttribute('aria-disabled') === 'true' || e.classList.contains('mat-mdc-select-disabled')"
                )
                assert is_disabled, (
                    "Expected Result NOT met: Customer Name dropdown should be disabled to prevent modifications."
                )

                cust_field.click(force=True)
                options = self.page.locator("mat-option")
                assert options.count() == 0, (
                    "Expected Result NOT met: Options panel unexpectedly opened for disabled Customer Name."
                )
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_NEG_03: Verify search with non-existent PO Ref No or Name yields no matching records
        if tc_id == "TC_PO_NEG_03":
            self.po_page.open_purchase_order_list(direct=True)
            query = data.get("Query", "NON_EXISTENT_PO_99999999")
            self.po_page.search_purchase_order(query)

            rows = self.page.locator("tbody tr").all()
            for r in rows:
                text = r.inner_text().strip()
                assert query not in text, (
                    f"Expected Result NOT met: Non-existent query '{query}' was unexpectedly found in table rows."
                )
            self.po_page.search_purchase_order("")
            return

        # TC_PO_NEG_04: Verify file input restricts upload of unauthorized file extensions
        if tc_id == "TC_PO_NEG_04":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                file_input = self.page.locator("input#po_document_url, input[type='file']").first
                accept_attr = file_input.get_attribute("accept") or ""

                for unauth_ext in [".exe", ".bat", ".sh", ".cmd", ".js"]:
                    assert unauth_ext not in accept_attr.lower(), (
                        f"Expected Result NOT met: Unauthorized extension '{unauth_ext}' found in file accept filter: '{accept_attr}'"
                    )

                for approved_ext in [".pdf", ".doc", ".docx"]:
                    assert approved_ext in accept_attr.lower(), (
                        f"Expected Result NOT met: Expected approved extension '{approved_ext}' missing from accept filter: '{accept_attr}'"
                    )
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_NEG_05: Verify canceling edit with dirty fields does not persist changes to the listing page
        if tc_id == "TC_PO_NEG_05":
            self.po_page.open_purchase_order_list(direct=True)
            orig_ref = self.po_page.get_first_row_po_ref()
            self.po_page.open_po_edit_modal(row_index=0)

            self.po_page.set_form_field("po_ref_no", "UNSAVED_99999")
            self.po_page.click_cancel()

            current_ref = self.po_page.get_first_row_po_ref()
            assert current_ref == orig_ref, (
                f"Expected Result NOT met: Cancelling edit modified listing data! Expected '{orig_ref}', found '{current_ref}'"
            )
            return

        # TC_PO_NEG_06: Verify modal close icon ('X') cleanly dismisses modal and discards uncommitted changes
        if tc_id == "TC_PO_NEG_06":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.set_form_field("authorized_by", "Unsaved Discard Test")
            self.po_page.click_close_icon()

            assert not self.po_page.is_update_form_visible(), (
                "Expected Result NOT met: Modal was expected to close on clicking close icon."
            )
            return

        # TC_PO_NEG_07: Verify clearing search query automatically restores full table records without page refresh
        if tc_id == "TC_PO_NEG_07":
            self.po_page.open_purchase_order_list(direct=True)
            self.page.wait_for_function("() => document.querySelectorAll('tbody tr').length >= 1", timeout=10000)
            self.page.wait_for_timeout(1000)

            initial_len = len(self.po_page.get_purchase_order_rows())
            assert initial_len >= 1, f"Pre-condition failed: Expected at least 1 row in table, found {initial_len}"

            first_ref = self.po_page.get_first_row_po_ref()
            if first_ref:
                self.po_page.search_purchase_order(first_ref)
                self.page.wait_for_timeout(1000)
                filtered_count = len(self.po_page.get_purchase_order_rows())
                assert filtered_count <= initial_len, (
                    "Expected Result NOT met: Table was not filtered down by search query."
                )

                self.po_page.search_purchase_order("")
                self.page.wait_for_timeout(1000)
                restored_count = len(self.po_page.get_purchase_order_rows())
                assert restored_count == initial_len, (
                    f"Expected Result NOT met: Clearing search did not restore full rows! Expected {initial_len}, found {restored_count}"
                )
            return

        # TC_PO_NEG_08: Verify mandatory field asterisk indicators are present only on required fields
        if tc_id == "TC_PO_NEG_08":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            try:
                for mand_field in ["Customer Name", "PO Details", "Status"]:
                    field_loc = self.page.locator(f"mat-form-field:has-text('{mand_field}')")
                    asterisk = field_loc.locator(".text-danger, span:has-text('*')")
                    assert asterisk.count() > 0, (
                        f"Expected Result NOT met: Mandatory field '{mand_field}' is missing required asterisk (*) indicator."
                    )

                for opt_field in ["Authorized By", "Base Amount", "Tax Amount"]:
                    field_loc = self.page.locator(f"mat-form-field:has-text('{opt_field}')")
                    asterisk = field_loc.locator(".text-danger")
                    assert asterisk.count() == 0, (
                        f"Expected Result NOT met: Optional field '{opt_field}' unexpectedly has mandatory indicator."
                    )
            finally:
                self.po_page.click_cancel()
            return

        # TC_PO_NEG_09: Verify application rejects duplicate PO Reference Number assignment matching an existing PO
        if tc_id == "TC_PO_NEG_09":
            self.po_page.open_purchase_order_list(direct=True)
            self.page.wait_for_selector("tbody tr", timeout=10000)
            rows = self.po_page.get_purchase_order_rows()
            if len(rows) < 2:
                pytest.skip("Requires at least 2 PO records in table to test duplicate reference collision")

            ref_orig = None
            ref_target = None
            for i in range(min(15, len(rows))):
                r = self.po_page.get_row_ref_no(i)
                if not r:
                    continue
                if ref_orig is None:
                    ref_orig = r
                elif r != ref_orig:
                    ref_target = r
                    break

            if not ref_orig or not ref_target:
                pytest.skip("Could not find two distinct PO reference numbers in table rows to test collision")

            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.set_form_field("po_ref_no", ref_target)
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            is_rejected = (
                snackbar["is_error"]
                or "duplicate" in snackbar["text"].lower()
                or "already exists" in snackbar["text"].lower()
                or "conflict" in snackbar["text"].lower()
            )

            # Rollback / restore original ref
            if self.po_page.is_update_form_visible():
                self.po_page.click_cancel()
            else:
                self.po_page.open_po_edit_modal(row_index=0)
                self.po_page.set_form_field("po_ref_no", ref_orig)
                self.po_page.click_update()
                self.page.wait_for_timeout(1000)

            assert is_rejected, (
                f"Data Integrity Defect: System accepted duplicate PO Reference No '{ref_target}' "
                f"which already belongs to another PO. Notification received: '{snackbar['text']}'"
            )
            return

        # TC_PO_NEG_10: Verify application validates financial calculation consistency when Total Amount does not equal Base + Tax
        if tc_id == "TC_PO_NEG_10":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)

            self.po_page.set_form_field("base_amount", "5000")
            self.po_page.set_form_field("tax_amount", "500")
            self.po_page.set_form_field("total_amount", "99999")
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            is_rejected = (
                snackbar["is_error"]
                or "mismatch" in snackbar["text"].lower()
                or "total amount" in snackbar["text"].lower()
                or "equal" in snackbar["text"].lower()
            )

            if self.po_page.is_update_form_visible():
                self.po_page.click_cancel()

            assert is_rejected, (
                "Financial Calculation Defect: System permitted saving contradictory amounts "
                "(Base: 5000 + Tax: 500 != Total: 99999) without mathematical validation."
            )
            return

        # TC_PO_NEG_11: Verify application restricts modifying critical financial amounts on CANCELLED Purchase Orders
        if tc_id == "TC_PO_NEG_11":
            self.po_page.open_purchase_order_list(direct=True)
            self.po_page.open_po_edit_modal(row_index=0)
            orig_status = self.po_page.get_form_field_value("status")
            self.po_page.select_status("CANCELLED")
            self.po_page.click_update()
            self.page.wait_for_timeout(1000)

            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.set_form_field("base_amount", "88888")
            self.po_page.set_form_field("total_amount", "88888")
            self.po_page.click_update()

            snackbar = self.po_page.get_snackbar_info(timeout_ms=5000)
            is_blocked = (
                snackbar["is_error"]
                or "cancelled" in snackbar["text"].lower()
                or "cannot be modified" in snackbar["text"].lower()
                or "read-only" in snackbar["text"].lower()
            )

            if self.po_page.is_update_form_visible():
                self.po_page.click_cancel()

            self.po_page.open_po_edit_modal(row_index=0)
            self.po_page.select_status(orig_status if orig_status else "ACTIVE")
            self.po_page.click_update()
            self.page.wait_for_timeout(1000)

            assert is_blocked, (
                "Lifecycle State Defect: System permitted modifying financial amounts on a CANCELLED "
                "Purchase Order without requiring reactivation."
            )
            return

        # Fallback generic negative case
        log.warning(f"No specific handler for negative test case {tc_id}")
        self.po_page.open_purchase_order_list(direct=True)
        self.po_page.open_po_edit_modal(row_index=0)
        try:
            if data:
                self.po_page.fill_po_update_form(data)
            self.po_page.click_update()
            sb = self.po_page.get_snackbar_info(timeout_ms=5000)
            assert sb["is_error"] or not sb["is_success"], f"Negative validation should have rejected for {tc_id}"
        finally:
            self.po_page.click_cancel()


# Alias for backward compatibility / multi-naming
FormExecutor = POUpdateFormExecutor
