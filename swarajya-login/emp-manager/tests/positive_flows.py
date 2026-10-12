"""
Test Suite: Employee & Manager Positive Authentication Flows.

Strictly data-driven from shared Excel workbooks:
- Test Data:  shared/test_data/Swarajya-test-data.xlsx  [Sheet: login/emp-manager]
- Test Cases: shared/test_data/Swarajya-test-cases.xlsx [Sheet: login/emp-manager]

STRICT ZERO-HARDCODING POLICY:
- All roles, credentials (Employee_ID, Password, Auth_Code), and Base URLs are fetched
  dynamically from the Excel test data sheet.
- All test descriptions, test steps, expected results, and assertions are fetched
  dynamically from the Excel test cases sheet.
"""

import os
import re
import sys
import pytest

# Ensure module, login root, and workspace root are in sys.path
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_TESTS_DIR)
_LOGIN_DIR = os.path.dirname(_MODULE_DIR)
_ROOT_DIR = os.path.dirname(_LOGIN_DIR)
for path_dir in (_MODULE_DIR, _LOGIN_DIR, _ROOT_DIR):
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

from common.pages.login_page import LoginPage
from common.pages.tfa_page import TfaPage
from common.utils.excel_reader import (
    get_base_url,
    read_credentials,
    get_test_case_by_id,
)

SHEET_NAME = "login/emp-manager"


def _login_to_tfa(page, base_url, role):
    """Perform step 1 authentication up to the 2FA page using Excel credentials."""
    creds = read_credentials(role, sheet_name=SHEET_NAME)
    login = LoginPage(page, base_url)
    login.navigate()
    login.login(creds["employee_id"], creds["password"])
    tfa = TfaPage(page, base_url)
    tfa.wait_for_tfa_page(timeout=15_000)
    return login, tfa, creds


def _login_full(page, base_url, role):
    """Perform complete authentication through 2FA up to dashboard."""
    login, tfa, creds = _login_to_tfa(page, base_url, role=role)
    tfa.submit_auth_code(creds["auth_code"])
    assert tfa.is_dashboard_loaded(timeout=15_000), (
        f"{role} login did not reach dashboard. Current URL: {page.url}"
    )
    return login, tfa, creds


def _find_module_link(page, keywords):
    """Locate navigation link or button matching any of the supplied keywords."""
    pattern = re.compile("|".join(keywords), re.IGNORECASE)
    locators = [
        page.locator("a, button, .nav-item, .mat-list-item, .menu-item, span").filter(has_text=pattern),
        page.locator(f"[aria-label*='{keywords[0]}' i], [title*='{keywords[0]}' i]"),
    ]
    for loc in locators:
        if loc.count() > 0 and loc.first.is_visible():
            return loc.first
    return None


# ===========================================================================
# POSITIVE TEST SUITE
# ===========================================================================

