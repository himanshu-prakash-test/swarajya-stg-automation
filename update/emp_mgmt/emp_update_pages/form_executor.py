"""Form Executor for Employee Management Update positive and negative test suites."""

import logging
import re
import pytest
from playwright.sync_api import Page
from emp_update_pages.employee_update_page import EmployeeUpdatePage
from emp_update_utils.logger import get_logger

log = get_logger("form_executor")


def _parse_key_values(text: str) -> dict:
    if not text:
        return {}
    pairs = re.findall(r"^([^:\n]+):\s*(.+)$", str(text), re.MULTILINE)
    return {k.strip(): v.strip() for k, v in pairs}


class EmployeeUpdateFormExecutor:
    def __init__(self, page: Page):
        self.page = page
        self.update_page = EmployeeUpdatePage(page)

    def prepare_profile(self):
        self.update_page.open_target_profile()
        return self.update_page

    def execute_positive_case(self, case: dict):
        tc_id = str(case.get("Test Case ID", "")).strip()
        raw_data = str(case.get("Test Data", "") or "")
        data = _parse_key_values(raw_data)
        emp = self.prepare_profile()

        log.info(f"Executing Positive Update Test: {tc_id}")

        if tc_id == "TC_POS_UPD_001":
            emp.update({
                ("First Name", "firstName", "emp_first_name"): data.get("First Name", "Ruchira"),
                ("Last Name", "lastName", "emp_last_name"): data.get("Last Name", "Rao"),
                ("Mobile Number", "mobile", "emp_mobile_number"): data.get("Mobile Number", "9876543220"),
                ("Email ID", "email", "emp_email"): data.get("Email ID", "ruchira.rao@company.com"),
            })
        elif tc_id == "TC_POS_UPD_002":
            gender_val = data.get("Gender", "Female").split()[0]
            emp.set_gender(gender_val).save()
        elif tc_id == "TC_POS_UPD_003":
            for option in ("Married", "Unmarried"):
                emp.select_option(("Marital Status", "maritalStatus", "emp_maritalStatus"), option).save()
                if option != "Unmarried":
                    emp.open_target_profile()
        elif tc_id == "TC_POS_UPD_004":
            toggle = self.page.locator("mat-datepicker-toggle button, [aria-label*='calendar' i]").first
            if toggle.count():
                toggle.click()
                cell = self.page.locator("mat-calendar .mat-calendar-body-cell:not(.mat-calendar-body-disabled)").first
                cell.wait_for(state="visible", timeout=4_000)
                cell.click()
                try:
                    self.page.locator("mat-calendar").wait_for(state="hidden", timeout=3_000)
                except Exception:
                    pass
            else:
                emp.set_field(("Date Of Birth", "Date of Birth", "dateOfBirth", "emp_dob"), "20-05-1994")
            emp.save()
        elif tc_id == "TC_POS_UPD_005":
            emp.update({("Personal Email ID", "personalEmail", "emp_personal_email"): "ruchira.personal@example.com"})
        elif tc_id == "TC_POS_UPD_006":
            emp.toggle("Is Egg?", True).toggle("Is Non-Veg?", False).save()
        elif tc_id == "TC_POS_UPD_007":
            emp.update({
                ("Emergency Contact Name", "emergencyContactName", "emp_emergency_contact_name"): "Suresh Rao",
                ("Emergency Contact Number", "emergencyContactNumber", "emp_emergency_contact_number"): "9123456780",
            })
        elif tc_id == "TC_POS_UPD_008":
            emp.update({
                ("Correspondence Address 1", "address1", "emp_correspondance_address1"): "Flat 12, Green Residency",
                ("Address 2", "address2", "emp_correspondance_address2"): "Near City Mall",
                ("City", "city", "emp_correspondance_city"): "Pune",
                ("PIN", "pin", "emp_correspondance_pin"): "411001",
            })
        elif tc_id in {"TC_POS_UPD_009", "TC_POS_UPD_011"}:
            emp.save()
        elif tc_id == "TC_POS_UPD_010":
            assert emp.employee_id_is_read_only(), f"Employee ID should be read-only for {tc_id}"
            return
        elif tc_id == "TC_POS_UPD_012":
            emp.set_field(("First Name", "firstName", "emp_first_name"), "Test Update").cancel()
            return
        elif tc_id == "TC_POS_UPD_013":
            emp.update({("Last Name", "lastName", "emp_last_name"): "O'Connor"})
        elif tc_id == "TC_POS_UPD_014":
            emp.update({
                ("First Name", "firstName", "emp_first_name"): "A" * 50,
                ("Last Name", "lastName", "emp_last_name"): "B" * 50,
            })
        elif tc_id == "TC_POS_UPD_015":
            emp.update({
                ("First Name", "firstName", "emp_first_name"): "Ruchira",
                ("Last Name", "lastName", "emp_last_name"): "Rao",
                ("Correspondence Address 1", "address1", "emp_correspondance_address1"): "Flat 12, Green Residency",
                ("Emergency Contact Name", "emergencyContactName", "emp_emergency_contact_name"): "Suresh Rao",
            })
        else:
            emp.save()

        assert emp.success_message_visible(), f"Expected save confirmation / successful update for {tc_id}"

    def execute_negative_case(self, case: dict):
        tc_id = str(case.get("Test Case ID", "")).strip()
        raw_data = str(case.get("Test Data", "") or "")
        data = _parse_key_values(raw_data)

        log.info(f"Executing Negative Update Test: {tc_id}")

        if tc_id == "TC_NEG_UPD_009":
            pytest.skip("Session-expiry update requires a controllable expired session mock")

        emp = self.prepare_profile()

        if tc_id == "TC_NEG_UPD_001":
            emp.set_field(("First Name", "firstName", "emp_first_name"), "").save()
        elif tc_id == "TC_NEG_UPD_002":
            emp.set_field(("Mobile Number", "mobile", "emp_mobile_number"), "98765abcde").save()
        elif tc_id == "TC_NEG_UPD_003":
            emp.set_field(("Email ID", "email", "emp_email"), "ruchira.rao@").save()
        elif tc_id == "TC_NEG_UPD_004":
            emp.set_field(("First Name", "firstName", "emp_first_name"), "12345").save()
        elif tc_id == "TC_NEG_UPD_005":
            emp.set_field(("PIN", "pin", "emp_correspondance_pin"), "1234A").save()
        elif tc_id == "TC_NEG_UPD_006":
            emp.set_field(("Date Of Joining", "Date of Joining", "dateOfJoining", "emp_doj"), "01-01-1990").save()
        elif tc_id == "TC_NEG_UPD_007":
            assert emp.employee_id_is_read_only(), f"Employee ID field should be read-only for {tc_id}"
            return
        elif tc_id == "TC_NEG_UPD_008":
            emp.set_field(("Mobile Number", "mobile", "emp_mobile_number"), "9876543210").save()
        elif tc_id == "TC_NEG_UPD_010":
            emp.set_field(("First Name", "firstName", "emp_first_name"), "   ").save()
        elif tc_id == "TC_NEG_UPD_011":
            emp.set_field(("Date Of Birth", "Date of Birth", "dateOfBirth", "emp_dob"), "01-01-2025").save()
        elif tc_id == "TC_NEG_UPD_012":
            emp.set_field(("Date Of Joining", "Date of Joining", "dateOfJoining", "emp_doj"), "03-03-2031").save()
        elif tc_id == "TC_NEG_UPD_013":
            emp.set_field(("Emergency Contact Number", "emergencyContactNumber", "emp_emergency_contact_number"), "987abc1234").save()
        else:
            emp.save()

        assert emp.validation_visible(), f"Expected validation feedback or prevented update for {tc_id}"
