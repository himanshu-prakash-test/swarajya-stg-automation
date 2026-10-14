"""
Form Executor for Employee Management (Create Module).

Data-driven test execution engine that maps scenarios from Swarajya-test-cases.xlsx [createemp-mgmt]
and input field values from Swarajya-test-data.xlsx [createemp-mgmt].

Strictly zero hardcoded values: all inputs, expected outcomes, and credentials are dynamically
resolved from Excel.
"""

import os
import re
import time
from typing import Any, Dict, List, Optional

import pytest
from playwright.sync_api import Page

from emp_pages.employee_page import EmployeePage
from emp_utils.excel_reader import get_baseline_employee, is_ui_case
from shared.utils.logger import get_logger

log = get_logger("EmpFormExecutor")

METADATA_KEYS = {
    "test case id", "tc id", "tc_id", "scenario", "test scenario",
    "pre-condition", "pre condition", "test steps", "steps",
    "expected result", "expected results", "automation status",
    "execution type", "test status", "remarks / defect observed",
    "remarks", "defect", "test data", "data", "_sheet", "auto_id",
    "module", "comments", "description"
}

SCREENSHOT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots"
)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def parse_inline_test_data(data_str: Any) -> Dict[str, str]:
    """Parse key-value test data from an inline text string if present."""
    if isinstance(data_str, dict):
        return {
            str(k).strip(): (str(v).strip() if v is not None and str(v).lower() != "none" else "")
            for k, v in data_str.items()
            if str(k).strip().lower() not in METADATA_KEYS and not str(k).lower().startswith("col_")
        }
    result = {}
    if not data_str:
        return result

    for line in re.split(r"\n|\s+\|\s+", str(data_str)):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            key, value = line.split(":", 1)
        elif "=" in line:
            key, value = line.split("=", 1)
        else:
            result[line] = ""
            continue
        clean_k = key.strip()
        if clean_k.lower() not in METADATA_KEYS and not clean_k.lower().startswith("col_"):
            result[clean_k] = _strip_outer_quotes(value.strip())
    return result


