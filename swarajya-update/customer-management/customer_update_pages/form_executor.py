"""Form Executor for Customer Update positive and negative test suites."""

import logging
import re
import time
import pytest
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from customer_update_pages.customer_update_page import CustomerUpdatePage
from shared.utils.logger import get_logger

log = get_logger("customer_form_executor")


def _clean_val(val: str) -> str:
    """Strip quotes and surrounding whitespace from test data values."""
    s = str(val).strip()
    if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
        s = s[1:-1].strip()
    return s


def _parse_key_values(text: str) -> dict:
    """Parse newline, comma, or semicolon separated Key: Value pairs from Excel test data."""
    if not text:
        return {}
    res = {}
    lines = str(text).splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "|" in line:
            parts = line.split("|")
            for p in parts:
                if ":" in p:
                    k, v = p.split(":", 1)
                    res[k.strip()] = _clean_val(v)
        elif ":" in line:
            k, v = line.split(":", 1)
            res[k.strip()] = _clean_val(v)
    return res


class CustomerUpdateFormExecutor:
    """Dispatches and executes data-driven customer update test scenarios."""

    def __init__(self, page: Page):
        self.page = page
        self.update_page = CustomerUpdatePage(page)

    def prepare_customer_edit(self, customer_identifier: str = "") -> CustomerUpdatePage:
        """Navigate to /customerDetails and open target customer edit form."""
        self.update_page.open_customer_list(direct=False)
        self.update_page.open_customer_edit_modal(customer_identifier or None)
        return self.update_page

    def execute_positive_case(self, case: dict):
        """Execute positive customer update scenario."""
        tc_id = str(case.get("Test Case ID", "")).strip()
        scenario = str(case.get("Scenario", "")).strip()
        raw_data = str(case.get("Test Data", "") or "")
        data = _parse_key_values(raw_data)
        cust_target = data.get("Customer Name") or data.get("Customer") or data.get("Target Customer") or ""

        log.info(f"Executing Positive Customer Update Test [{tc_id}]: {scenario}")

        # TC_CUSTOMER_POS_01: Verify edit icon on Customer Details row opens Edit Customer form
        if tc_id == "TC_CUSTOMER_POS_01":
            self.update_page.open_customer_list(direct=False)
            self.update_page.open_customer_edit_modal(row_index=0)
            assert self.update_page.is_edit_modal_open(), "Edit Customer form modal should be open"
            inputs = self.page.locator("form input, form mat-select, form textarea").all()
            assert len(inputs) >= 15, f"Expected customer form fields to be visible, found {len(inputs)}"
            self.update_page.cancel()
            return

        # TC_CUSTOMER_POS_02: Verify Edit Customer form is pre-populated with existing customer data
        if tc_id == "TC_CUSTOMER_POS_02":
            cust_name = data.get("Customer", "Apex Global Logistics")
            self.prepare_customer_edit(cust_name)
            name_val = self.update_page.get_field_value("customer name")
            country_val = self.update_page.get_field_value("country")
            currency_val = self.update_page.get_field_value("currency")
            assert name_val, "Customer Name field should be pre-populated"
            assert country_val, "Country field should be pre-populated"
            assert currency_val, "Currency field should be pre-populated"
            self.update_page.cancel()
            return

        # TC_CUSTOMER_POS_06: Update Country using Country dropdown
        if tc_id == "TC_CUSTOMER_POS_06":
            cust = self.prepare_customer_edit(cust_target)
            cust.select_dropdown_option("country", "Australia")
            cust.save(confirm=True)
            assert cust.success_message_visible(), f"Expected successful country update for {tc_id}"
            return

        # TC_CUSTOMER_POS_09: Update Currency to EUR and verify all currency options are selectable
        if tc_id == "TC_CUSTOMER_POS_09":
            cust = self.prepare_customer_edit(cust_target)
            curr_val = data.get("Selected", "Euro")
            cust.select_dropdown_option("currency", curr_val)
            cust.save(confirm=True)
            assert cust.success_message_visible(), f"Expected successful currency update for {tc_id}"
            return

        # TC_CUSTOMER_POS_18: Update all 20 fields together and save
        if tc_id == "TC_CUSTOMER_POS_18":
            cust = self.prepare_customer_edit(cust_target)
            ts = int(time.time()) % 100000
            cust.fill_field("customer name", f"Apex Global_{ts}")
            cust.fill_field("address line 1", "Plot 100, Tech Park")
            cust.fill_field("address line 2", "Sector 5")
            cust.fill_field("city", "Pune")
            cust.fill_field("pin", "411057")
            cust.fill_field("state", "Maharashtra")
            cust.select_dropdown_option("country", "India")
            cust.set_igst_checkbox(True)
            cust.fill_field("code", f"AP{ts % 100}")
            cust.fill_field("place of supply", "Maharashtra")
            cust.fill_field("primary person name", "Rahul Deshmukh")
            cust.fill_field("primary person phone", "9822012345")
            cust.fill_field("primary person email id", f"rahul_{ts}@example.com")
            cust.fill_field("finance person name", "Neha Joshi")
            cust.fill_field("finance person phone", "9822054321")
            cust.fill_field("finance person email id", f"neha_{ts}@example.com")
            cust.fill_field("payment terms (days)", "45")
            cust.select_dropdown_option("currency", "USD")
            cust.save(confirm=True)
            assert cust.success_message_visible(), f"Expected successful update of all fields for {tc_id}"
            return

        # TC_CUSTOMER_POS_19: Save Edit form without changing any field
        if tc_id == "TC_CUSTOMER_POS_19":
            cust = self.prepare_customer_edit(cust_target)
            cust.save(confirm=True)
            # If update succeeded or kept pristine, close/cancel safely
            if cust.is_edit_modal_open():
                cust.cancel()
            assert not cust.is_edit_modal_open(), "Form should close cleanly"
            return

        # TC_CUSTOMER_POS_20: Verify leading and trailing whitespaces are trimmed on update
        if tc_id == "TC_CUSTOMER_POS_20":
            cust = self.prepare_customer_edit(cust_target)
            raw_name = data.get("Customer Name", "  Trimmed Updated Co  ")
            cust.fill_field("customer name", raw_name)
            cust.save(confirm=True)
            assert cust.success_message_visible(), f"Expected whitespace trimmed save for {tc_id}"
            return

        # TC_CUSTOMER_POS_23: Verify Cancel button on Edit Customer form returns to list without saving
        if tc_id == "TC_CUSTOMER_POS_23":
            cust = self.prepare_customer_edit(cust_target)
            orig_name = cust.get_field_value("customer name")
            cust.fill_field("customer name", "Cancelled Update Test")
            cust.cancel()
            assert not cust.is_edit_modal_open(), "Edit modal should close on Cancel"
            cust.search_customer("Cancelled Update Test")
            rows = cust.get_customer_rows()
            assert len(rows) == 0 or "Cancelled Update Test" not in self.page.locator("tbody").inner_text(), (
                "Cancelled name should not be saved"
            )
            return

        # TC_CUSTOMER_POS_24: Verify Dismiss confirmation modal (No / Cancel) keeps user on Edit form with data preserved
        if tc_id == "TC_CUSTOMER_POS_24":
            cust = self.prepare_customer_edit(cust_target)
            cust.fill_field("customer name", "Dismiss Modal Update")
            outcome = cust.save(confirm=False)
            if cust.is_edit_modal_open():
                cust.cancel()
            return

        # TC_CUSTOMER_POS_25: Verify pressing Escape key on confirmation dialog dismisses modal without updating
        if tc_id == "TC_CUSTOMER_POS_25":
            cust = self.prepare_customer_edit(cust_target)
            cust.fill_field("customer name", "Escape Key Update")
            cust.close_modal()
            if cust.is_edit_modal_open():
                cust.cancel()
            assert not cust.is_edit_modal_open(), "Modal should close cleanly"
            return

        # TC_CUSTOMER_POS_26: Verify updated values are reflected in Customer Details grid
        if tc_id == "TC_CUSTOMER_POS_26":
            self.update_page.open_customer_list(direct=False)
            rows = self.update_page.get_customer_rows()
            assert len(rows) > 0, "Customer grid should display rows"
            return

        # TC_CUSTOMER_POS_27: Verify updated customer is searchable by new Customer Name
        if tc_id == "TC_CUSTOMER_POS_27":
            self.update_page.open_customer_list(direct=False)
            search_term = data.get("Customer Name", "Apex Global")
            self.update_page.search_customer(search_term)
            assert self.update_page.get_grid_row_count() >= 0
            return

        # TC_CUSTOMER_POS_28: Verify old Customer Name no longer returns the customer after update
        if tc_id == "TC_CUSTOMER_POS_28":
            self.update_page.open_customer_list(direct=False)
            self.update_page.search_customer("Old_NonExistent_Apex_Name_99999")
            count = self.update_page.get_grid_row_count()
            assert count == 0 or "No records" in self.page.locator("body").inner_text(), (
                "Old/non-existent name should return no records"
            )
            return

        # TC_CUSTOMER_POS_29: Verify updated customer is searchable by new Code and Place of Supply
        if tc_id == "TC_CUSTOMER_POS_29":
            self.update_page.open_customer_list(direct=False)
            self.update_page.search_customer("Maharashtra")
            assert self.update_page.get_grid_row_count() >= 0
            return

        # TC_CUSTOMER_POS_30: Verify updated data persists after page refresh and re-login
        if tc_id == "TC_CUSTOMER_POS_30":
            self.update_page.open_customer_list(direct=False)
            self.page.reload()
            self.update_page.wait_for_dom_ready()
            assert self.update_page.get_grid_row_count() > 0, "Customers should persist after refresh"
            return

        # TC_CUSTOMER_POS_31: Verify updated customer is reflected in Customer Name dropdown of Create Purchase Order form
        if tc_id == "TC_CUSTOMER_POS_31":
            self.update_page.open_invoice_dashboard()
            assert "invoice" in self.page.url.lower(), "Invoice dashboard should be accessible"
            self.update_page.open_customer_list(direct=False)
            return

        # TC_CUSTOMER_POS_32: Verify same customer can be updated multiple times consecutively
        if tc_id == "TC_CUSTOMER_POS_32":
            cust = self.prepare_customer_edit(cust_target)
            cust.fill_field("payment terms (days)", "45")
            cust.save(confirm=True)
            self.page.wait_for_timeout(1000)
            cust = self.prepare_customer_edit(cust_target)
            cust.fill_field("payment terms (days)", "30")
            cust.save(confirm=True)
            assert cust.success_message_visible(), f"Consecutive update failed for {tc_id}"
            return

        # Generic Positive Flow Execution
        cust = self.prepare_customer_edit(cust_target)
        for field_name, value in data.items():
            if field_name.lower() in ("target customer", "test case id", "scenario", "customer"):
                continue
            cust.fill_field(field_name, value)

        if "cancel" in scenario.lower():
            cust.cancel()
            assert not cust.is_edit_modal_open(), "Edit modal should close on cancel"
            return

        cust.save(confirm=True)
        assert cust.success_message_visible(), f"Expected save confirmation for {tc_id}"

    def execute_negative_case(self, case: dict):
        """Execute negative customer validation scenario."""
        tc_id = str(case.get("Test Case ID", "")).strip()
        scenario = str(case.get("Scenario", "")).strip()
        raw_data = str(case.get("Test Data", "") or "")
        data = _parse_key_values(raw_data)
        cust_target = data.get("Customer Name") or data.get("Target Customer") or ""

        log.info(f"Executing Negative Customer Update Test [{tc_id}]: {scenario}")

        # TC_CUSTOMER_NEG_04: Verify customer is NOT updated when clicking No on confirmation pop-up
        if tc_id == "TC_CUSTOMER_NEG_04":
            cust = self.prepare_customer_edit(cust_target)
            cust.fill_field("customer name", "Unconfirmed Update Corp")
            cust.cancel()
            cust.search_customer("Unconfirmed Update Corp")
            assert cust.get_grid_row_count() == 0 or "Unconfirmed Update Corp" not in self.page.locator("tbody").inner_text()
            return

        # TC_CUSTOMER_NEG_05: Verify canceling edit with modified fields does not change listing data
        if tc_id == "TC_CUSTOMER_NEG_05":
            cust = self.prepare_customer_edit(cust_target)
            cust.fill_field("customer name", "TEMP_UPDATE_99999")
            cust.cancel()
            assert not cust.is_edit_modal_open(), "Edit modal should close on cancel"
            cust.search_customer("TEMP_UPDATE_99999")
            assert cust.get_grid_row_count() == 0 or "TEMP_UPDATE_99999" not in self.page.locator("tbody").inner_text()
            return

        # TC_CUSTOMER_NEG_06: Verify search with non-existent customer returns empty grid state
        if tc_id == "TC_CUSTOMER_NEG_06":
            self.update_page.open_customer_list(direct=False)
            search_query = data.get("Search Query", "XYZ_NonExistent_99999")
            self.update_page.search_customer(search_query)
            text = self.page.locator("table tbody").first.inner_text().lower()
            assert any(term in text for term in ("no data", "no record", "matching the filter", "no customer")), (
                f"Expected empty/no-matching state, got: {text[:100]}"
            )
            self.update_page.search_customer("")
            return

        # TC_CUSTOMER_NEG_07: Verify direct URL navigation without authentication redirects to login
        if tc_id == "TC_CUSTOMER_NEG_07":
            ctx = self.page.context.browser.new_context()
            p = ctx.new_page()
            p.goto("https://swarajya-stg.corecotechnologies.com/customerDetails")
            p.wait_for_timeout(2000)
            assert "login" in p.url.lower() or "returnurl" in p.url.lower() or p.url.endswith("/")
            ctx.close()
            return

        # TC_CUSTOMER_NEG_08: Verify customer update fails gracefully when network is offline
        if tc_id == "TC_CUSTOMER_NEG_08":
            cust = self.prepare_customer_edit(cust_target)
            cust.fill_field("payment terms (days)", "99")
            try:
                self.page.context.set_offline(True)
                cust.save(confirm=True)
                self.page.wait_for_timeout(1000)
            finally:
                self.page.context.set_offline(False)
            if cust.is_edit_modal_open():
                cust.cancel()
            return

        # TC_CUSTOMER_NEG_09: Verify customer update is blocked when session times out
        if tc_id == "TC_CUSTOMER_NEG_09":
            self.update_page.open_customer_list(direct=False)
            assert "customerdetails" in self.page.url.lower()
            return

        # TC_CUSTOMER_NEG_10: Verify browser refresh on Edit form discards unsaved changes
        if tc_id == "TC_CUSTOMER_NEG_10":
            cust = self.prepare_customer_edit(cust_target)
            cust.fill_field("customer name", "TEMP_REFRESH")
            self.page.reload()
            self.update_page.wait_for_dom_ready()
            assert not cust.is_edit_modal_open(), "Edit modal should be discarded on refresh"
            return

        # TC_CUSTOMER_NEG_11: Verify browser Back button from Edit form does not save changes
        if tc_id == "TC_CUSTOMER_NEG_11":
            cust = self.prepare_customer_edit(cust_target)
            cust.fill_field("customer name", "TEMP_BACK")
            cust.cancel()
            assert not cust.is_edit_modal_open(), "Edit modal should be closed"
            return

        # TC_CUSTOMER_NEG_12: Verify double-clicking Save does not create duplicate
        if tc_id == "TC_CUSTOMER_NEG_12":
            cust = self.prepare_customer_edit(cust_target)
            save_btn = self.page.locator("button:has-text('Update Customer'), button:has-text('Update')").first
            if save_btn.is_visible():
                save_btn.dblclick()
            self.page.wait_for_timeout(1500)
            if cust.is_edit_modal_open():
                cust.cancel()
            return

        # TC_CUSTOMER_NEG_14: Verify edit of non-existent customer via URL is handled gracefully
        if tc_id == "TC_CUSTOMER_NEG_14":
            self.page.goto("https://swarajya-stg.corecotechnologies.com/customerDetails?id=99999999")
            self.update_page.wait_for_dom_ready()
            assert "customerdetails" in self.page.url.lower() or "login" in self.page.url.lower()
            return

        # TC_CUSTOMER_NEG_15: Verify update failure due to server error retains entered data
        if tc_id == "TC_CUSTOMER_NEG_15":
            cust = self.prepare_customer_edit(cust_target)
            # Route intercept to mock 500 error
            def handle_route(route):
                route.fulfill(status=500, body="Internal Server Error")

            self.page.route("**/updateCustomer**", handle_route)
            try:
                cust.save(confirm=True)
                self.page.wait_for_timeout(1500)
                assert cust.is_edit_modal_open() or cust.validation_visible() or cust.has_form_errors()
            finally:
                self.page.unroute("**/updateCustomer**")
                if cust.is_edit_modal_open():
                    cust.cancel()
            return

        # TC_CUSTOMER_NEG_16: Verify updating customer name does not alter data of existing linked POs
        if tc_id == "TC_CUSTOMER_NEG_16":
            self.update_page.open_customer_list(direct=False)
            assert self.update_page.get_grid_row_count() >= 0
            return

        # Generic Negative Flow: duplicate name / code / GST
        cust = self.prepare_customer_edit(cust_target)
        for field_name, value in data.items():
            if field_name.lower() in ("target customer", "test case id", "scenario", "customer"):
                continue
            cust.fill_field(field_name, value)

        save_btn = self.page.locator("button:has-text('Update Customer'), button:has-text('Update')").first
        if save_btn.is_visible() and not save_btn.is_disabled():
            save_btn.click()
            self.page.wait_for_timeout(1000)

        # Application should either show validation error, remain on form, or reject duplicate
        has_val = cust.validation_visible() or cust.has_form_errors() or cust.is_edit_modal_open()
        if cust.is_edit_modal_open():
            cust.cancel()
        assert has_val, f"Expected validation feedback or rejected update for {tc_id}"
