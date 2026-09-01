"""Workbook-driven Employee Management update tests with automated screenshot capture."""

import logging
import os
import re
import time
import pytest

from pages.login_page import LoginPage
from pages.tfa_page import TfaPage
from update.emp_mgmt.employee_update_page import EmployeeUpdatePage
from update.emp_mgmt.employee_workbook import read_employee_cases, update_employee_result

log = logging.getLogger(__name__)

CASES = read_employee_cases()
SCREENSHOT_DIR = os.path.join(os.getcwd(), "update", "emp_mgmt", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def _case_id(case):
    return str(case["Test Case ID"]).strip()


def _login_and_open(page, base_url, employee_credentials):
    employee = EmployeeUpdatePage(page, base_url)
    if "/empProfile/" in page.url:
        return employee
    if "/default" in page.url or "/employeeList" in page.url:
        employee.open_target_profile()
        return employee

    login = LoginPage(page, base_url)
    login.navigate()
    if "/default" in page.url or "/employeeList" in page.url or "/empProfile/" in page.url:
        employee.open_target_profile()
        return employee

    emp_id = str(employee_credentials.get("employee_id", "332"))
    pwd = str(employee_credentials.get("password", "test@1234"))
    auth_code = str(employee_credentials.get("auth_code", "111111"))

    login.login(emp_id, pwd)
    if "/default" not in page.url and "/employeeList" not in page.url and "/empProfile/" not in page.url:
        tfa = TfaPage(page, base_url)
        tfa.wait_for_tfa_page(timeout=15_000)
        if tfa.is_on_tfa_page():
            tfa.submit_auth_code(auth_code)
            assert tfa.is_dashboard_loaded(timeout=15_000), f"Dashboard did not load: {page.url}"
    employee.open_target_profile()
    return employee


def _values(text):
    return dict(re.findall(r"^([^:\n]+):\s*(.+)$", text or "", re.MULTILINE))


@pytest.mark.regression
@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_employee_update_case(case, page, base_url, employee_credentials):
    case_id = _case_id(case)
    log.info("Running Employee Update Test: %s", case_id)
    try:
        employee = _login_and_open(page, base_url, employee_credentials)
        data = _values(str(case.get("Test Data", "")))

        if case_id == "TC_POS_UPD_001":
            employee.update({
                ("First Name", "firstName", "emp_first_name"): data.get("First Name", "Ruchira"),
                ("Last Name", "lastName", "emp_last_name"): data.get("Last Name", "Rao"),
                ("Mobile Number", "mobile", "emp_mobile_number"): data.get("Mobile Number", "9876543220"),
                ("Email ID", "email", "emp_email"): data.get("Email ID", "ruchira.rao@company.com"),
            })
        elif case_id == "TC_POS_UPD_002":
            employee.set_gender(data.get("Gender", "Female").split()[0]).save()
        elif case_id == "TC_POS_UPD_003":
            for option in ("Married", "Unmarried"):
                employee.select_option(("Marital Status", "maritalStatus", "emp_maritalStatus"), option).save()
                if option != "Unmarried":
                    employee.open_target_profile()
        elif case_id == "TC_POS_UPD_004":
            toggle = page.locator("mat-datepicker-toggle button, [aria-label*='calendar' i]").first
            if toggle.count():
                toggle.click()
                cell = page.locator("mat-calendar .mat-calendar-body-cell:not(.mat-calendar-body-disabled)").first
                cell.wait_for(state="visible", timeout=4_000)
                cell.click()
                try:
                    page.locator("mat-calendar").wait_for(state="hidden", timeout=3_000)
                except Exception:
                    pass
            else:
                employee.set_field(("Date Of Birth", "Date of Birth", "dateOfBirth", "emp_dob"), "20-05-1994")
            employee.save()
        elif case_id == "TC_POS_UPD_005":
            employee.update({("Personal Email ID", "personalEmail", "emp_personal_email"): "ruchira.personal@example.com"})
        elif case_id == "TC_POS_UPD_006":
            employee.toggle("Is Egg?", True).toggle("Is Non-Veg?", False).save()
        elif case_id == "TC_POS_UPD_007":
            employee.update({
                ("Emergency Contact Name", "emergencyContactName", "emp_emergency_contact_name"): "Suresh Rao",
                ("Emergency Contact Number", "emergencyContactNumber", "emp_emergency_contact_number"): "9123456780",
            })
        elif case_id == "TC_POS_UPD_008":
            employee.update({
                ("Correspondence Address 1", "address1", "emp_correspondance_address1"): "Flat 12, Green Residency",
                ("Address 2", "address2", "emp_correspondance_address2"): "Near City Mall",
                ("City", "city", "emp_correspondance_city"): "Pune",
                ("PIN", "pin", "emp_correspondance_pin"): "411001",
            })
        elif case_id in {"TC_POS_UPD_009", "TC_POS_UPD_011"}:
            employee.save()
        elif case_id == "TC_POS_UPD_010" or case_id == "TC_NEG_UPD_007":
            assert employee.employee_id_is_read_only()
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{case_id}_passed.png"))
            update_employee_result(case_id, "PASS")
            return
        elif case_id == "TC_POS_UPD_012":
            employee.set_field(("First Name", "firstName", "emp_first_name"), "Test Update").cancel()
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{case_id}_passed.png"))
            update_employee_result(case_id, "PASS")
            return
        elif case_id == "TC_POS_UPD_013":
            employee.update({("Last Name", "lastName", "emp_last_name"): "O'Connor"})
        elif case_id == "TC_POS_UPD_014":
            employee.update({("First Name", "firstName", "emp_first_name"): "A" * 50, ("Last Name", "lastName", "emp_last_name"): "B" * 50})
        elif case_id == "TC_POS_UPD_015":
            employee.update({
                ("First Name", "firstName", "emp_first_name"): "Ruchira",
                ("Last Name", "lastName", "emp_last_name"): "Rao",
                ("Correspondence Address 1", "address1", "emp_correspondance_address1"): "Flat 12, Green Residency",
                ("Emergency Contact Name", "emergencyContactName", "emp_emergency_contact_name"): "Suresh Rao",
            })
        elif case_id == "TC_NEG_UPD_001":
            employee.set_field(("First Name", "firstName", "emp_first_name"), "").save()
        elif case_id == "TC_NEG_UPD_002":
            employee.set_field(("Mobile Number", "mobile", "emp_mobile_number"), "98765abcde").save()
        elif case_id == "TC_NEG_UPD_003":
            employee.set_field(("Email ID", "email", "emp_email"), "ruchira.rao@").save()
        elif case_id == "TC_NEG_UPD_004":
            employee.set_field(("First Name", "firstName", "emp_first_name"), "12345").save()
        elif case_id == "TC_NEG_UPD_005":
            employee.set_field(("PIN", "pin", "emp_correspondance_pin"), "1234A").save()
        elif case_id == "TC_NEG_UPD_006":
            employee.set_field(("Date Of Joining", "Date of Joining", "dateOfJoining", "emp_doj"), "01-01-1990").save()
        elif case_id == "TC_NEG_UPD_008":
            employee.set_field(("Mobile Number", "mobile", "emp_mobile_number"), "9876543210").save()
        elif case_id == "TC_NEG_UPD_009":
            page.goto(f"{base_url}/logout", wait_until="networkidle", timeout=15_000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{case_id}_skipped.png"))
            pytest.skip("Session-expiry update requires a controllable expired session")
        elif case_id == "TC_NEG_UPD_010":
            employee.set_field(("First Name", "firstName", "emp_first_name"), "   ").save()
        elif case_id == "TC_NEG_UPD_011":
            employee.set_field(("Date Of Birth", "Date of Birth", "dateOfBirth", "emp_dob"), "01-01-2025").save()
        elif case_id == "TC_NEG_UPD_012":
            employee.set_field(("Date Of Joining", "Date of Joining", "dateOfJoining", "emp_doj"), "03-03-2031").save()
        elif case_id == "TC_NEG_UPD_013":
            employee.set_field(("Emergency Contact Number", "emergencyContactNumber", "emp_emergency_contact_number"), "987abc1234").save()
        else:
            pytest.fail(f"Unhandled employee update case: {case_id}")

        if case_id.startswith("TC_NEG_"):
            assert employee.validation_visible(), f"Expected validation feedback for {case_id}"
        elif case_id not in {"TC_POS_UPD_010", "TC_POS_UPD_011", "TC_POS_UPD_012"}:
            assert employee.success_message_visible(), f"Expected save confirmation for {case_id}"

        # Capture pass screenshot
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{case_id}_passed.png"))
        log.info("Test %s completed successfully.", case_id)

    except pytest.skip.Exception:
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{case_id}_skipped.png"))
        update_employee_result(case_id, "SKIPPED", "Scenario requires a controllable session or unavailable UI control")
        raise
    except Exception as exc:
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"{case_id}_failed.png"))
        update_employee_result(case_id, "FAIL", str(exc))
        raise
    else:
        update_employee_result(case_id, "PASS")