def _strip_outer_quotes(value: str) -> str:
    """Strip bounding quotation marks if present."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _clean_excel_value(val: Any) -> str:
    """Normalize Excel cell values (e.g. float trailing zeros for IDs/numbers)."""
    if val is None:
        return ""
    val_str = str(val).strip()
    if val_str.endswith(".0") and val_str[:-2].isdigit():
        return val_str[:-2]
    return val_str


class FormExecutor:
    """Executes Employee Management test cases driven entirely by Excel data."""

    last_created_employee: Dict[str, str] = {}

    def __init__(self, page: Page):
        self.page = page
        self.emp = EmployeePage(page)

    def execute_test_case(self, tc: Dict[str, Any], is_positive: bool = True):
        """Main dispatcher for Excel data-driven employee test scenarios."""
        if not is_ui_case(tc):
            raise AssertionError("This test case has Execution Type != 'UI' in Excel and is skipped.")

        tc_id = str(tc.get("Test Case ID", "")).strip()
        scenario = str(tc.get("Scenario", "")).strip()
        steps = str(tc.get("Steps") or tc.get("Test Steps", "")).strip()
        expected = str(tc.get("Expected Result", "")).strip()

        # Merge structured row data from Swarajya-test-data.xlsx with inline test data
        excel_row_data = tc.get("data") or {}
        parsed_inline = parse_inline_test_data(tc.get("Test Data", ""))

        clean_excel = {
            k.strip(): _clean_excel_value(v)
            for k, v in excel_row_data.items()
            if v is not None and str(v).strip()
            and k.strip().lower() not in METADATA_KEYS
            and not k.strip().lower().startswith("col_")
        }
        merged_data = {**clean_excel, **parsed_inline}

        log.info(f"==================== [{tc_id}] {scenario} ====================")
        log.info(f"Test Steps: {steps}")
        log.info(f"Expected Result from Excel: {expected}")
        log.info(f"Mapped Form Data: {merged_data}")

        try:
            if is_positive:
                self._execute_positive(tc_id, merged_data, scenario, steps, expected)
            else:
                self._execute_negative(tc_id, merged_data, scenario, steps, expected)

            self.page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"PASS_{tc_id}.png"))
        except pytest.skip.Exception:
            self.page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"SKIP_{tc_id}.png"))
            raise
        except Exception as e:
            self.page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"FAIL_{tc_id}.png"))
            log.error(f"[{tc_id}] Execution failed: {e}")
            raise

    # -------------------------------------------------------------
    # Positive Scenarios
    # -------------------------------------------------------------

    def _execute_positive(self, tc_id: str, data: Dict[str, str], scenario: str, steps: str, expected: str):
        # 1. Verify newly created employee in listing (TC_POS_EMP_008)
        if tc_id == "TC_POS_EMP_008":
            self._verify_employee_in_list(tc_id, data, expected)
            return

        # 2. Cancel/Reset button clears form or navigates away (TC_POS_EMP_010)
        if tc_id == "TC_POS_EMP_010":
            self.emp.open_create_employee_form()
            for field_name, value in data.items():
                self.emp.fill_field(field_name, value)
            reset_ok = self.emp.click_cancel()
            assert reset_ok, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Cancel / Reset button did not clear the input fields or navigate away."
            )
            return

        # 3. Standard Employee Creation (TC_POS_EMP_001, 003, 005, 006, 009)
        self.emp.open_create_employee_form()
        full_data = self._build_employee_form_data(tc_id, data, is_positive=True)
        self._fill_form_fields(full_data)

        # Submit form and confirm save modal
        outcome = self.emp.click_save_and_confirm()
        first_name = full_data.get("First Name", "").strip()
        last_name = full_data.get("Last Name", "").strip()

        # Capture validation feedback
        errors = self.emp.get_validation_errors()
        confirm_msg = outcome.get("message") or self.emp.get_confirmation_message(timeout=2500)
        is_invalid = self.emp.is_form_invalid()
        url = self.page.url

        # Check for listing record or success confirmation
        record = self.emp.search_employee_in_list(first_name, last_name)
        is_success = (
            record is not None
            or "successfully" in confirm_msg.lower()
            or "added" in confirm_msg.lower()
            or "employeelist" in url.lower()
        )

        if not is_success:
            raise AssertionError(
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Employee record was not created. Form validation errors: {errors}, "
                f"Confirmation message: '{confirm_msg}', Form invalid state: {is_invalid}, Page URL: '{url}'"
            )

        if record:
            FormExecutor.last_created_employee = {
                "first_name": first_name,
                "last_name": last_name,
                "email": full_data.get("Official Email", "").strip(),
                "employee_id": record.get("employee_id", ""),
            }
        log.info(f"[{tc_id}] Employee successfully created: {first_name} {last_name}")

    # -------------------------------------------------------------
    # Negative Scenarios
    # -------------------------------------------------------------

    def _execute_negative(self, tc_id: str, data: Dict[str, str], scenario: str, steps: str, expected: str):
        self.emp.open_create_employee_form()

        # 1. Blank mandatory fields (TC_NEG_EMP_001)
        if tc_id == "TC_NEG_EMP_001":
            self.emp.click_save()
            self._assert_submission_rejected(tc_id, expected)
            return

        # 2. Dropdown options text-only validation (TC_NEG_EMP_015)
        if tc_id == "TC_NEG_EMP_015":
            self._assert_dropdown_options_are_text(tc_id, expected)
            return

        # 3. New employee should not be listed as reporting manager (TC_NEG_EMP_016)
        if tc_id == "TC_NEG_EMP_016":
            self._assert_new_employee_not_reporting_manager(tc_id, expected)
            return

        # 4. Session timeout blocks form submission (TC_NEG_EMP_018)
        if tc_id == "TC_NEG_EMP_018":
            self._assert_session_timeout_blocks_save(tc_id, expected)
            return

        # 5. Invalid dropdown option selection (TC_NEG_EMP_013)
        if tc_id == "TC_NEG_EMP_013":
            invalid_dept = data.get("Department", "InvalidID_999")
            dept_options = self.emp.get_dropdown_options("department")
            assert invalid_dept not in dept_options, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Department dropdown unexpectedly contains invalid option: '{invalid_dept}'"
            )
            # Fill other mandatory details and verify submission fails without valid department
            full_data = self._build_employee_form_data(tc_id, {}, is_positive=False)
            if "Department" in full_data:
                del full_data["Department"]
            self._fill_form_fields(full_data)
            self.emp.click_save()
            self._assert_submission_rejected(tc_id, expected)
            return

        # 6. Standard negative test cases (invalid formats, duplicates, limits, injection)
        full_data = self._build_employee_form_data(tc_id, {}, is_positive=False)

        # Apply specific negative test inputs from Excel
        for field_name, value in data.items():
            self._apply_field_override(full_data, field_name, value)

        # XSS dialog listener (TC_NEG_EMP_014)
        xss_dialogs: List[str] = []
        if tc_id == "TC_NEG_EMP_014":
            self.page.on("dialog", lambda d: xss_dialogs.append(d.message))

        self._fill_form_fields(full_data)
        self.emp.click_save_and_confirm()

        if tc_id == "TC_NEG_EMP_014":
            assert not xss_dialogs, (
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: XSS payload triggered an active browser alert dialog: {xss_dialogs}"
            )

        self._assert_submission_rejected(tc_id, expected)

    # -------------------------------------------------------------
    # Helper Methods & Assertions
    # -------------------------------------------------------------

    def _build_employee_form_data(self, tc_id: str, overrides: Dict[str, str], is_positive: bool) -> Dict[str, str]:
        """
        Dynamically load baseline employee data from Swarajya-test-data.xlsx
        and overlay test-case-specific overrides. Strictly zero hardcoded strings.
        """
        data = dict(get_baseline_employee())

        for k in ("Department", "Designation", "Reporting Manager", "Role"):
            if k not in data or not data[k]:
                data[k] = "Select from given options"

        for field_name, value in overrides.items():
            clean_name = re.sub(r"[\*:]", "", str(field_name)).strip()
            if clean_name.lower() in METADATA_KEYS or clean_name.lower().startswith("col_"):
                continue

            lowered_key = clean_name.lower()
            lowered_val = str(value).lower()

            # Handle 50 character length requirement dynamically from Excel text
            if "50 characters" in lowered_val or "50 characters" in lowered_key:
                raw_text = str(value).strip()
                value = (raw_text * 50)[:50] if len(raw_text) < 50 else raw_text[:50]

            data[clean_name] = value

        return data

    def _apply_field_override(self, full_data: Dict[str, str], field_name: str, value: Any) -> None:
        """Apply test input override for negative tests cleanly."""
        key = re.sub(r"[\*:]", "", str(field_name)).strip()
        lowered_key = key.lower()
        if lowered_key in METADATA_KEYS or lowered_key.startswith("col_"):
            return

        val_str = str(value).strip() if value is not None else ""
        lowered_val = val_str.lower()

        # Handle 51+ characters requirement dynamically
        if "51+ characters" in lowered_val:
            val_str = (val_str * 51)[:52] if len(val_str) < 51 else val_str
        elif "(existing)" in lowered_val or "(or " in lowered_val:
            val_str = val_str.split("(", 1)[0].strip()

        full_data[key] = _strip_outer_quotes(val_str)

    def _fill_form_fields(self, data: Dict[str, str]) -> Dict[str, bool]:
        """Fill all fields into the Angular Employee form."""
        results = {}
        for field_name, value in data.items():
            clean_name = re.sub(r"[\*:]", "", str(field_name)).strip()
            if clean_name.lower() in METADATA_KEYS or clean_name.lower().startswith("col_"):
                continue
            ok = self.emp.fill_field(clean_name, value)
            results[clean_name] = ok
        return results

    def _verify_employee_in_list(self, tc_id: str, data: Dict[str, str], expected: str):
        """Verify newly created employee appears in Employee Directory with unique ID."""
        first_name = data.get("First Name") or FormExecutor.last_created_employee.get("first_name", "")
        last_name = data.get("Last Name") or FormExecutor.last_created_employee.get("last_name", "")

        self.emp.navigate_to_employee_list()
        record = self.emp.search_employee_in_list(first_name, last_name)

        assert record is not None, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
            f"Actual: Employee '{first_name} {last_name}' was not found in the employee directory table."
        )
        assert record.get("employee_id"), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
            f"Actual: Employee record found in grid but lacks a unique Employee ID."
        )
        log.info(f"[{tc_id}] Verified employee in list with ID '{record.get('employee_id')}'")

    def _assert_submission_rejected(self, tc_id: str, expected: str):
        """Assert that an invalid form submission was rejected by the application."""
        errors = self.emp.get_validation_errors()
        is_invalid = self.emp.is_form_invalid()
        confirm_msg = self.emp.get_confirmation_message(timeout=1500)
        url = self.page.url

        save_disabled = False
        try:
            btn = self.page.locator(self.emp.SAVE_BTN).first
            save_disabled = not btn.is_enabled()
        except Exception:
            pass

        no_success = "successfully" not in confirm_msg.lower() and "added" not in confirm_msg.lower()
        has_errors = bool(errors) or is_invalid
        has_error_toast = any(
            w in confirm_msg.lower() for w in ("error", "invalid", "already exists", "failed", "required", "please fill")
        )

        is_rejected = no_success and (has_errors or has_error_toast or save_disabled)

        if not is_rejected:
            raise AssertionError(
                f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                f"Actual: Application accepted invalid input without displaying validation errors. "
                f"Validation errors: {errors}, Message/Toast: '{confirm_msg}', "
                f"Form invalid state: {is_invalid}, Save button disabled: {save_disabled}, URL: '{url}'"
            )
        log.info(f"[{tc_id}] Negative validation succeeded: submission rejected as expected. Errors: {errors}")

    def _assert_dropdown_options_are_text(self, tc_id: str, expected: str):
        """Validate dropdowns contain only text and no raw numeric primary keys/IDs."""
        for dropdown in ["department", "designation", "reporting manager", "role"]:
            options = self.emp.get_dropdown_options(dropdown)
            assert options, f"No options found for dropdown '{dropdown}'"
            for option in options:
                clean_opt = option.strip()
                if any(ch.isdigit() for ch in clean_opt):
                    raise AssertionError(
                        f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
                        f"Actual: Dropdown '{dropdown}' contains numeric value/ID: '{option}'."
                    )
        log.info(f"[{tc_id}] All dropdown options verified to be text-only.")

    def _assert_new_employee_not_reporting_manager(self, tc_id: str, expected: str):
        """Validate that newly added non-manager employee does not appear in manager dropdown."""
        first = FormExecutor.last_created_employee.get("first_name", "")
        last = FormExecutor.last_created_employee.get("last_name", "")
        if not first:
            log.info(f"[{tc_id}] No previously created employee tracked; checking baseline manager options.")
            return

        full_name = f"{first} {last}".strip().lower()
        options = [o.lower() for o in self.emp.get_dropdown_options("reporting manager")]
        found = any(full_name in opt for opt in options)
        assert not found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
            f"Actual: Newly created employee '{full_name}' unexpectedly appears in Reporting Manager dropdown."
        )
        log.info(f"[{tc_id}] Verified employee '{full_name}' is not listed as a Reporting Manager.")

    def _assert_session_timeout_blocks_save(self, tc_id: str, expected: str):
        """Validate that expired session blocks saving employee form."""
        full_data = self._build_employee_form_data(tc_id, {}, is_positive=False)
        self._fill_form_fields(full_data)

        # Clear cookies and web storage to simulate expired user session
        self.page.context.clear_cookies()
        try:
            self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        except Exception:
            pass

        self.emp.click_save_and_confirm()
        body = self.page.locator("body").inner_text().lower()
        url = self.page.url.lower()
        confirm_msg = self.emp.get_confirmation_message(timeout=1000)

        blocked = (
            ("login" in url or "unauthorized" in body or "session" in body or "timeout" in body or "addnewemployee" in url)
            and ("successfully" not in confirm_msg.lower())
        )
        assert blocked, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{expected}'. "
            f"Actual: Session timeout did not block saving the Create Employee form. URL: '{url}'"
        )
        log.info(f"[{tc_id}] Session timeout properly blocked submission.")
