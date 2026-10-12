import os
import re
import time
from typing import Any, Dict, List, Optional

from playwright.sync_api import Page

from emp_pages.employee_page import EmployeePage
from emp_utils.excel_reader import is_ui_case
from shared.utils.logger import get_logger

log = get_logger("FormExecutor")

METADATA_KEYS = {
    "test case id", "tc id", "tc_id", "scenario", "test scenario",
    "pre-condition", "pre condition", "test steps", "steps",
    "expected result", "expected results", "automation status",
    "execution type", "test status", "remarks / defect observed",
    "remarks", "defect", "test data", "data", "_sheet", "auto_id",
    "module", "comments", "description"
}


def parse_test_data(data_str: Any) -> Dict[str, str]:
    """Parse key-value test data from the workbook or return dict if already structured."""
    if isinstance(data_str, dict):
        return {
            str(k).strip(): (str(v) if v is not None and str(v).lower() != "none" else "")
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
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def get_baseline_employee() -> Dict[str, str]:
    """Fetch baseline valid employee test data dynamically from Swarajya-test-data.xlsx."""
    try:
        from shared.utils.excel_loader import load_test_data_sheet
        data_map = load_test_data_sheet("createemp-mgmt")
        for tc_id, row in data_map.items():
            if "POS" in tc_id.upper() and row.get("First Name") and row.get("Mobile Number"):
                res = {}
                for k, v in row.items():
                    val = str(v).strip() if v is not None else ""
                    if val.endswith(".0") and val[:-2].isdigit():
                        val = val[:-2]
                    res[k] = val
                return res
    except Exception as exc:
        log.warning(f"Could not load baseline employee from Excel: {exc}")
    return {}


class FormExecutor:
    """Executes Employee Management test cases from Excel steps and test data."""

    last_created_employee: Dict[str, str] = {}

    def __init__(self, page: Page):
        self.page = page
        self.emp = EmployeePage(page)

    def execute_test_case(self, tc: Dict[str, Any], is_positive: bool = True):
        if not is_ui_case(tc):
            raise AssertionError("This workbook row is marked API and must not be run as a UI test.")

        tc_id = tc.get("Test Case ID", "")
        scenario = tc.get("Scenario", "")
        steps = tc.get("Steps", "")
        excel_data = tc.get("data") or {}
        parsed_inline = parse_test_data(tc.get("Test Data", ""))
        clean_excel = {
            k.strip(): (str(v)[:-2] if str(v).endswith(".0") and str(v)[:-2].isdigit() else str(v).strip())
            for k, v in excel_data.items()
            if v is not None and str(v).strip()
            and k.strip().lower() not in METADATA_KEYS
            and not k.strip().lower().startswith("col_")
        }
        data = {**clean_excel, **parsed_inline}
        expected = tc.get("Expected Result", "")

        log.info(f"==================== [{tc_id}] {scenario} ====================")
        log.info(f"Excel steps: {steps}")
        log.info(f"Excel expected result: {expected}")
        log.info(f"Mapped form input data: {data}")

        if is_positive:
            self._execute_positive_case(tc_id, data, expected)
        else:
            self._execute_negative_case(tc_id, data, expected)

    def _execute_positive_case(self, tc_id: str, data: Dict[str, str], expected: str = ""):
        self.emp.open_create_employee_form()

        if tc_id == "TC_POS_EMP_008":
            self._verify_last_created_employee()
            return

        if tc_id == "TC_POS_EMP_010":
            for field_name, value in data.items():
                clean_k = re.sub(r"[\*:]", "", str(field_name)).strip()
                if clean_k.lower() not in METADATA_KEYS and not clean_k.lower().startswith("col_"):
                    self.emp.fill_field(field_name, value)
            assert self.emp.click_cancel(), "Cancel/Reset did not clear the form or navigate away"
            return

        full_data = self._build_valid_employee_data(tc_id, data, mandatory_only=False)
        self._fill_fields(full_data)

        outcome = self.emp.click_save_and_confirm()
        first_name = full_data.get("First Name", "").strip()
        last_name = full_data.get("Last Name", "").strip()

        # Validate UI outcome before asserting failure
        errors = self.emp.get_validation_errors()
        confirm_msg = outcome.get("message") or self.emp.get_confirmation_message(timeout=2000)
        is_invalid = self.emp.is_form_invalid()
        url = self.page.url

        record = self.emp.search_employee_in_list(first_name, last_name)
        is_success = (
            record is not None
            or "successfully" in confirm_msg.lower()
            or "employeelist" in url.lower()
        )

        if not is_success:
            raise AssertionError(
                f"Validation Failure [{tc_id}]: Expected '{expected or 'Employee record created successfully'}', "
                f"but employee was not created. Form validation errors: {errors}, "
                f"Confirmation message: '{confirm_msg}', Form invalid: {is_invalid}, Page URL: {url}"
            )

        if record:
            FormExecutor.last_created_employee = {
                "first_name": first_name,
                "last_name": last_name,
                "email": full_data.get("Official Email", "").strip(),
                "employee_id": record.get("employee_id", ""),
            }
        log.info(f"Save outcome for {tc_id}: {outcome}")

    def _execute_negative_case(self, tc_id: str, data: Dict[str, str], expected: str = ""):
        self.emp.open_create_employee_form()

        if tc_id == "TC_NEG_EMP_001":
            self.emp.click_save()
            self._assert_submission_rejected(tc_id, expected)
            return

        if tc_id == "TC_NEG_EMP_015":
            self._assert_dropdown_options_are_text()
            return

        if tc_id == "TC_NEG_EMP_016":
            self._assert_new_employee_not_manager_option()
            return

        if tc_id == "TC_NEG_EMP_018":
            self._assert_session_timeout_blocks_save(tc_id, expected)
            return

        if tc_id == "TC_NEG_EMP_013":
            # Verify InvalidID_999 cannot be selected from dropdown options
            options = self.emp.get_dropdown_options("department")
            assert "InvalidID_999" not in options, "Dropdown unexpectedly contains invalid option 'InvalidID_999'"
            full_data = self._build_valid_employee_data(tc_id, {}, mandatory_only=False)
            if "Department" in full_data:
                del full_data["Department"]
            self._fill_fields(full_data)
            self.emp.click_save_and_confirm()
            errors = self.emp.get_validation_errors()
            has_dept_err = any("department" in err.lower() for err in errors)
            if not has_dept_err:
                raise AssertionError(
                    "Validation Failure [TC_NEG_EMP_013]: Form failed to display mandatory Department validation error message upon submission"
                )
            return

        full_data = self._build_valid_employee_data(tc_id, {}, mandatory_only=False)
        for field_name, value in data.items():
            self._apply_negative_override(full_data, field_name, value)

        # For duplicate test cases (008, 009, 019), ensure we attempt duplicate submission from Excel data
        if tc_id == "TC_NEG_EMP_008":
            full_data["Personal Email"] = data.get("Personal Email") or "existing.email@example.com"
        elif tc_id == "TC_NEG_EMP_009":
            mob_val = str(data.get("Mobile Number", "9876543210"))
            digits = re.sub(r"\D", "", mob_val)
            full_data["Mobile Number"] = digits[:10] if len(digits) >= 10 else "9876543210"
        elif tc_id == "TC_NEG_EMP_019":
            full_data["Official Email"] = data.get("Official Email") or "existing@company.com"

        self._fill_fields(full_data)

        dialog_messages = []
        if tc_id == "TC_NEG_EMP_014":
            self.page.on("dialog", lambda dialog: dialog_messages.append(dialog.message))

        self.emp.click_save_and_confirm()
        if tc_id == "TC_NEG_EMP_014":
            assert not dialog_messages, f"XSS payload executed a browser dialog: {dialog_messages}"

        self._assert_submission_rejected(tc_id, expected)

    def _build_valid_employee_data(self, tc_id: str, overrides: Dict[str, str], mandatory_only: bool) -> Dict[str, str]:
        # Fetch baseline employee directly from Excel (0 hardcoded values)
        data = dict(get_baseline_employee())
        for k in ("Department", "Designation", "Reporting Manager", "Role"):
            if k not in data or not data[k]:
                data[k] = "Select from given options"

        for field_name, value in overrides.items():
            clean_name = re.sub(r"[\*:]", "", str(field_name)).strip()
            if clean_name.lower() in METADATA_KEYS or clean_name.lower().startswith("col_"):
                continue
            lowered_key = clean_name.lower()
            lowered_value = str(value).lower()
            if "valid data for all mandatory" in lowered_key:
                continue
            if "first name and last name" in lowered_key:
                continue
            if "50 characters" in lowered_value:
                value = "A" * 50 if "first" in lowered_key else "B" * 50
            data[clean_name] = value

        if mandatory_only:
            allowed = {
                "First Name",
                "Last Name",
                "Gender",
                "Date of Birth",
                "Personal Email",
                "Mobile Number",
                "Joining Date",
                "Department",
                "Designation",
                "Reporting Manager",
                "Role",
                "Official Email",
            }
            data = {key: value for key, value in data.items() if key in allowed}

        return data

    def _apply_negative_override(self, full_data: Dict[str, str], field_name: str, value: str) -> None:
        key = re.sub(r"[\*:]", "", str(field_name)).strip()
        lowered_key = key.lower()
        if lowered_key in METADATA_KEYS or lowered_key.startswith("col_"):
            return
        lowered_value = str(value).lower()

        if "other mandatory fields" in lowered_key:
            return
        if "one mandatory field" in lowered_key:
            full_data["Last Name"] = ""
            return

        if "51+ characters" in lowered_value:
            value = "A" * 51
        elif "98765abcde" in lowered_value:
            value = "98765abcde"
        elif "111222 or kumar@!" in lowered_value:
            value = "111222"
        elif "invalid" in lowered_value and ("link" in lowered_value or "email" in lowered_value):
            value = "invalid.email"
        elif "(existing)" in lowered_value:
            value = value.split("(", 1)[0].strip()

        full_data[key] = _strip_outer_quotes(str(value))

    def _fill_fields(self, data: Dict[str, str]) -> Dict[str, bool]:
        results = {}
        for field_name, value in data.items():
            clean_name = re.sub(r"[\*:]", "", str(field_name)).strip()
            if clean_name.lower() in METADATA_KEYS or clean_name.lower().startswith("col_"):
                continue
            ok = self.emp.fill_field(clean_name, value)
            results[clean_name] = ok
        return results

    def _validate_dropdowns(self, dropdowns):
        for dropdown in dropdowns:
            options = self.emp.validate_all_options_for_dropdown(dropdown)
            assert options, f"Dropdown '{dropdown}' options could not be selected"

    def _verify_last_created_employee(self) -> None:
        created = FormExecutor.last_created_employee
        if not created:
            self.emp.navigate_to_employee_list()
            res = self.emp.search_employee_in_list("Auto")
            assert res and res.get("employee_id"), "Could not find an employee with ID in the list"
            return
        record = self.emp.search_employee_in_list(created["first_name"], created["last_name"])
        assert record, "Newly created employee is not displayed in the employee list"
        assert record.get("employee_id"), "Employee list did not display a unique Employee ID"

    DEFECT_REASONS = {
        "TC_NEG_EMP_001": "Application failed to validate blank mandatory fields",
        "TC_NEG_EMP_002": "Application accepted numeric/special characters in name fields without validation error",
        "TC_NEG_EMP_003": "Application accepted invalid mobile number (<10 digits) without validation error",
        "TC_NEG_EMP_004": "Application accepted improperly formatted email address without validation error",
        "TC_NEG_EMP_005": "Application accepted underage Date of Birth (01-01-2025) without validation error",
        "TC_NEG_EMP_006": "Application accepted Joining Date prior to Date of Birth without validation error",
        "TC_NEG_EMP_008": "Application accepted duplicate Personal Email without returning validation error or 409",
        "TC_NEG_EMP_009": "Application accepted duplicate Mobile Number without returning validation error or 409",
        "TC_NEG_EMP_010": "Application accepted name exceeding maximum 50 character limit without displaying validation error",
        "TC_NEG_EMP_011": "Application accepted raw SQL injection payload in name field without validation error",
        "TC_NEG_EMP_012": "Application accepted future Date of Birth (01-01-2050) without validation error",
        "TC_NEG_EMP_013": "Application accepted invalid Department selection without validation error",
        "TC_NEG_EMP_014": "Application accepted raw XSS script tags in name field without input rejection",
        "TC_NEG_EMP_015": "Application dropdown options contain numeric values/IDs violating text-only requirement",
        "TC_NEG_EMP_016": "Newly added non-manager employee unexpectedly appears in Reporting Manager dropdown",
        "TC_NEG_EMP_017": "Application accepted whitespace-only mandatory fields without validation error",
        "TC_NEG_EMP_018": "Application failed to block submission on expired user session",
        "TC_NEG_EMP_019": "Application accepted duplicate Official Email without returning validation error or 409",
    }

    def _assert_submission_rejected(self, tc_id: str, expected: str = "") -> None:
        errors = self.emp.get_validation_errors()
        is_invalid = self.emp.is_form_invalid()
        success_msg = self.emp.get_confirmation_message(timeout=1500)
        url = self.page.url

        # Check if Save button is disabled
        save_disabled = False
        try:
            save_btn = self.page.locator(self.emp.SAVE_BTN).first
            save_disabled = not save_btn.is_enabled()
        except Exception:
            pass

        # A negative scenario is legitimately rejected if:
        # 1. No success message was received AND
        # 2. Form or fields are marked invalid, OR validation errors are shown, OR toast indicates rejection, OR save button disabled, OR remained on create form without creation
        no_success = "successfully" not in success_msg.lower() and "added" not in success_msg.lower()
        has_errors = bool(errors) or is_invalid
        has_error_toast = any(w in success_msg.lower() for w in ("error", "invalid", "already exists", "failed", "required", "please fill"))

        rejected = no_success and (has_errors or has_error_toast or save_disabled)

        if not rejected:
            defect_msg = self.DEFECT_REASONS.get(
                tc_id, "Application accepted invalid data without displaying validation error"
            )
            raise AssertionError(
                f"Validation Failure [{tc_id}]: Expected negative validation rejection ('{expected}'), "
                f"but {defect_msg}. Form errors: {errors}, Confirmation/Toast: '{success_msg}', "
                f"Form invalid: {is_invalid}, Save button disabled: {save_disabled}, Page URL: {url}"
            )
        log.info(f"Negative scenario [{tc_id}] validated and properly rejected. Errors: {errors}, Message: '{success_msg}'")

    def _assert_dropdown_options_are_text(self) -> None:
        for dropdown in ["department", "designation", "reporting manager", "role"]:
            options = self.emp.get_dropdown_options(dropdown)
            assert options, f"No options found for dropdown '{dropdown}'"
            for option in options:
                clean_opt = option.strip()
                if any(ch.isdigit() for ch in clean_opt):
                    raise AssertionError(
                        f"Application defect: Dropdown '{dropdown}' contains numeric value/ID: '{option}' violating text-only requirement"
                    )

    def _assert_new_employee_not_manager_option(self) -> None:
        created = FormExecutor.last_created_employee
        first = created.get("first_name", "Auto") if created else "Auto"
        last = created.get("last_name", "Employee") if created else "Employee"
        full_name = f"{first} {last}".lower()
        options = [option.lower() for option in self.emp.get_dropdown_options("reporting manager")]
        # Newly created employee should not be listed as reporting manager
        found = any(full_name in opt or "auto" in opt for opt in options)
        if found:
            raise AssertionError(
                f"Application defect: Newly added employee ('{full_name}') unexpectedly appears in Reporting Manager dropdown"
            )

    def _assert_session_timeout_blocks_save(self, tc_id: str) -> None:
        full_data = self._build_valid_employee_data(tc_id, {}, mandatory_only=False)
        self._fill_fields(full_data)
        self.page.context.clear_cookies()
        try:
            self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
        except Exception:
            pass
        self.emp.click_save_and_confirm()
        body = self.page.locator("body").inner_text().lower()
        url = self.page.url.lower()
        success_msg = self.emp.get_confirmation_message(timeout=1000)
        blocked = ("login" in url or "unauthorized" in body or "session" in body or "timeout" in body or "addnewemployee" in url) and ("successfully" not in success_msg.lower())

        assert blocked, "Expired session did not block saving the Create Employee form"
        log.info(f"Negative scenario [{tc_id}] session timeout blocked save as expected.")

