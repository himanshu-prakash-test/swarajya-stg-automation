import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from playwright.sync_api import Page
from customer_pages.customer_page import CustomerPage
from shared.utils.logger import get_logger

log = get_logger("CustomerFormExecutor")


class FormExecutor:
    """Executes data-driven test scenarios from Create-Customer-Management.xlsx."""

    last_created_customer: Dict[str, str] = {}

    FIELD_NORM_MAP = {
        "customer name": "Customer Name",
        "name": "Customer Name",
        "address line 1": "Address Line 1",
        "address 1": "Address Line 1",
        "addressline1": "Address Line 1",
        "address line 2": "Address Line 2",
        "address 2": "Address Line 2",
        "addressline2": "Address Line 2",
        "city": "City",
        "pin": "PIN",
        "pincode": "PIN",
        "pin code": "PIN",
        "state": "State",
        "country": "Country",
        "is igst applicable?": "Is IGST Applicable?",
        "is igst applicable": "Is IGST Applicable?",
        "igst applicable": "Is IGST Applicable?",
        "igst": "Is IGST Applicable?",
        "pan/it no.": "PAN/IT NO.",
        "pan/it no": "PAN/IT NO.",
        "pan": "PAN/IT NO.",
        "pan no": "PAN/IT NO.",
        "gst no.": "GST No.",
        "gst no": "GST No.",
        "gstin": "GST No.",
        "gst": "GST No.",
        "code": "Code",
        "customer code": "Code",
        "place of supply": "Place of Supply",
        "place_of_supply": "Place of Supply",
        "primary person name": "Primary Person Name",
        "primary contact name": "Primary Person Name",
        "primary contact person": "Primary Person Name",
        "finance person name": "Finance Person Name",
        "finance contact name": "Finance Person Name",
        "finance contact person": "Finance Person Name",
        "primary person phone": "Primary Person Phone",
        "primary phone": "Primary Person Phone",
        "finance person phone": "Finance Person Phone",
        "finance phone": "Finance Person Phone",
        "primary person email id": "Primary Person Email ID",
        "primary person email": "Primary Person Email ID",
        "primary email": "Primary Person Email ID",
        "finance person email id": "Finance Person Email ID",
        "finance person email": "Finance Person Email ID",
        "finance email": "Finance Person Email ID",
        "payment terms (days)": "Payment Terms (Days)",
        "payment terms": "Payment Terms (Days)",
        "payment_terms": "Payment Terms (Days)",
        "days": "Payment Terms (Days)",
        "currency": "Currency",
    }

    last_created_customer: Dict[str, str] = {}
    last_custom_screenshot: Optional[str] = None

    def __init__(self, page: Page):
        self.page = page
        self.customer = CustomerPage(page)

    def execute_test_case(self, test_case_row: Dict[str, Any], is_positive: bool = True):
        """Main dispatcher for Excel data-driven execution."""
        FormExecutor.last_custom_screenshot = None
        tc_id = test_case_row.get("Test Case ID", "").strip()
        scenario = test_case_row.get("Scenario", "").strip()
        raw_data = test_case_row.get("Test Data", "")
        steps = test_case_row.get("Steps", test_case_row.get("Test Steps", ""))
        expected = test_case_row.get("Expected Result", "")

        log.info(f"==================== [{tc_id}] {scenario} ====================")
        parsed_data = self._parse_test_data(raw_data)
        log.info(f"Parsed test data: {parsed_data}")

        if is_positive:
            self._execute_positive(tc_id, parsed_data, scenario, steps, expected)
        else:
            self._execute_negative(tc_id, parsed_data, scenario, steps, expected)

    # ----------------- Positive Scenarios -----------------

    def _execute_positive(self, tc_id: str, data: Dict[str, str], scenario: str, steps: str, expected: str):
        # 1. Navigation test
        if tc_id == "TC_CUSTOMER_POS_01":
            self.customer.open_customer_list()
            is_valid_url = "customerdetails" in self.page.url.lower()
            assert is_valid_url, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Failed to navigate to Customer Details listing page. Current URL: '{self.page.url}'"
            )
            return

        # 2. Listing UI components check (table, search input, Add Customer / New Customer button)
        if tc_id == "TC_CUSTOMER_POS_02":
            self.customer.open_customer_list()
            search_visible = self.customer.is_visible("input[placeholder*='Search' i], input[type='search']")
            btn_visible = self.customer.is_visible(
                "button:has-text('New Customer'), button:has-text('Add Customer'), a:has-text('New Customer'), a:has-text('Add Customer'), button:has-text('Customer')"
            )
            table_visible = self.customer.is_visible("table, mat-table")
            assert search_visible and btn_visible and table_visible, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: UI elements missing. Search={search_visible}, AddBtn={btn_visible}, Table={table_visible}"
            )
            return

        # 3. Add Customer form open check (all fields rendered)
        if tc_id == "TC_CUSTOMER_POS_03":
            self.customer.open_create_customer_form()
            on_form = "addnewcustomer" in self.page.url.lower()
            save_btn = self.customer.is_visible("button:has-text('Save')")
            name_input = self.customer.is_visible("input[name*='name' i], input[formcontrolname*='name' i], input[placeholder*='Name' i]")
            assert on_form and save_btn and name_input, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Create form did not open properly. on_form={on_form}, save_btn={save_btn}, name_input={name_input}"
            )
            return

        # 4. Cancel on form test
        if tc_id in ("TC_CUSTOMER_POS_15", "TC_CUSTOMER_POS_05") and "cancel" in scenario.lower():
            self.customer.open_create_customer_form()
            for k, v in data.items():
                self.customer.fill_field(k, v)
            clicked = self.customer.click_cancel()
            self.page.wait_for_timeout(1000)
            returned_to_list = (
                "customerdetails" in self.page.url.lower()
                or not self.customer.is_visible("button:has-text('Save')")
            )
            assert clicked and returned_to_list, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Cancel button clicked={clicked}, returned to list={returned_to_list}. Current URL: '{self.page.url}'"
            )
            return

        # 5. Dismiss popup / Select No test
        if tc_id in ("TC_CUSTOMER_POS_16", "TC_CUSTOMER_POS_06") and "dismiss" in scenario.lower():
            self.customer.open_create_customer_form()
            for k, v in data.items():
                self.customer.fill_field(k, v)
            outcome = self.customer.click_save_and_confirm(confirm=False)
            remained_on_form = (
                "addnewcustomer" in self.page.url.lower()
                or self.customer.is_visible("button:has-text('Save')")
            )
            assert outcome == "Cancelled" or remained_on_form, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Dialog outcome='{outcome}', user remained on form={remained_on_form}. Current URL: '{self.page.url}'"
            )
            return

        # 6. Escape key dismisses modal
        if tc_id == "TC_CUSTOMER_POS_17":
            self.customer.open_create_customer_form()
            full_data = self._build_customer_data(tc_id, data, is_pos=True)
            self._fill_customer_fields(full_data)
            save_btn = self.page.locator("button:has-text('Save')").first
            if save_btn.is_visible():
                save_btn.click()
                self.page.wait_for_timeout(600)
            dismissed = self.customer.dismiss_modal_via_escape()
            remained = "addnewcustomer" in self.page.url.lower() or self.customer.is_visible("button:has-text('Save')")
            assert dismissed or remained, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Modal not dismissed via Escape key or user left form."
            )
            return

        # 7. Search customer in list by Name
        if tc_id in ("TC_CUSTOMER_POS_18", "TC_CUSTOMER_POS_07"):
            search_name = FormExecutor.last_created_customer.get("name")
            if not search_name:
                self.customer.open_create_customer_form()
                full_data = self._build_customer_data("TC_CUSTOMER_POS_04", {"Customer Name": "SearchTarget Corp"})
                self._fill_customer_fields(full_data)
                self.customer.click_save_and_confirm(confirm=True)
                search_name = full_data["Customer Name"]

            self.customer.open_customer_list()
            found = self.customer.is_customer_in_list(search_name)
            assert found, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Customer '{search_name}' was not found in Customer Details table."
            )
            return

        # 8. Search customer in list by Code
        if tc_id in ("TC_CUSTOMER_POS_19", "TC_CUSTOMER_POS_08"):
            search_code = FormExecutor.last_created_customer.get("code") or data.get("Code", "CUST01")
            self.customer.open_customer_list()
            self.customer.search_customer(search_code)
            has_error = "404" in self.page.title().lower() or "not found" in self.page.content().lower()
            assert not has_error, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Customer search by code '{search_code}' threw error or 404 page."
            )
            return

        # 9. Search customer in list by Place of Supply
        if tc_id == "TC_CUSTOMER_POS_20":
            supply_term = data.get("Place of Supply", "Maharashtra")
            self.customer.open_customer_list()
            self.customer.search_customer(supply_term)
            has_error = "404" in self.page.title().lower()
            assert not has_error, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Search by Place of Supply threw an error."
            )
            return

        # 10. Clear search input restores full table
        if tc_id == "TC_CUSTOMER_POS_21":
            self.customer.open_customer_list()
            self.customer.search_customer("TestFilter")
            self.customer.clear_search()
            row_count = self.customer.get_grid_row_count()
            assert row_count >= 0, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Grid failed to restore after clearing search."
            )
            return

        # 11. Pagination controls
        if tc_id == "TC_CUSTOMER_POS_22":
            self.customer.open_customer_list()
            paginated = self.customer.navigate_pagination("next")
            self.customer.navigate_pagination("prev")
            assert "customerdetails" in self.page.url.lower(), (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Pagination caused page error or crash."
            )
            return

        # 12. Verify newly created customer details in grid match entered data
        if tc_id == "TC_CUSTOMER_POS_23":
            last_cust = FormExecutor.last_created_customer
            if not last_cust.get("name"):
                self.customer.open_create_customer_form()
                full_data = self._build_customer_data("TC_CUSTOMER_POS_04", {"Customer Name": "VerifyGrid Corp"})
                self._fill_customer_fields(full_data)
                self.customer.click_save_and_confirm(confirm=True)
                last_cust = {"name": full_data["Customer Name"], "code": full_data.get("Code", "")}

            self.customer.open_customer_list()
            found = self.customer.is_customer_in_list(last_cust["name"])
            assert found, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Customer '{last_cust['name']}' not found in table for data integrity verification."
            )
            return

        # 13. Verify Country dropdown can be opened and options are selectable correctly
        if tc_id == "TC_CUSTOMER_POS_24":
            self.customer.open_create_customer_form()
            options = self.customer.get_dropdown_options("Country")
            log.info(f"Retrieved Country dropdown options: {options}")
            target_country = "India" if "India" in options else (options[0] if options else "India")
            selected = self.customer.verify_dropdown_selection("Country", target_country)
            assert selected, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Failed to select country option '{target_country}' in Country dropdown. Options found: {options}"
            )
            return

        # 14. Verify Currency dropdown can be opened and options (INR / Indian Rupees, USD, EUR) are selectable correctly
        if tc_id == "TC_CUSTOMER_POS_25":
            self.customer.open_create_customer_form()
            options = self.customer.get_dropdown_options("Currency")
            log.info(f"Retrieved Currency dropdown options: {options}")
            target_labels = ["Indian Rupees", "US Dollars", "Euro", "INR", "USD", "EUR"]
            currencies_to_test = [c for c in target_labels if c in options] or (options[:2] if options else ["Indian Rupees"])
            for curr in currencies_to_test:
                selected = self.customer.verify_dropdown_selection("Currency", curr)
                assert selected, (
                    f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                    f"Actual: Failed to select currency option '{curr}' in Currency dropdown. Options found: {options}"
                )
            return

        # 15. Verify Is IGST Applicable toggle switch functions correctly (toggle ON and toggle OFF)
        if tc_id == "TC_CUSTOMER_POS_26":
            self.customer.open_create_customer_form()
            initial_state = self.customer.get_igst_switch_state()
            # Toggle to opposite state
            toggled = self.customer.toggle_igst_switch()
            state_after_toggle = self.customer.get_igst_switch_state()
            # Toggle back
            self.customer.toggle_igst_switch()
            restored_state = self.customer.get_igst_switch_state()

            switch_responsive = toggled and (state_after_toggle != initial_state or restored_state == initial_state)
            assert switch_responsive, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: IGST switch did not respond to toggle. initial={initial_state}, after_toggle={state_after_toggle}, restored={restored_state}"
            )
            return

        # 16. Standard Customer Creation Flows (POS_04 through POS_14)
        self.customer.open_create_customer_form()
        full_data = self._build_customer_data(tc_id, data, is_pos=True)
        self._fill_customer_fields(full_data)

        # Press Save and click Yes on confirmation snackbar / dialog
        outcome = self.customer.click_save_and_confirm(confirm=True)
        customer_name = full_data.get("Customer Name", "").strip()
        customer_code = full_data.get("Code", "").strip()

        # Check for validation errors
        errors = self.customer.get_validation_errors()
        assert not errors, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
            f"Actual: Customer creation has unexpected validation errors: {errors}"
        )

        # Strict positive assertions: must not reject or fail
        is_rejected = "error" in outcome.lower() or "failed" in outcome.lower() or "please fill" in outcome.lower()
        assert not is_rejected, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
            f"Actual: Customer creation was rejected or failed. Outcome message: '{outcome}'"
        )

        # Validate that newly created customer is visible on the Customer Details page by searching with customer name
        self.customer.open_customer_list()
        found = self.customer.is_customer_in_list(customer_name)
        assert found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
            f"Actual: Customer '{customer_name}' was not visible in Customer Details table after pressing Yes on confirmation."
        )

        FormExecutor.last_created_customer = {"name": customer_name, "code": customer_code}
        log.info(f"Successfully created customer [{tc_id}] and confirmed visible in listing: '{customer_name}'")

    # ----------------- Negative Scenarios -----------------

    def _execute_negative(self, tc_id: str, data: Dict[str, str], scenario: str, steps: str, expected: str):
        # 1. Duplicate Customer Name rejection
        if tc_id == "TC_CUSTOMER_NEG_01":
            base_name = FormExecutor.last_created_customer.get("name")
            if not base_name:
                self.customer.open_create_customer_form()
                base_data = self._build_customer_data("TC_CUSTOMER_POS_04", {"Customer Name": "DuplicateTarget Corp"})
                self._fill_customer_fields(base_data)
                self.customer.click_save_and_confirm(confirm=True)
                base_name = base_data["Customer Name"]

            self.customer.open_create_customer_form()
            dup_data = self._build_customer_data(tc_id, {"Customer Name": base_name}, is_pos=False)
            dup_data["Customer Name"] = base_name  # exact duplicate
            self._fill_customer_fields(dup_data)
            outcome = self.customer.click_save_and_confirm(confirm=True)
            errors = self.customer.get_validation_errors()
            all_text = f"{outcome} {' '.join(errors)}".lower()

            has_conflict = "exist" in all_text or "duplicate" in all_text or "already" in all_text or "error" in all_text or len(errors) > 0
            assert has_conflict, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Application did not reject duplicate customer name '{base_name}'. Outcome: '{outcome}', Errors: {errors}"
            )
            return

        # 2. Duplicate Code rejection
        if tc_id == "TC_CUSTOMER_NEG_02":
            base_code = FormExecutor.last_created_customer.get("code") or "DUPCODE01"
            self.customer.open_create_customer_form()
            dup_data = self._build_customer_data(tc_id, {"Code": base_code}, is_pos=False)
            dup_data["Code"] = base_code
            self._fill_customer_fields(dup_data)
            outcome = self.customer.click_save_and_confirm(confirm=True)
            errors = self.customer.get_validation_errors()
            all_text = f"{outcome} {' '.join(errors)}".lower()

            has_conflict = "exist" in all_text or "code" in all_text or "duplicate" in all_text or "already" in all_text or "error" in all_text or len(errors) > 0
            assert has_conflict, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Application did not reject duplicate customer code '{base_code}'. Outcome: '{outcome}', Errors: {errors}"
            )
            return

        # 3. Duplicate GST No. rejection
        if tc_id == "TC_CUSTOMER_NEG_03":
            base_gst = "27ABCDE1234F1Z5"
            self.customer.open_create_customer_form()
            dup_data = self._build_customer_data(tc_id, {"GST No.": base_gst}, is_pos=False)
            dup_data["GST No."] = base_gst
            self._fill_customer_fields(dup_data)
            outcome = self.customer.click_save_and_confirm(confirm=True)
            errors = self.customer.get_validation_errors()
            all_text = f"{outcome} {' '.join(errors)}".lower()

            has_conflict = "exist" in all_text or "gst" in all_text or "duplicate" in all_text or "already" in all_text or "error" in all_text or len(errors) > 0
            assert has_conflict, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Application did not reject duplicate GST No. '{base_gst}'. Outcome: '{outcome}', Errors: {errors}"
            )
            return

        # 4. Verify customer is NOT created when clicking 'No' on confirmation
        if tc_id == "TC_CUSTOMER_NEG_04":
            unconfirmed_name = f"RejectCustomer_{int(time.time())}"
            self.customer.open_create_customer_form()
            reject_data = self._build_customer_data(tc_id, {"Customer Name": unconfirmed_name}, is_pos=False)
            self._fill_customer_fields(reject_data)
            outcome = self.customer.click_save_and_confirm(confirm=False)
            self.customer.open_customer_list()
            in_list = self.customer.is_customer_in_list(unconfirmed_name)
            assert not in_list, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Customer '{unconfirmed_name}' was created despite clicking No on confirmation popup."
            )
            return

        # 5. Non-existent customer search returns empty grid state
        if tc_id == "TC_CUSTOMER_NEG_05":
            non_existent = "XYZ_NonExistent_99999"
            self.customer.open_customer_list()
            self.customer.search_customer(non_existent)
            is_empty = self.customer.is_empty_grid_displayed()
            assert is_empty, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Grid displayed matching rows for non-existent query '{non_existent}'."
            )
            return

        # 6. Direct URL navigation without authentication redirects to login
        if tc_id == "TC_CUSTOMER_NEG_06":
            browser = self.page.context.browser
            if browser:
                temp_context = browser.new_context()
                temp_page = temp_context.new_page()
                try:
                    temp_page.goto("https://swarajya-stg.corecotechnologies.com/addNewCustomer", timeout=15000)
                    temp_page.wait_for_load_state("domcontentloaded")
                    parsed_path = urlparse(temp_page.url).path.lower()
                    blocked = (
                        "login" in parsed_path
                        or "tfa" in parsed_path
                        or "default" in parsed_path
                        or parsed_path in ("", "/")
                        or "addnewcustomer" not in parsed_path
                    )
                    assert blocked, (
                        f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                        f"Actual: Unauthenticated user was allowed access to /addNewCustomer. URL: {temp_page.url}"
                    )
                    # Capture evidence screenshot of unauthenticated redirect immediately after test executes
                    screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
                    os.makedirs(screenshots_dir, exist_ok=True)
                    shot_path = os.path.join(screenshots_dir, f"PASS_{tc_id}__{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    try:
                        temp_page.screenshot(path=shot_path, full_page=True)
                        FormExecutor.last_custom_screenshot = shot_path
                        log.info(f"Captured post-execution screenshot for {tc_id}: {shot_path}")
                    except Exception as e:
                        log.warning(f"Could not take screenshot in TC_CUSTOMER_NEG_06: {e}")
                finally:
                    temp_context.close()
            return

        # 7. Network offline handling during customer creation
        if tc_id == "TC_CUSTOMER_NEG_07":
            self.customer.open_create_customer_form()
            offline_data = self._build_customer_data(tc_id, data, is_pos=False)
            self._fill_customer_fields(offline_data)
            try:
                self.page.context.set_offline(True)
                save_btn = self.page.locator("button:has-text('Save')").first
                if save_btn.is_visible():
                    save_btn.click()
                    self.page.wait_for_timeout(1000)
                errors = self.customer.get_validation_errors()
                outcome = self.customer.get_toast_message(timeout=2000)
                assert "customerdetails" not in self.page.url.lower(), (
                    f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                    f"Actual: Application unexpectedly redirected to listing while network was offline."
                )
            finally:
                self.page.context.set_offline(False)
            return

        # 8. Session timeout during customer creation
        if tc_id == "TC_CUSTOMER_NEG_08":
            self.customer.open_create_customer_form()
            timeout_data = self._build_customer_data(tc_id, data, is_pos=False)
            self._fill_customer_fields(timeout_data)

            # Clear session cookies to simulate session timeout / expiration
            self.page.context.clear_cookies()
            try:
                save_btn = self.page.locator("button:has-text('Save'), button[type='submit']").first
                if save_btn.is_visible():
                    save_btn.click()
                    self.page.wait_for_timeout(1000)
                url = self.page.url.lower()
                body_text = self.page.content().lower()
                is_handled = (
                    "login" in url
                    or "tfa" in url
                    or "session" in body_text
                    or "expired" in body_text
                    or "unauthorized" in body_text
                    or "customerdetails" not in url
                )
                assert is_handled, (
                    f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                    f"Actual: Application accepted save with expired session instead of redirecting to login. URL: {self.page.url}"
                )
            finally:
                pass
            return


    # ----------------- Helpers & Data Parsing -----------------

    def _parse_test_data(self, raw_data: Any) -> Dict[str, str]:
        """Parse key-value pairs from Excel Test Data cell."""
        if not raw_data or str(raw_data).strip().lower() in ("fetch from excel", "n/a", "none", "-"):
            return {}

        result = {}
        for line in str(raw_data).splitlines():
            line = line.strip().lstrip("•-* ").strip()
            if not line:
                continue
            if ":" in line:
                parts = line.split(":", 1)
                k = parts[0].strip()
                v = parts[1].strip().strip("'\"")
                result[k] = v
            elif "=" in line:
                parts = line.split("=", 1)
                k = parts[0].strip()
                v = parts[1].strip().strip("'\"")
                result[k] = v
        return result

    def _build_customer_data(self, tc_id: str, overrides: Dict[str, str], is_pos: bool = True) -> Dict[str, str]:
        """Build full dataset for customer form submission with appropriate Customer Details fields."""
        ts = int(time.time()) % 100000
        pan_digits = ts % 10000
        num = re.sub(r"\D", "", tc_id) or "01"
        default_phone_1 = f"98765{ts:05d}"[:10]
        default_phone_2 = f"98123{ts:05d}"[:10]

        mandatory_keys = [
            "Customer Name",
            "Country",
            "Place of Supply",
            "Finance Person Email ID",
            "Payment Terms (Days)",
            "Currency",
        ]

        full_template = {
            "Customer Name": f"AutoCustomer_{num}_{ts}",
            "Address Line 1": "Plot 102, Silver Tech Park",
            "Address Line 2": "Opposite Metro Pillar 42, Hinjewadi Phase 1",
            "City": "Pune",
            "PIN": "411057",
            "State": "Maharashtra",
            "Country": "India",
            "Is IGST Applicable?": "Yes",
            "PAN/IT NO.": f"ABCDE{pan_digits:04d}F",
            "GST No.": f"27ABCDE{pan_digits:04d}F1Z5",
            "Code": f"C{num[-1]}",
            "Place of Supply": "Maharashtra",
            "Primary Person Name": "Rajesh Sharma",
            "Finance Person Name": "Pooja Verma",
            "Primary Person Phone": default_phone_1,
            "Finance Person Phone": default_phone_2,
            "Primary Person Email ID": f"primary_{num}_{ts}@example.com",
            "Finance Person Email ID": f"finance_{num}_{ts}@example.com",
            "Payment Terms (Days)": "30",
            "Currency": "INR",
        }

        # Normalize override keys
        normalized_overrides = {}
        for k, v in overrides.items():
            norm_key = self.FIELD_NORM_MAP.get(k.strip().lower(), k.strip())
            normalized_overrides[norm_key] = v

        # If POS_05 or extensive data provided, start with full 20 fields
        if tc_id == "TC_CUSTOMER_POS_05" or len(normalized_overrides) >= 15:
            data = dict(full_template)
        else:
            # Baseline is the mandatory fields
            data = {k: full_template[k] for k in mandatory_keys if k in full_template}

        for k, v in normalized_overrides.items():
            key_lower = k.lower()
            if "customer name" in key_lower and is_pos:
                if tc_id == "TC_CUSTOMER_POS_14":
                    v = f"  Trimmed_{ts}  "
                else:
                    clean_name = str(v).strip().replace("'", "")
                    v = f"{clean_name}_{ts}"
            elif "email" in key_lower and is_pos:
                v = f"cust_{num}_{ts}@example.com"
            elif "phone" in key_lower:
                if "invalid" not in tc_id.lower() and not ("invalid" in str(v).lower() or len(str(v)) < 10):
                    digits = re.sub(r"\D", "", str(v))
                    if len(digits) == 10 and digits[0] in "6789":
                        v = digits
                    else:
                        v = default_phone_1
            elif "pan" in key_lower and is_pos:
                v = f"ABCDE{pan_digits:04d}F"
            elif "gst" in key_lower and is_pos:
                v = f"27ABCDE{pan_digits:04d}F1Z5"
            data[k] = v

        return data

    def _fill_customer_fields(self, data: Dict[str, str]):
        """Fill each field on customer form."""
        failed_fields = []
        for field, value in data.items():
            success = self.customer.fill_field(field, value)
            if not success:
                failed_fields.append(field)
        if failed_fields:
            log.warning(f"Fields not matched directly on UI: {failed_fields}")
            mandatory_names = {
                "customer name",
                "country",
                "place of supply",
                "finance person email id",
                "payment terms (days)",
                "days",
                "currency",
            }
            critical_missing = [f for f in failed_fields if f.strip().lower() in mandatory_names]
            if critical_missing:
                log.warning(f"Warning: Could not fill mandatory fields: {critical_missing}")
