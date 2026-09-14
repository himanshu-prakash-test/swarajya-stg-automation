"""Comprehensive Positive and Negative automated test scenarios for Purchase Order Update."""

import os
import pytest
from po_update_pages.po_update_page import POUpdatePage
from po_update_utils.excel_reader import update_test_result

SAMPLE_PDF = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "test_data",
    "sample_po.pdf",
)


@pytest.mark.purchase_order
@pytest.mark.po_update
class TestPurchaseOrderUpdatePositiveFlows:
    """Positive test scenarios for Purchase Order Update workflow."""

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_01")
    def test_po_edit_modal_populated(self, authenticated_page):
        """Verify Purchase Order Edit Form opens with pre-populated existing PO details."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        assert po_page.is_update_form_visible(), "Purchase Order update form modal is not visible."

        # Verify key pre-populated fields
        po_date = po_page.get_form_field_value("po_date")
        ref_no = po_page.get_form_field_value("po_ref_no")
        cust_name = po_page.get_form_field_value("customer_name")
        status = po_page.get_form_field_value("status")

        assert len(po_date) > 0, "PO Date field is unexpectedly empty in edit modal."
        assert len(ref_no) > 0, "PO Reference No field is unexpectedly empty in edit modal."
        assert len(cust_name) > 0, "Customer Name field is unexpectedly empty in edit modal."
        assert len(status) > 0, "Status dropdown is unexpectedly empty in edit modal."

        po_page.click_cancel()
        update_test_result("TC_PO_POS_01", "Passed", "Edit modal opens with pre-populated data")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_02")
    def test_po_customer_name_immutable(self, authenticated_page):
        """Verify Customer Name field is read-only / disabled and cannot be changed."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        is_disabled = po_page.is_customer_name_readonly()
        assert is_disabled, "Customer Name should be strictly disabled/read-only in update form."

        po_page.click_cancel()
        update_test_result("TC_PO_POS_02", "Passed", "Customer Name is disabled/read-only")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_03")
    def test_po_date_calendar_picker(self, authenticated_page):
        """Verify PO Date field calendar toggle button opens datepicker calendar popup."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        calendar_opened = po_page.open_calendar_picker()
        assert calendar_opened, "PO Date calendar toggle button failed to open the calendar picker popup."

        po_page.click_cancel()
        update_test_result("TC_PO_POS_03", "Passed", "Calendar picker toggle and popup verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_04")
    def test_po_currency_dropdown_options(self, authenticated_page):
        """Verify Currency dropdown contains all specified options and permits selection."""
        expected_currencies = ["INR", "USD", "SAR", "EUR", "GBP", "NZD", "JYN"]
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        options = po_page.get_currency_options()
        for curr in expected_currencies:
            assert curr in options, f"Expected currency '{curr}' was not found in options: {options}"

        # Test selecting EUR
        po_page.select_currency("EUR")
        selected = po_page.get_form_field_value("currency")
        assert "EUR" in selected, f"Failed to select currency 'EUR'. Current value: '{selected}'"

        po_page.click_cancel()
        update_test_result("TC_PO_POS_04", "Passed", "All specified currencies present and selectable")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_05")
    def test_po_status_dropdown_options(self, authenticated_page):
        """Verify Status dropdown contains all specified options and permits selection."""
        expected_statuses = ["ACTIVE", "FULLY_USED", "PARTIALLY_USED", "CANCELLED"]
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        options = po_page.get_status_options()
        for st in expected_statuses:
            assert st in options, f"Expected status '{st}' was not found in options: {options}"

        # Test selecting ACTIVE
        po_page.select_status("ACTIVE")
        selected = po_page.get_form_field_value("status")
        assert "ACTIVE" in selected, f"Failed to select status 'ACTIVE'. Current value: '{selected}'"

        po_page.click_cancel()
        update_test_result("TC_PO_POS_05", "Passed", "All 4 lifecycle status options verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_06")
    def test_po_document_file_upload_and_view(self, authenticated_page):
        """Verify uploading a document via 'Choose File' attaches file and validates 'View Current Document'."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        uploaded = po_page.upload_po_document(SAMPLE_PDF)
        assert uploaded, "File upload failed to target the file input."

        doc_text = po_page.get_uploaded_document_text()
        assert "sample_po.pdf" in doc_text, f"Uploaded filename 'sample_po.pdf' not reflected. Found: '{doc_text}'"

        doc_link = po_page.get_view_current_document_link()
        assert doc_link is not None, "'View Current Document' link is not accessible after file selection."

        po_page.click_cancel()
        update_test_result("TC_PO_POS_06", "Passed", "File upload and View Current Document link verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_07")
    def test_po_cancel_button_retracts(self, authenticated_page):
        """Verify Cancel button dismisses edit form and returns to PO list without modifying record."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        po_page.set_form_field("authorized_by", "Temporary Cancel Author")
        po_page.click_cancel()

        assert not po_page.is_update_form_visible(), "Edit form modal did not close upon clicking Cancel."
        update_test_result("TC_PO_POS_07", "Passed", "Cancel button retraction verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_08")
    def test_po_valid_update_green_snackbar(self, authenticated_page):
        """Verify successful update of Purchase Order with green snackbar notification."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        # Ensure valid mandatory details
        po_page.set_form_field("po_details", "test@1234")
        po_page.click_update()

        snackbar = po_page.get_snackbar_info(timeout_ms=5000)
        assert snackbar["visible"], "Expected snackbar did not appear after clicking Update."
        assert snackbar["is_success"], (
            f"Expected green success snackbar (class snackbar-success). "
            f"Actual class: '{snackbar['class']}', message: '{snackbar['text']}'"
        )
        assert "Purchase Order Updated Successfully" in snackbar["text"], (
            f"Unexpected success message: '{snackbar['text']}'"
        )
        update_test_result("TC_PO_POS_08", "Passed", "Green success snackbar verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_09")
    def test_po_list_search_by_id_or_name(self, authenticated_page):
        """Verify searching PO by Reference Number or Customer Name in the list view."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)

        first_ref = po_page.get_first_row_po_ref()
        assert len(first_ref) > 0, "No PO records found in listing table to test search."

        # Search for that exact PO reference
        count = po_page.search_purchase_order(first_ref)
        assert count > 0, f"Search by Ref No '{first_ref}' yielded 0 rows."

        # Clear search
        po_page.search_purchase_order("")
        update_test_result("TC_PO_POS_09", "Passed", "Search by Ref No verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_10")
    def test_po_include_fully_used_checkbox_filter(self, authenticated_page):
        """Verify 'Include Fully Used PO' checkbox filter toggles visibility of FULLY_USED records."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)

        # Toggle on
        po_page.toggle_include_fully_used_po(check=True)
        statuses_with_cb = [
            td.inner_text().strip()
            for td in authenticated_page.locator("tbody tr td:nth-child(7)").all()
        ]

        # Toggle off
        po_page.toggle_include_fully_used_po(check=False)

        assert "FULLY_USED" in statuses_with_cb, (
            "Checking 'Include Fully Used PO' should retrieve records with FULLY_USED status."
        )
        update_test_result("TC_PO_POS_10", "Passed", "Include Fully Used PO filter verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_11")
    def test_po_status_transition_partially_used(self, authenticated_page):
        """Verify Status transition to PARTIALLY_USED reflects in listing table."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        po_page.select_status("PARTIALLY_USED")
        po_page.click_update()

        snackbar = po_page.get_snackbar_info(timeout_ms=5000)
        assert snackbar["is_success"], "Success snackbar did not appear on updating status to PARTIALLY_USED."

        try:
            authenticated_page.wait_for_function(
                "() => document.querySelector('tbody tr td:nth-child(7)')?.innerText.includes('PARTIALLY_USED')",
                timeout=6000,
            )
        except Exception:
            authenticated_page.wait_for_timeout(1500)

        row_status = po_page.get_row_status(0)
        assert "PARTIALLY_USED" in row_status, f"Listing row status was not updated. Found: '{row_status}'"

        # Restore to ACTIVE
        po_page.open_po_edit_modal(row_index=0)
        po_page.select_status("ACTIVE")
        po_page.click_update()
        authenticated_page.wait_for_timeout(1000)
        update_test_result("TC_PO_POS_11", "Passed", "Status transition to PARTIALLY_USED verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_12")
    def test_po_status_transition_cancelled(self, authenticated_page):
        """Verify Status transition to CANCELLED reflects in listing table."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        po_page.select_status("CANCELLED")
        po_page.click_update()

        snackbar = po_page.get_snackbar_info(timeout_ms=5000)
        assert snackbar["is_success"], "Success snackbar did not appear on updating status to CANCELLED."

        try:
            authenticated_page.wait_for_function(
                "() => document.querySelector('tbody tr td:nth-child(7)')?.innerText.includes('CANCELLED')",
                timeout=6000,
            )
        except Exception:
            authenticated_page.wait_for_timeout(1500)

        row_status = po_page.get_row_status(0)
        assert "CANCELLED" in row_status, f"Listing row status was not updated to CANCELLED. Found: '{row_status}'"

        # Restore to ACTIVE
        po_page.open_po_edit_modal(row_index=0)
        po_page.select_status("ACTIVE")
        po_page.click_update()
        authenticated_page.wait_for_timeout(1000)
        update_test_result("TC_PO_POS_12", "Passed", "Status transition to CANCELLED verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_13")
    def test_po_status_transition_fully_used_and_filter(self, authenticated_page):
        """Verify Status transition to FULLY_USED and filter interplay."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_ref = po_page.get_first_row_po_ref()
        po_page.open_po_edit_modal(row_index=0)

        po_page.select_status("FULLY_USED")
        po_page.click_update()

        snackbar = po_page.get_snackbar_info(timeout_ms=5000)
        assert snackbar["is_success"], "Success snackbar did not appear on updating status to FULLY_USED."

        # Enable Include Fully Used PO to locate and restore
        po_page.toggle_include_fully_used_po(check=True)
        po_page.open_po_edit_modal(po_ref=po_ref)
        po_page.select_status("ACTIVE")
        po_page.click_update()
        authenticated_page.wait_for_timeout(1000)
        po_page.toggle_include_fully_used_po(check=False)
        update_test_result("TC_PO_POS_13", "Passed", "FULLY_USED transition and filter interplay verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_14")
    def test_po_currency_update_persistence(self, authenticated_page):
        """Verify Currency update persists and reflects in listing table."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        po_page.select_currency("USD")
        po_page.click_update()

        snackbar = po_page.get_snackbar_info(timeout_ms=5000)
        assert snackbar["is_success"], "Success snackbar did not appear on updating currency."

        try:
            authenticated_page.wait_for_function(
                "() => document.querySelector('tbody tr td:nth-child(5)')?.innerText.includes('USD')",
                timeout=6000,
            )
        except Exception:
            authenticated_page.wait_for_timeout(1500)

        row_curr = po_page.get_row_currency(0)
        assert "USD" in row_curr, f"Listing table row did not reflect updated currency 'USD'. Found: '{row_curr}'"

        # Restore to INR
        po_page.open_po_edit_modal(row_index=0)
        po_page.select_currency("INR")
        po_page.click_update()
        authenticated_page.wait_for_timeout(1000)
        update_test_result("TC_PO_POS_14", "Passed", "Currency update persistence verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_15")
    def test_po_reference_no_update_persistence(self, authenticated_page):
        """Verify PO Reference Number modification persists and is searchable."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        orig_ref = po_page.get_first_row_po_ref()
        new_ref = f"{orig_ref}9" if len(orig_ref) < 15 else orig_ref[:-1]

        po_page.open_po_edit_modal(row_index=0)
        po_page.set_form_field("po_ref_no", new_ref)
        po_page.click_update()

        snackbar = po_page.get_snackbar_info(timeout_ms=5000)
        assert snackbar["is_success"], "Success snackbar did not appear on updating PO Reference No."

        # Verify search retrieves new ref
        count = po_page.search_purchase_order(new_ref)
        assert count > 0, f"Search by updated reference '{new_ref}' yielded no rows."

        # Restore original ref
        po_page.open_po_edit_modal(po_ref=new_ref)
        po_page.set_form_field("po_ref_no", orig_ref)
        po_page.click_update()
        po_page.search_purchase_order("")
        update_test_result("TC_PO_POS_15", "Passed", "PO Reference modification and search sync verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_16")
    def test_po_amount_update_reflection(self, authenticated_page):
        """Verify Amount fields update and reflection in listing Total Amount."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        po_page.set_form_field("base_amount", "2000")
        po_page.set_form_field("total_amount", "2000")
        po_page.click_update()

        snackbar = po_page.get_snackbar_info(timeout_ms=5000)
        assert snackbar["is_success"], "Success snackbar did not appear on updating amounts."

        row_total = po_page.get_row_total_amount(0)
        assert "2000" in row_total, f"Total amount was not updated to 2000 in listing. Found: '{row_total}'"
        update_test_result("TC_PO_POS_16", "Passed", "Amount fields update verified")

    @pytest.mark.positive
    @pytest.mark.tc_id("TC_PO_POS_17")
    def test_po_document_replacement_reupload(self, authenticated_page):
        """Verify Document replacement / re-upload updates attachment."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        uploaded = po_page.upload_po_document(SAMPLE_PDF)
        assert uploaded, "File upload failed to target file input."

        doc_text = po_page.get_uploaded_document_text()
        assert "sample_po.pdf" in doc_text, f"Uploaded document not reflected. Found: '{doc_text}'"

        link = po_page.get_view_current_document_link()
        assert link is not None, "View Current Document link should be accessible."

        po_page.click_cancel()
        update_test_result("TC_PO_POS_17", "Passed", "Document replacement verified")


@pytest.mark.purchase_order
@pytest.mark.po_update
class TestPurchaseOrderUpdateNegativeFlows:
    """Negative and boundary validation scenarios for Purchase Order Update."""

    @pytest.mark.negative
    @pytest.mark.tc_id("TC_PO_NEG_01")
    def test_po_empty_required_field_snackbar(self, authenticated_page):
        """Verify updating PO with empty mandatory PO Details displays error snackbar."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        # Clear mandatory PO Details
        po_page.set_form_field("po_details", "")
        po_page.click_update()

        snackbar = po_page.get_snackbar_info(timeout_ms=5000)
        assert snackbar["visible"], "Expected validation snackbar did not appear for empty PO Details."
        assert snackbar["is_error"], (
            f"Expected error snackbar (class snackbar-error). "
            f"Actual class: '{snackbar['class']}', message: '{snackbar['text']}'"
        )
        assert "Please Enter PO Details" in snackbar["text"], (
            f"Unexpected error message: '{snackbar['text']}'"
        )

        # Clean up
        po_page.click_cancel()
        update_test_result("TC_PO_NEG_01", "Passed", "Mandatory PO Details validation snackbar verified")

    @pytest.mark.negative
    @pytest.mark.tc_id("TC_PO_NEG_02")
    def test_po_customer_name_rejects_modification(self, authenticated_page):
        """Verify Customer Name field rejects manual alteration or selection change."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        cust_field = authenticated_page.locator(
            "mat-form-field:has-text('Customer Name') mat-select, mat-select[formcontrolname='poCustomer']"
        ).first
        
        # Verify disabled attribute prevents opening options
        is_disabled = cust_field.evaluate(
            "e => e.hasAttribute('disabled') || e.getAttribute('aria-disabled') === 'true' || e.classList.contains('mat-mdc-select-disabled')"
        )
        assert is_disabled, "Customer Name dropdown should be disabled to prevent modifications."

        # Verify options panel does not open
        cust_field.click(force=True)
        options = authenticated_page.locator("mat-option")
        assert options.count() == 0, "Options panel unexpectedly opened for disabled Customer Name."

        po_page.click_cancel()
        update_test_result("TC_PO_NEG_02", "Passed", "Customer Name rejected modification verified")

    @pytest.mark.negative
    @pytest.mark.tc_id("TC_PO_NEG_03")
    def test_po_non_existent_search_graceful(self, authenticated_page):
        """Verify search with non-existent PO Ref No or Name yields no matching records."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)

        # Search for impossible query
        query = "NON_EXISTENT_PO_99999999"
        po_page.search_purchase_order(query)

        # Verify table displays 0 matching rows or empty text
        rows = authenticated_page.locator("tbody tr").all()
        for r in rows:
            text = r.inner_text().strip()
            assert query not in text, f"Non-existent query '{query}' was unexpectedly found."

        # Reset search
        po_page.search_purchase_order("")
        update_test_result("TC_PO_NEG_03", "Passed", "Non-existent search handled gracefully")

    @pytest.mark.negative
    @pytest.mark.tc_id("TC_PO_NEG_04")
    def test_po_file_input_extension_restriction(self, authenticated_page):
        """Verify file input restricts upload of unauthorized file extensions."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        file_input = authenticated_page.locator("input#po_document_url, input[type='file']").first
        accept_attr = file_input.get_attribute("accept") or ""

        # Validate that executable and dangerous scripts are not allowed
        for unauth_ext in [".exe", ".bat", ".sh", ".cmd", ".js"]:
            assert unauth_ext not in accept_attr.lower(), (
                f"Unauthorized extension '{unauth_ext}' found in file accept filter: '{accept_attr}'"
            )

        # Validate approved extensions are present
        for approved_ext in [".pdf", ".doc", ".docx"]:
            assert approved_ext in accept_attr.lower(), (
                f"Expected approved extension '{approved_ext}' missing from accept filter: '{accept_attr}'"
            )

        po_page.click_cancel()
        update_test_result("TC_PO_NEG_04", "Passed", "File input extension restriction verified")

    @pytest.mark.negative
    @pytest.mark.tc_id("TC_PO_NEG_05")
    def test_po_cancel_preserves_original_listing_data(self, authenticated_page):
        """Verify canceling edit with dirty fields does not persist changes to the listing page."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)

        orig_ref = po_page.get_first_row_po_ref()
        po_page.open_po_edit_modal(row_index=0)

        # Alter PO Reference No
        po_page.set_form_field("po_ref_no", "UNSAVED_99999")
        po_page.click_cancel()

        # Check listing page
        current_ref = po_page.get_first_row_po_ref()
        assert current_ref == orig_ref, (
            f"Cancelling edit modified listing data! Expected '{orig_ref}', found '{current_ref}'"
        )
        update_test_result("TC_PO_NEG_05", "Passed", "Cancel preserved original listing data")

    @pytest.mark.negative
    @pytest.mark.tc_id("TC_PO_NEG_06")
    def test_po_modal_close_icon_dismissal(self, authenticated_page):
        """Verify modal close icon ('X') cleanly dismisses modal and discards uncommitted changes."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        po_page.set_form_field("authorized_by", "Unsaved Discard Test")
        po_page.click_close_icon()

        assert not po_page.is_update_form_visible(), "Modal was expected to close on clicking close icon."
        update_test_result("TC_PO_NEG_06", "Passed", "Modal close icon dismissal verified")

    @pytest.mark.negative
    @pytest.mark.tc_id("TC_PO_NEG_07")
    def test_po_search_clear_grid_restoration(self, authenticated_page):
        """Verify clearing search query automatically restores full table records without page refresh."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        authenticated_page.wait_for_function("() => document.querySelectorAll('tbody tr').length >= 1", timeout=10000)
        authenticated_page.wait_for_timeout(1000)

        initial_len = len(po_page.get_purchase_order_rows())
        assert initial_len >= 1, f"Expected at least 1 row in table, found {initial_len}"

        first_ref = po_page.get_first_row_po_ref()
        if first_ref:
            po_page.search_purchase_order(first_ref)
            authenticated_page.wait_for_timeout(1000)
            filtered_count = len(po_page.get_purchase_order_rows())
            assert filtered_count <= initial_len, "Table was not filtered down by search query."

            # Clear search
            po_page.search_purchase_order("")
            authenticated_page.wait_for_timeout(1000)
            restored_count = len(po_page.get_purchase_order_rows())
            assert restored_count == initial_len, (
                f"Clearing search did not restore full rows! Expected {initial_len}, found {restored_count}"
            )
        update_test_result("TC_PO_NEG_07", "Passed", "Search clear grid restoration verified")

    @pytest.mark.negative
    @pytest.mark.tc_id("TC_PO_NEG_08")
    def test_po_mandatory_field_asterisk_indicators(self, authenticated_page):
        """Verify mandatory field asterisk indicators are present only on required fields."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        # Mandatory fields
        for mand_field in ["Customer Name", "PO Details", "Status"]:
            field_loc = authenticated_page.locator(f"mat-form-field:has-text('{mand_field}')")
            asterisk = field_loc.locator(".text-danger, span:has-text('*')")
            assert asterisk.count() > 0, f"Mandatory field '{mand_field}' is missing required asterisk (*) indicator."

        # Optional fields should not have asterisk
        for opt_field in ["Authorized By", "Base Amount", "Tax Amount"]:
            field_loc = authenticated_page.locator(f"mat-form-field:has-text('{opt_field}')")
            asterisk = field_loc.locator(".text-danger")
            assert asterisk.count() == 0, f"Optional field '{opt_field}' unexpectedly has mandatory indicator."

        po_page.click_cancel()
        update_test_result("TC_PO_NEG_08", "Passed", "Mandatory indicators verified")