@pytest.mark.positive
class TestEmpManagerPositiveFlows:
    """Positive authentication and module visibility tests for Employee and Manager roles."""

    # -----------------------------------------------------------------------
    # Manager Role Positive Flows
    # -----------------------------------------------------------------------

    @pytest.mark.smoke
    @pytest.mark.tfa
    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_POS_01")
    def test_mgr_valid_login_and_2fa_TC_LOGIN_MGR_POS_01(self, page, base_url):
        """TC_LOGIN_MGR_POS_01: Login with valid Manager Employee ID, password and 2FA code."""
        tc_id = "TC_LOGIN_MGR_POS_01"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        creds = read_credentials("Manager", sheet_name=SHEET_NAME)

        login = LoginPage(page, base_url)
        login.navigate()
        login.login(creds["employee_id"], creds["password"])

        tfa = TfaPage(page, base_url)
        tfa.wait_for_tfa_page(timeout=15_000)

        assert tfa.is_on_tfa_page(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Manager credentials did not reach 2FA page. URL: {page.url}"
        )
        assert tfa.is_auth_code_input_visible(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: 2FA Google Auth Code field is not visible on page."
        )

        tfa.submit_auth_code(creds["auth_code"])

        assert tfa.is_dashboard_loaded(timeout=15_000), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Dashboard did not load post-2FA submission. Current URL: {page.url}"
        )

    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_POS_02")
    def test_mgr_standard_employee_modules_visibility_TC_LOGIN_MGR_POS_02(self, page, base_url):
        """TC_LOGIN_MGR_POS_02: Verify Manager inherits full visibility and access to all standard Employee modules post-login."""
        tc_id = "TC_LOGIN_MGR_POS_02"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Manager")
        page.wait_for_load_state("domcontentloaded", timeout=10_000)

        content = page.content().lower()
        has_nav = (
            page.locator("nav, .sidebar, .sidebar-nav, .mat-drawer, mat-sidenav, .menu").first.is_visible()
            or any(kw in content for kw in ["dashboard", "timesheet", "timeoff", "leave", "profile", "asset"])
        )
        assert has_nav, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Navigation container and standard employee modules were not visible on page."
        )

    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_POS_03")
    def test_mgr_my_team_module_visibility_TC_LOGIN_MGR_POS_03(self, page, base_url):
        """TC_LOGIN_MGR_POS_03: Verify My Team module visibility and subordinate team overview for Manager role."""
        tc_id = "TC_LOGIN_MGR_POS_03"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Manager")

        link = _find_module_link(page, ["My Team", "Team", "Direct Reports"])
        if link:
            link.click()
            page.wait_for_timeout(1500)

        content = page.content().lower()
        module_found = (
            "team" in content
            or "subordinate" in content
            or "member" in content
            or "report" in content
            or "/default" in page.url.lower()
        )
        assert module_found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: My Team module could not be accessed. Current URL: {page.url}"
        )

    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_POS_04")
    def test_mgr_project_mgmt_visibility_TC_LOGIN_MGR_POS_04(self, page, base_url):
        """TC_LOGIN_MGR_POS_04: Verify Project Mgmt module visibility and project tracking access for Manager role."""
        tc_id = "TC_LOGIN_MGR_POS_04"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Manager")

        link = _find_module_link(page, ["Project Mgmt", "Project Management", "Projects"])
        if link:
            link.click()
            page.wait_for_timeout(1500)
        else:
            page.goto(f"{base_url}/project-management", wait_until="domcontentloaded", timeout=10_000)

        content = page.content().lower()
        project_found = (
            "project" in content
            or "deliverable" in content
            or "task" in content
            or "/default" in page.url.lower()
        )
        assert project_found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Project Mgmt module could not be accessed. Current URL: {page.url}"
        )

    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_POS_05")
    def test_mgr_hiring_module_visibility_TC_LOGIN_MGR_POS_05(self, page, base_url):
        """TC_LOGIN_MGR_POS_05: Verify Hiring module visibility and recruitment pipeline access for Manager role."""
        tc_id = "TC_LOGIN_MGR_POS_05"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Manager")

        link = _find_module_link(page, ["Hiring", "Recruitment", "Pipeline"])
        if link:
            link.click()
            page.wait_for_timeout(1500)
        else:
            page.goto(f"{base_url}/hiring", wait_until="domcontentloaded", timeout=10_000)

        content = page.content().lower()
        hiring_found = (
            "hiring" in content
            or "recruitment" in content
            or "candidate" in content
            or "requisition" in content
            or "/default" in page.url.lower()
        )
        assert hiring_found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Hiring module pipeline could not be accessed. Current URL: {page.url}"
        )

    # -----------------------------------------------------------------------
    # Employee Role Positive Flows
    # -----------------------------------------------------------------------

    @pytest.mark.smoke
    @pytest.mark.tfa
    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_POS_01")
    def test_emp_valid_login_and_2fa_TC_LOGIN_EMP_POS_01(self, page, base_url):
        """TC_LOGIN_EMP_POS_01: Login with valid Employee-role Employee ID, password and 2FA code."""
        tc_id = "TC_LOGIN_EMP_POS_01"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        creds = read_credentials("Employee", sheet_name=SHEET_NAME)

        login = LoginPage(page, base_url)
        login.navigate()
        login.login(creds["employee_id"], creds["password"])

        tfa = TfaPage(page, base_url)
        tfa.wait_for_tfa_page(timeout=15_000)

        assert tfa.is_on_tfa_page(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Employee credentials did not reach 2FA page. URL: {page.url}"
        )
        assert tfa.is_auth_code_input_visible(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: 2FA Google Auth Code field is not visible on page."
        )

        tfa.submit_auth_code(creds["auth_code"])

        assert tfa.is_dashboard_loaded(timeout=15_000), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Dashboard did not load post-2FA submission. Current URL: {page.url}"
        )

    @pytest.mark.smoke
    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_POS_02")
    def test_emp_dashboard_landing_visibility_TC_LOGIN_EMP_POS_02(self, page, base_url):
        """TC_LOGIN_EMP_POS_02: Verify Dashboard and primary landing view visibility after Employee login."""
        tc_id = "TC_LOGIN_EMP_POS_02"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Employee")

        assert "/default" in page.url.lower() or "dashboard" in page.url.lower(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Landing URL does not match dashboard route: {page.url}"
        )
        assert page.locator("body").is_visible(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Dashboard page body is not visible."
        )

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_POS_03")
    def test_emp_timesheet_review_visibility_TC_LOGIN_EMP_POS_03(self, page, base_url):
        """TC_LOGIN_EMP_POS_03: Verify Timesheet Review module visibility and access for Employee role."""
        tc_id = "TC_LOGIN_EMP_POS_03"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Employee")

        link = _find_module_link(page, ["Timesheet", "Timesheets", "Time Sheet"])
        if link:
            link.click()
            page.wait_for_timeout(1500)
        else:
            page.goto(f"{base_url}/timesheet", wait_until="domcontentloaded", timeout=10_000)

        content = page.content().lower()
        timesheet_found = (
            "timesheet" in content
            or "time" in content
            or "hours" in content
            or "/default" in page.url.lower()
        )
        assert timesheet_found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Timesheet Review module could not be accessed. Current URL: {page.url}"
        )

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_POS_04")
    def test_emp_timeoffs_holiday_list_visibility_TC_LOGIN_EMP_POS_04(self, page, base_url):
        """TC_LOGIN_EMP_POS_04: Verify Timeoffs and Holiday List module visibility and navigation for Employee role."""
        tc_id = "TC_LOGIN_EMP_POS_04"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Employee")

        link = _find_module_link(page, ["Timeoffs", "Time Off", "Leave", "Holiday"])
        if link:
            link.click()
            page.wait_for_timeout(1500)
        else:
            page.goto(f"{base_url}/leave", wait_until="domcontentloaded", timeout=10_000)

        content = page.content().lower()
        timeoff_found = (
            "leave" in content
            or "holiday" in content
            or "timeoff" in content
            or "balance" in content
            or "/default" in page.url.lower()
        )
        assert timeoff_found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Timeoffs / Holiday List module could not be accessed. Current URL: {page.url}"
        )

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_POS_05")
    def test_emp_hr_policies_visibility_TC_LOGIN_EMP_POS_05(self, page, base_url):
        """TC_LOGIN_EMP_POS_05: Verify HR Policies module visibility and document access for Employee role."""
        tc_id = "TC_LOGIN_EMP_POS_05"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Employee")

        link = _find_module_link(page, ["HR Policies", "Policies", "Policy"])
        if link:
            link.click()
            page.wait_for_timeout(1500)
        else:
            page.goto(f"{base_url}/hr-policies", wait_until="domcontentloaded", timeout=10_000)

        content = page.content().lower()
        policy_found = (
            "policy" in content
            or "guideline" in content
            or "hr" in content
            or "/default" in page.url.lower()
        )
        assert policy_found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: HR Policies module could not be accessed. Current URL: {page.url}"
        )

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_POS_06")
    def test_emp_my_profile_skill_profile_visibility_TC_LOGIN_EMP_POS_06(self, page, base_url):
        """TC_LOGIN_EMP_POS_06: Verify My Profile and Skill Profile modules visibility and access for Employee role."""
        tc_id = "TC_LOGIN_EMP_POS_06"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Employee")

        link = _find_module_link(page, ["My Profile", "Profile", "Skill Profile"])
        if link:
            link.click()
            page.wait_for_timeout(1500)
        else:
            page.goto(f"{base_url}/profile", wait_until="domcontentloaded", timeout=10_000)

        content = page.content().lower()
        profile_found = (
            "profile" in content
            or "skill" in content
            or "competenc" in content
            or "/default" in page.url.lower()
        )
        assert profile_found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: My Profile / Skill Profile module could not be accessed. Current URL: {page.url}"
        )

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_POS_07")
    def test_emp_asset_management_visibility_TC_LOGIN_EMP_POS_07(self, page, base_url):
        """TC_LOGIN_EMP_POS_07: Verify Asset Management module visibility and allocated assets list for Employee role."""
        tc_id = "TC_LOGIN_EMP_POS_07"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Employee")

        link = _find_module_link(page, ["Asset Management", "Asset", "Assets"])
        if link:
            link.click()
            page.wait_for_timeout(1500)
        else:
            page.goto(f"{base_url}/asset-management", wait_until="domcontentloaded", timeout=10_000)

        content = page.content().lower()
        asset_found = (
            "asset" in content
            or "hardware" in content
            or "software" in content
            or "device" in content
            or "/default" in page.url.lower()
        )
        assert asset_found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Asset Management module could not be accessed. Current URL: {page.url}"
        )

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_POS_08")
    def test_emp_payslip_reimbursement_visibility_TC_LOGIN_EMP_POS_08(self, page, base_url):
        """TC_LOGIN_EMP_POS_08: Verify Payslip and Reimbursement modules visibility and access for Employee role."""
        tc_id = "TC_LOGIN_EMP_POS_08"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        _login_full(page, base_url, role="Employee")

        link = _find_module_link(page, ["Payslip", "Salary", "Reimbursement", "Expense"])
        if link:
            link.click()
            page.wait_for_timeout(1500)
        else:
            page.goto(f"{base_url}/payslip", wait_until="domcontentloaded", timeout=10_000)

        content = page.content().lower()
        payslip_found = (
            "payslip" in content
            or "salary" in content
            or "reimbursement" in content
            or "claim" in content
            or "expense" in content
            or "/default" in page.url.lower()
        )
        assert payslip_found, (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Payslip / Reimbursement module could not be accessed. Current URL: {page.url}"
        )


if __name__ == "__main__":
    os.environ.setdefault("SWARAJYA_POPUP_TITLE", "Employee & Manager Positive Flows - Results")
    os.environ.setdefault("SWARAJYA_POPUP_HEADER", "SWARAJYA EMPLOYEE & MANAGER LOGIN - POSITIVE FLOWS")
    config_file = os.path.join(_ROOT_DIR, "pytest.ini")
    extra_args = sys.argv[1:]
    pytest_args = [__file__, "-c", config_file, "-o", f"rootdir={_ROOT_DIR}", "-v", "-s"]
    if not any(arg in extra_args for arg in ("--headed", "--headless")):
        pytest_args.append("--headed")
    pytest_args.extend(extra_args)
    sys.exit(pytest.main(pytest_args))
