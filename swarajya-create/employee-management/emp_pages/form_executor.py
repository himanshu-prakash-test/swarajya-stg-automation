import re
from typing import Any, Dict

from playwright.sync_api import Page

from emp_pages.employee_page import EmployeePage
from emp_utils.excel_reader import is_ui_case
from emp_utils.logger import get_logger

log = get_logger("FormExecutor")


def parse_test_data(data_str: str) -> Dict[str, str]:
    """Parse key-value test data from the workbook."""
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
        result[key.strip()] = _strip_outer_quotes(value.strip())
    return result


def _strip_outer_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


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
        data = parse_test_data(tc.get("Test Data", ""))
        expected = tc.get("Expected Result", "")

        log.info(f"==================== [{tc_id}] {scenario} ====================")
        log.info(f"Excel steps: {steps}")
        log.info(f"Excel expected result: {expected}")

        if is_positive:
            self._execute_positive_case(tc_id, data)
        else:
            self._execute_negative_case(tc_id, data)

    def _execute_positive_case(self, tc_id: str, data: Dict[str, str]):
        self.emp.open_create_employee_form()

        if tc_id == "TC_POS_EMP_008":
            self._verify_last_created_employee()
            return

        if tc_id == "TC_POS_EMP_010":
            for field_name, value in data.items():
                assert self.emp.fill_field(field_name, value), f"Could not fill '{field_name}'"
            assert self.emp.click_cancel(), "Cancel/Reset did not clear the form or navigate away"
            return

        full_data = self._build_valid_employee_data(tc_id, data, mandatory_only=False)
        self._fill_fields(full_data)

        outcome = self.emp.click_save_and_confirm()
        record = self.emp.search_employee_in_list(
            full_data["First Name"].strip(),
            full_data["Last Name"].strip(),
        )

        assert record, f"Created employee was not found in list: {full_data['First Name']} {full_data['Last Name']}"
        FormExecutor.last_created_employee = {
            "first_name": full_data["First Name"].strip(),
            "last_name": full_data["Last Name"].strip(),
            "email": full_data.get("Official Email", "").strip(),
            "employee_id": record.get("employee_id", ""),
        }
        if "008" not in tc_id:
            log.info(f"Save outcome for {tc_id}: {outcome}")

    def _execute_negative_case(self, tc_id: str, data: Dict[str, str]):
        self.emp.open_create_employee_form()

        if tc_id == "TC_NEG_EMP_001":
            self.emp.click_save()
            self._assert_submission_rejected(tc_id)
            return

        if tc_id == "TC_NEG_EMP_015":
            self._assert_dropdown_options_are_text()
            return

        if tc_id == "TC_NEG_EMP_016":
            self._assert_new_employee_not_manager_option()
            return

        if tc_id == "TC_NEG_EMP_018":
            self._assert_session_timeout_blocks_save(tc_id)
            return

        if tc_id == "TC_NEG_EMP_013":
            # Verify InvalidID_999 cannot be selected from dropdown options
            options = self.emp.get_dropdown_options("department")
            assert "InvalidID_999" not in options, "Dropdown unexpectedly contains invalid option 'InvalidID_999'"
            full_data = self._build_valid_employee_data(tc_id, {}, mandatory_only=False)
            del full_data["Department"]
            self._fill_fields(full_data)
            self.emp.click_save_and_confirm()
            errors = self.emp.get_validation_errors()
            has_dept_err = any("department" in err.lower() for err in errors)
            if not has_dept_err:
                raise AssertionError(
                    "Application defect: Form failed to display mandatory Department validation error message upon submission"
                )
            return

        full_data = self._build_valid_employee_data(tc_id, {}, mandatory_only=False)
        for field_name, value in data.items():
            self._apply_negative_override(full_data, field_name, value)

        # For duplicate test cases (008, 009, 019), ensure we attempt duplicate submission
        if tc_id == "TC_NEG_EMP_008":
            full_data["Personal Email"] = "existing.email@example.com"
        elif tc_id == "TC_NEG_EMP_009":
            full_data["Mobile Number"] = "9876543210"
        elif tc_id == "TC_NEG_EMP_019":
            full_data["Official Email"] = "existing@company.com"

        self._fill_fields(full_data)

        dialog_messages = []
        if tc_id == "TC_NEG_EMP_014":
            self.page.on("dialog", lambda dialog: dialog_messages.append(dialog.message))

        self.emp.click_save_and_confirm()
        if tc_id == "TC_NEG_EMP_014":
            assert not dialog_messages, f"XSS payload executed a browser dialog: {dialog_messages}"

        self._assert_submission_rejected(tc_id)

    def _build_valid_employee_data(self, tc_id: str, overrides: Dict[str, str], mandatory_only: bool) -> Dict[str, str]:
        number = int(re.search(r"(\d+)$", tc_id).group(1))
        prefix = tc_id.lower().replace("tc_", "").replace("_", "")
        import time
        ts = int(time.time()) % 100000
        data = {
            "First Name": f"Auto{number:03d}",
            "Last Name": "Employee",
            "Gender": "Male",
            "Date of Birth": "15-08-1990",
            "Personal Email": f"{prefix}{ts}.p@example.com",
            "Mobile Number": f"98765{number:02d}{ts%1000:03d}"[:10],
            "Joining Date": "01-09-2026",
            "Department": "Select from given options",
            "Designation": "Select from given options",
            "Reporting Manager": "Select from given options",
            "Role": "Select from given options",
            "Official Email": f"{prefix}{ts}@company.com",
        }

        for field_name, value in overrides.items():
            lowered_key = field_name.lower()
            lowered_value = value.lower()
            if "valid data for all mandatory" in lowered_key:
                continue
            if "first name and last name" in lowered_key:
                continue
            if "50 characters" in lowered_value:
                value = "A" * 50 if "first" in lowered_key else "B" * 50
            data[field_name] = value

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
        key = field_name.strip()
        lowered_key = key.lower()
        lowered_value = value.lower()

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

        full_data[key] = _strip_outer_quotes(value)

    def _fill_fields(self, data: Dict[str, str]) -> None:
        for field_name, value in data.items():
            assert self.emp.fill_field(field_name, value), f"Could not fill '{field_name}' with Excel data"

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

    def _assert_submission_rejected(self, tc_id: str) -> None:
        errors = self.emp.get_validation_errors()
        is_invalid = self.emp.is_form_invalid()
        success_msg = self.emp.get_confirmation_message(timeout=1500)
        
        # A negative scenario is only legitimately rejected if:
        # 1. No success message was received AND
        # 2. Form or fields are marked invalid / validation error text is displayed on screen
        rejected = ("successfully" not in success_msg.lower()) and (is_invalid or bool(errors))
        
        defect_msg = self.DEFECT_REASONS.get(
            tc_id, "Application accepted invalid data without displaying validation error"
        )
        assert rejected, f"Application defect: {defect_msg}"
        log.info(f"Negative scenario [{tc_id}] rejected as expected. Errors: {errors}")

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
        from pages.login_page import LoginPage
        from utils.excel_reader import read_credentials

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
        
        # Restore session credentials for subsequent test cases
        creds = read_credentials("Employee")
        LoginPage(self.page).login(creds["employee_id"], creds["password"], creds["auth_code"])
        assert blocked, "Expired session did not block saving the Create Employee form"
        log.info(f"Negative scenario [{tc_id}] session timeout blocked save as expected.")
