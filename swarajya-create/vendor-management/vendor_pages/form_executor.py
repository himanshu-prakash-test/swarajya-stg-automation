import re
import time
from typing import Any, Dict, List, Optional
from playwright.sync_api import Page
from vendor_pages.vendor_page import VendorPage
from shared.utils.logger import get_logger

log = get_logger("VendorFormExecutor")


class FormExecutor:
    """Executes data-driven test scenarios from Create-Vendor-Management.xlsx."""

    last_created_vendor: Dict[str, str] = {}

    def __init__(self, page: Page):
        self.page = page
        self.vendor = VendorPage(page)

    def execute_test_case(self, test_case_row: Dict[str, Any], is_positive: bool = True):
        """Main dispatcher for Excel data-driven execution."""
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
        if tc_id == "TC_VENDOR_POS_01":
            self.vendor.open_vendor_list()
            assert not ("login" in self.page.url.lower() or "404" in self.page.title().lower()), "Failed to navigate to Vendor Management"
            return

        # 2. Cancel on form test
        if tc_id == "TC_VENDOR_POS_06":
            self.vendor.open_create_vendor_form()
            for k, v in data.items():
                self.vendor.fill_field(k, v)
            assert self.vendor.click_cancel(), "Cancel/Reset button failed to respond"
            return

        # 3. Dismiss popup (Select No) test
        if tc_id == "TC_VENDOR_POS_08":
            self.vendor.open_create_vendor_form()
            for k, v in data.items():
                self.vendor.fill_field(k, v)
            outcome = self.vendor.click_save_and_confirm(confirm=False)
            assert outcome == "Cancelled" or self.vendor.is_visible("input, button:has-text('Save')"), "Did not remain on create page after selecting No"
            return

        # 4. Search for newly created vendor
        if tc_id == "TC_VENDOR_POS_04":
            search_term = FormExecutor.last_created_vendor.get("name")
            if not search_term:
                # Ensure vendor exists
                self.vendor.open_create_vendor_form()
                full_data = self._build_vendor_data("TC_VENDOR_POS_02", {"Vendor Name": "Acme Corp"})
                self._fill_vendor_fields(full_data)
                self.vendor.click_save_and_confirm(confirm=True)
                search_term = full_data["Vendor Name"]
            self.vendor.open_vendor_list()
            found = self.vendor.is_vendor_in_list(search_term)
            assert found, f"Vendor '{search_term}' not found in vendor management list"
            return

        # 5. Inactive vendor listed with include inactive checked
        if tc_id == "TC_VENDOR_POS_09":
            self.vendor.open_vendor_list()
            self.vendor.toggle_include_inactive(True)
            assert self.vendor.is_visible("table tr, table tbody tr"), "Table has no rows when include inactive is enabled"
            return

        # 6. Standard Creation Flows (POS_02, POS_07, POS_10, POS_11)
        self.vendor.open_create_vendor_form()
        full_data = self._build_vendor_data(tc_id, data)
        self._fill_vendor_fields(full_data)

        outcome = self.vendor.click_save_and_confirm(confirm=True)
        vendor_name = full_data.get("Vendor Name", "").strip()

        # Strict positive assertions
        assert "please fill all details correctly" not in outcome.lower(), f"Vendor creation rejected with error: '{outcome}'"
        errors = self.vendor.get_validation_errors()
        assert not errors, f"Vendor creation has validation errors: {errors}"
        
        # If not yet on vendordetails and toast was not captured, wait briefly for URL redirection
        if "success" not in outcome.lower() and "vendordetails" not in self.page.url.lower():
            self.vendor.wait_for_url_contains("vendordetails", timeout=10000)

        # Verify success via explicit signals only (toast or URL redirect)
        is_success = ("success" in outcome.lower()) or ("vendordetails" in self.page.url.lower())
        assert is_success, f"Vendor creation did not succeed. Outcome: '{outcome}', URL: {self.page.url}"

        FormExecutor.last_created_vendor = {
            "name": vendor_name,
            "email": full_data.get("Email", "").strip(),
            "phone": full_data.get("Phone", "").strip(),
        }
        log.info(f"Created vendor record: {FormExecutor.last_created_vendor}")

    # ----------------- Negative Scenarios -----------------

    DEFECT_REASONS = {
        "TC_VENDOR_NEG_01": "Application accepted blank mandatory fields (Vendor Name / Country) without validation error",
        "TC_VENDOR_NEG_02": "Application accepted duplicate email address without returning conflict error",
        "TC_VENDOR_NEG_03": "Application accepted raw SQL injection payload without input rejection or sanitation",
        "TC_VENDOR_NEG_04": "Application accepted Vendor Name exceeding 100 character maximum limit",
        "TC_VENDOR_NEG_05": "Application accepted invalid email address format without validation error",
        "TC_VENDOR_NEG_06": "Application accepted alphabetic characters in phone number field",
        "TC_VENDOR_NEG_07": "Application created vendor despite dismissing confirmation popup",
        "TC_VENDOR_NEG_08": "Non-admin user was granted unauthorized access to Vendor Management",
        "TC_VENDOR_NEG_09": "Application accepted duplicate Vendor Name without validation error",
        "TC_VENDOR_NEG_10": "Application accepted numeric/special characters in name/address/state/POC fields",
        "TC_VENDOR_NEG_11": "Application accepted non-numeric characters in numeric fields (tax/phone/percentage/days)",
        "TC_VENDOR_NEG_12": "Application accepted improper email format without validation error",
        "TC_VENDOR_NEG_13": "Application failed to redirect to login on expired session during vendor creation",
        "TC_VENDOR_NEG_14": "Application failed to display network/server error when backend is unreachable",
        "TC_VENDOR_NEG_15": "Vendor created during expired session was incorrectly listed in Vendor Management table",
        "TC_VENDOR_NEG_16": "Application accepted Percentage value greater than 100% or less than 0%",
        "TC_VENDOR_NEG_17": "Application accepted negative Payment Terms (Days) value",
        "TC_VENDOR_NEG_18": "Application executed raw XSS script tag payload without input sanitation",
    }

    def _execute_negative(self, tc_id: str, data: Dict[str, str], scenario: str, steps: str, expected: str):
        # 1. Blank mandatory fields
        if tc_id == "TC_VENDOR_NEG_01":
            self.vendor.open_create_vendor_form()
            self.vendor.click_save()
            self._assert_negative_rejected(tc_id)
            return

        # 2. Duplicate email check
        if tc_id == "TC_VENDOR_NEG_02":
            # 1. First ensure a base vendor exists with target email
            self.vendor.open_create_vendor_form()
            first_data = self._build_vendor_data("TC_VENDOR_POS_02", {})
            dup_email = first_data["Email"]
            self._fill_vendor_fields(first_data)
            self.vendor.click_save_and_confirm(confirm=True)
            self.page.wait_for_timeout(1000)
            
            # 2. Now attempt to create a second vendor with the same email
            self.vendor.open_create_vendor_form()
            second_data = self._build_vendor_data(tc_id, {"Email": dup_email})
            self._fill_vendor_fields(second_data)
            save_outcome = self.vendor.click_save_and_confirm(confirm=True)
            self._assert_negative_rejected(tc_id, save_outcome=save_outcome)
            return

        # 3. Duplicate vendor name check
        if tc_id == "TC_VENDOR_NEG_09":
            # 1. First ensure a base vendor exists with target name
            self.vendor.open_create_vendor_form()
            first_data = self._build_vendor_data("TC_VENDOR_POS_02", {})
            dup_name = first_data["Vendor Name"]
            self._fill_vendor_fields(first_data)
            self.vendor.click_save_and_confirm(confirm=True)
            self.page.wait_for_timeout(1000)
            
            # 2. Now attempt to create a second vendor with the same name
            self.vendor.open_create_vendor_form()
            second_data = self._build_vendor_data(tc_id, {"Vendor Name": dup_name})
            self._fill_vendor_fields(second_data)
            save_outcome = self.vendor.click_save_and_confirm(confirm=True)
            self._assert_negative_rejected(tc_id, save_outcome=save_outcome)
            return

        # 4. Dismiss popup (Select No) negative check
        if tc_id == "TC_VENDOR_NEG_07":
            self.vendor.open_create_vendor_form()
            full_data = self._build_vendor_data(tc_id, data)
            self._fill_vendor_fields(full_data)
            outcome = self.vendor.click_save_and_confirm(confirm=False)
            assert outcome == "Cancelled" or self.vendor.is_visible("input, button:has-text('Save')"), "Did not remain on create page after selecting No"
            return

        # 5. Timeout vendor search negative check
        if tc_id == "TC_VENDOR_NEG_15":
            self.vendor.open_vendor_list()
            v_name = data.get("Vendor Name", "Timeout Vendor")
            found = self.vendor.is_vendor_in_list(v_name)
            assert not found, f"Vendor '{v_name}' from failed session was incorrectly listed in vendor table"
            return

        # 6. Non-admin access check — login as Employee and verify access is denied
        if tc_id == "TC_VENDOR_NEG_08":
            from common.pages.login_page import LoginPage
            # Open a fresh context to test as a non-admin role
            context = self.page.context.browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            emp_page = context.new_page()
            emp_page.set_default_timeout(15000)
            try:
                login_page = LoginPage(emp_page)
                login_page.login(role="Employee")
                emp_page.goto(
                    f"{login_page.base_url}/vendordetails",
                    wait_until="domcontentloaded",
                    timeout=15000,
                )
                emp_page.wait_for_timeout(2000)
                # Non-admin should be redirected away or see access denied
                url = emp_page.url.lower()
                content = emp_page.content().lower()
                access_denied = (
                    "login" in url
                    or "dashboard" in url
                    or "default" in url
                    or "unauthorized" in content
                    or "access denied" in content
                    or "permission" in content
                    or "vendordetails" not in url
                )
                assert access_denied, f"Application defect: {self.DEFECT_REASONS[tc_id]}"
                log.info(f"Non-admin access correctly denied. URL: {emp_page.url}")
            finally:
                context.close()
            return

        # 7. Session timeout check
        if tc_id == "TC_VENDOR_NEG_13":
            self.vendor.open_create_vendor_form()
            # Clear cookies to simulate expired session
            self.page.context.clear_cookies()
            self.vendor.click_save()
            self.page.wait_for_timeout(1000)
            assert "login" in self.page.url.lower() or self.vendor.is_form_invalid(), f"Application defect: {self.DEFECT_REASONS[tc_id]}"
            return

        # 8. Network offline / server unreachable check
        if tc_id == "TC_VENDOR_NEG_14":
            self.vendor.open_create_vendor_form()
            full_data = self._build_vendor_data(tc_id, data)
            self._fill_vendor_fields(full_data)
            # Simulate network disconnect
            self.page.context.set_offline(True)
            try:
                self.vendor.click_save()
                self.page.wait_for_timeout(1000)
                toast = self.vendor.get_toast(timeout=1500)
                # When offline, the record must not be saved successfully
                rejected = "success" not in toast.lower()
                assert rejected, f"Application defect: {self.DEFECT_REASONS[tc_id]}"
                log.info(f"Offline network scenario [{tc_id}] verified successfully.")
            finally:
                # Always restore network connectivity for subsequent tests
                self.page.context.set_offline(False)
            return

        # 9. Standard Negative Input Overrides
        self.vendor.open_create_vendor_form()
        full_data = self._build_vendor_data(tc_id, data)
        self._fill_vendor_fields(full_data)

        # XSS alert listener
        dialog_detected = []
        if tc_id == "TC_VENDOR_NEG_18":
            self.page.on("dialog", lambda d: dialog_detected.append(d.message))

        save_outcome = self.vendor.click_save_and_confirm(confirm=True)

        if tc_id == "TC_VENDOR_NEG_18":
            assert not dialog_detected, f"XSS payload executed browser dialog: {dialog_detected}"

        self._assert_negative_rejected(tc_id, save_outcome=save_outcome)

    def _assert_negative_rejected(self, tc_id: str, save_outcome: str = ""):
        """Assert that a negative test submission was properly rejected by the application."""
        errors = self.vendor.get_validation_errors()
        is_invalid = self.vendor.is_form_invalid()
        # Use the toast already captured during save, or try to get a fresh one
        toast = save_outcome if save_outcome else self.vendor.get_toast(timeout=3000)

        defect_msg = self.DEFECT_REASONS.get(tc_id, "Application accepted invalid vendor input without validation error")

        # If the page redirected to vendordetails, the creation SUCCEEDED — that's a defect for negative tests
        if "vendordetails" in self.page.url.lower():
            assert False, f"Application defect: {defect_msg} (redirected to vendor details page)"

        # If a success toast appeared (from save outcome or fresh capture), that's a defect
        if toast and "success" in toast.lower():
            assert False, f"Application defect: {defect_msg} (success toast displayed: '{toast}')"

        # Must have at least one explicit signal of rejection:
        #   - Form has ng-invalid CSS class
        #   - Visible validation error messages
        #   - A non-success toast/snackbar was shown
        has_error_toast = bool(toast) and "success" not in toast.lower()
        rejected = is_invalid or bool(errors) or has_error_toast

        assert rejected, f"Application defect: {defect_msg} (no validation errors, no invalid form state, no error toast)"
        log.info(f"Negative scenario [{tc_id}] correctly rejected. Errors: {errors}, Toast: '{toast}', FormInvalid: {is_invalid}")

    # ----------------- Helpers -----------------

    FIELD_NORM_MAP = {
        "percentage": "TDS Percentage (%)",
        "tds percentage": "TDS Percentage (%)",
        "days": "Payment Terms (Days)",
        "payment terms": "Payment Terms (Days)",
        "payment terms (days)": "Payment Terms (Days)",
        "tax number": "Tax Number",
        "vendor tax number": "Tax Number",
        "vendor name": "Vendor Name",
        "vendor address": "Address",
        "address": "Address",
        "vendor state": "State",
        "state": "State",
        "vendor phone": "Phone",
        "phone": "Phone",
        "vendor email": "Email",
        "email": "Email",
        "vendor poc": "POC",
        "poc": "POC",
        "country": "Country",
    }

    def _parse_test_data(self, raw_data: Any) -> Dict[str, str]:
        if not raw_data or str(raw_data).strip() in ("None", "N/A", "Fetch from excel"):
            return {}
        result = {}
        for line in str(raw_data).split("\n"):
            line = line.strip()
            if ":" in line:
                key, val = line.split(":", 1)
                clean_val = val.strip().strip("'\"")
                result[key.strip()] = clean_val
        return result

    def _build_vendor_data(self, tc_id: str, overrides: Dict[str, str]) -> Dict[str, str]:
        ts = int(time.time() * 1000) % 1000000
        num = re.search(r"(\d+)$", tc_id).group(1) if re.search(r"(\d+)$", tc_id) else "01"
        is_pos = "POS" in tc_id
        default_phone = f"98{ts%100000000:08d}"
        
        data = {
            "Vendor Name": f"AutoVendor_{num}_{ts}",
            "Country": "India",
            "State": "Maharashtra",
            "Email": f"vendor_{num}_{ts}@example.com",
            "Phone": default_phone,
            "Address": "123 Tech Park",
            "POC": "John Doe",
            "TDS Percentage (%)": "10",
            "Tax Number": "TAX12345",
            "Active": "Ticked",
            "Payment Terms (Days)": "30",
        }

        # Normalize override keys
        normalized_overrides = {}
        for k, v in overrides.items():
            norm_key = self.FIELD_NORM_MAP.get(k.strip().lower(), k.strip())
            normalized_overrides[norm_key] = v

        for k, v in normalized_overrides.items():
            key_lower = k.lower()
            if "100 times" in str(v).lower() or ("exceed" in str(v).lower() and len(str(v)) > 50):
                v = "A" * 120
            elif is_pos and "vendor name" in key_lower:
                clean_name = v.strip().replace("'", "")
                if "space corp" in clean_name.lower():
                    v = f"   SpaceCorp_{ts}   "
                else:
                    v = f"{clean_name}_{ts}"
            elif is_pos and "email" in key_lower:
                v = f"vendor_{num}_{ts}@example.com"
            elif "phone" in key_lower:
                # If this test specifically tests invalid phone (NEG_06), keep the invalid phone
                if tc_id == "TC_VENDOR_NEG_06":
                    pass
                else:
                    # Clean or use valid 10-digit Indian phone so unrelated phone format errors don't mask defects
                    digits = re.sub(r"\D", "", str(v))
                    if len(digits) == 10 and digits[0] in "6789":
                        v = digits
                    elif len(digits) >= 10 and digits[-10] in "6789":
                        v = digits[-10:]
                    else:
                        v = default_phone
            elif "country" in key_lower and not is_pos:
                # If country is blank (e.g. NEG_01), keep blank; otherwise use India for clean select
                if str(v).strip() != "":
                    v = "India"
            data[k] = v

        # Specific adjustments for defect tests:
        # NEG_10: Test non-alphabetic in name, address, state with valid POC and phone to expose backend defect
        if tc_id == "TC_VENDOR_NEG_10":
            data["Vendor Name"] = "213232saadadads"
            data["Address"] = "3232131eqeq"
            data["State"] = "sdda223213"
            data["POC"] = "sadasd"
            data["Phone"] = default_phone

        # NEG_11: Test non-numeric in payment terms days and tax number with valid phone and valid percentage to expose backend defect
        if tc_id == "TC_VENDOR_NEG_11":
            data["Tax Number"] = "weqweqe1212312"
            data["Payment Terms (Days)"] = "wqww212eqwqeq"
            data["TDS Percentage (%)"] = "10"
            data["Phone"] = default_phone

        return data

    def _fill_vendor_fields(self, data: Dict[str, str]):
        failed_fields = []
        for field, value in data.items():
            success = self.vendor.fill_field(field, value)
            if not success:
                failed_fields.append(field)
        if failed_fields:
            log.warning(f"Failed to fill fields: {failed_fields}")
            # Fail the test if critical fields (Vendor Name, Country) couldn't be filled
            critical_fields = {f for f in failed_fields if f.lower() in ("vendor name", "name", "country")}
            if critical_fields:
                raise AssertionError(f"Could not fill critical form fields: {critical_fields}. Test data cannot be applied.")
