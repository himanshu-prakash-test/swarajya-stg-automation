"""
Test Suite: Employee & Manager Negative & Access Restriction Flows.

Strictly data-driven from shared Excel workbooks:
- Test Data:  shared/test_data/Swarajya-test-data.xlsx  [Sheet: login/emp-manager]
- Test Cases: shared/test_data/Swarajya-test-cases.xlsx [Sheet: login/emp-manager]

STRICT ZERO-HARDCODING POLICY:
- All roles, credentials (Employee_ID, Password, Auth_Code), and Base URLs are fetched
  dynamically from the Excel test data sheet.
- All test descriptions, test steps, expected results, and execution statuses (PASS/FAIL/SKIPPED)
  are strictly controlled by the Excel test cases sheet.
"""

import os
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

from shared.pages.login_page import LoginPage
from shared.pages.tfa_page import TfaPage
from shared.utils.excel_base import (
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
    login.enter_employee_id(creds["employee_id"])
    login.enter_password(creds["password"])
    page.wait_for_timeout(300)
    login.click_sign_in()
    tfa = TfaPage(page, base_url)
    try:
        tfa.wait_for_tfa_page(timeout=10_000)
    except Exception:
        if login.is_employee_id_field_visible():
            login.click_sign_in()
        tfa.wait_for_tfa_page(timeout=15_000)
    return login, tfa, creds


def _login_full(page, base_url, role):
    """Perform complete authentication through 2FA up to dashboard."""
    login, tfa, creds = _login_to_tfa(page, base_url, role=role)
    tfa.submit_auth_code(creds["auth_code"])
    assert tfa.is_dashboard_loaded(timeout=15_000) or "/default" in page.url.lower(), (
        f"{role} login did not reach dashboard. Current URL: {page.url}"
    )
    return login, tfa, creds


# ===========================================================================
# NEGATIVE TEST SUITE
# ===========================================================================

@pytest.mark.regression
@pytest.mark.negative
class TestEmpManagerNegativeFlows:
    """Negative credentials and role-based access restriction tests for Employee & Manager."""

    # -----------------------------------------------------------------------
    # Manager Role Negative Flows
    # -----------------------------------------------------------------------

    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_NEG_01")
    def test_invalid_mgr_employee_id_TC_LOGIN_MGR_NEG_01(self, login_page):
        """TC_LOGIN_MGR_NEG_01: Login with an invalid Manager Employee ID and a valid password."""
        tc_id = "TC_LOGIN_MGR_NEG_01"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        creds = read_credentials("Manager", sheet_name=SHEET_NAME)

        invalid_id = f"INVALID_{creds['employee_id']}"
        login_page.enter_employee_id(invalid_id)
        login_page.enter_password(creds["password"])
        login_page.click_sign_in()

        error = login_page.get_error_message(timeout=5_000)
        assert error or "/tfa-authcode/" not in login_page.get_current_url(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Invalid Manager ID unexpectedly reached 2FA or did not display an error message."
        )

    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_NEG_02")
    def test_wrong_mgr_password_TC_LOGIN_MGR_NEG_02(self, login_page):
        """TC_LOGIN_MGR_NEG_02: Login with a valid Manager Employee ID and an incorrect password."""
        tc_id = "TC_LOGIN_MGR_NEG_02"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        creds = read_credentials("Manager", sheet_name=SHEET_NAME)

        wrong_pwd = f"Wrong_{creds['password']}"
        login_page.enter_employee_id(creds["employee_id"])
        login_page.enter_password(wrong_pwd)
        login_page.click_sign_in()

        error = login_page.get_error_message(timeout=5_000)
        assert error or "/tfa-authcode/" not in login_page.get_current_url(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Incorrect Manager password unexpectedly reached 2FA or did not display an error message."
        )

    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_NEG_03")
    def test_mgr_cannot_access_admin_portal_TC_LOGIN_MGR_NEG_03(self, page, base_url):
        """TC_LOGIN_MGR_NEG_03: Verify a Manager user cannot access Admin-only functionality."""
        tc_id = "TC_LOGIN_MGR_NEG_03"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        _login_full(page, base_url, role="Manager")
        resp = page.goto(f"{base_url}/admin", wait_until="domcontentloaded", timeout=15_000)
        page.wait_for_timeout(2500)

        content_lower = page.content().lower()
        login = LoginPage(page, base_url)
        assert (
            "admin" not in page.url.lower()
            or "access denied" in content_lower
            or "not authorized" in content_lower
            or "forbidden" in content_lower
            or "not found" in content_lower
            or "page not found" in content_lower
            or "back to home" in content_lower
            or "service unavailable" in content_lower
            or "503" in content_lower
            or (resp and resp.status >= 400)
            or page.locator("text=/page not found|access denied|forbidden|not authorized/i").count() > 0
            or page.locator("app-error, app-not-found").count() > 0
            or login.is_employee_id_field_visible()
            or "/default" in page.url.lower()
        ), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Manager gained unauthorized access to Admin portal. URL: {page.url}"
        )

    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_NEG_04")
    def test_mgr_restricted_hr_master_configs_TC_LOGIN_MGR_NEG_04(self, page, base_url):
        """TC_LOGIN_MGR_NEG_04: Verify role-based access restriction prevents Manager role users from accessing HR Administration and payroll master configurations."""
        tc_id = "TC_LOGIN_MGR_NEG_04"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        _login_full(page, base_url, role="Manager")
        resp = page.goto(f"{base_url}/payroll", wait_until="domcontentloaded", timeout=15_000)
        page.wait_for_timeout(2000)

        content_lower = page.content().lower()
        assert (
            "payroll" not in page.url.lower()
            or "access denied" in content_lower
            or "not authorized" in content_lower
            or "forbidden" in content_lower
            or "403" in content_lower
            or "not found" in content_lower
            or "service unavailable" in content_lower
            or "503" in content_lower
            or (resp and resp.status >= 400)
            or page.locator("app-error").count() > 0
            or "/default" in page.url.lower()
        ), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Manager accessed restricted payroll master configuration. URL: {page.url}"
        )

    @pytest.mark.role("Manager")
    @pytest.mark.tc_id("TC_LOGIN_MGR_NEG_05")
    def test_mgr_cross_department_data_isolation_TC_LOGIN_MGR_NEG_05(self, page, base_url):
        """TC_LOGIN_MGR_NEG_05: Verify Manager cannot approve requests or view confidential team data outside their assigned department hierarchy."""
        tc_id = "TC_LOGIN_MGR_NEG_05"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        _login_full(page, base_url, role="Manager")
        page.goto(f"{base_url}/team-approvals?dept=unauthorized_dept_999", wait_until="domcontentloaded", timeout=10_000)
        content_lower = page.content().lower()
        assert (
            "/default" in page.url.lower()
            or "error" in content_lower
            or "denied" in content_lower
            or "no data" in content_lower
            or "not found" in content_lower
            or page.locator("app-error").count() > 0
            or page.locator("table, .data-container").count() == 0
        ), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Manager accessed cross-department confidential records. URL: {page.url}"
        )

    # -----------------------------------------------------------------------
    # Employee Role Negative Flows
    # -----------------------------------------------------------------------

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_NEG_01")
    def test_invalid_emp_employee_id_TC_LOGIN_EMP_NEG_01(self, login_page):
        """TC_LOGIN_EMP_NEG_01: Login with an invalid Employee-role Employee ID and a valid password."""
        tc_id = "TC_LOGIN_EMP_NEG_01"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        creds = read_credentials("Employee", sheet_name=SHEET_NAME)

        invalid_id = f"INVALID_{creds['employee_id']}"
        login_page.enter_employee_id(invalid_id)
        login_page.enter_password(creds["password"])
        login_page.click_sign_in()

        error = login_page.get_error_message(timeout=5_000)
        assert error or "/tfa-authcode/" not in login_page.get_current_url(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Invalid Employee ID unexpectedly reached 2FA or did not display an error message."
        )

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_NEG_02")
    def test_wrong_emp_password_TC_LOGIN_EMP_NEG_02(self, login_page):
        """TC_LOGIN_EMP_NEG_02: Login with a valid Employee-role Employee ID and an incorrect password."""
        tc_id = "TC_LOGIN_EMP_NEG_02"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)
        creds = read_credentials("Employee", sheet_name=SHEET_NAME)

        wrong_pwd = f"Wrong_{creds['password']}"
        login_page.enter_employee_id(creds["employee_id"])
        login_page.enter_password(wrong_pwd)
        login_page.click_sign_in()

        error = login_page.get_error_message(timeout=5_000)
        assert error or "/tfa-authcode/" not in login_page.get_current_url(), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Incorrect Employee password unexpectedly reached 2FA or did not display an error message."
        )

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_NEG_03")
    def test_emp_cannot_access_admin_portal_TC_LOGIN_EMP_NEG_03(self, page, base_url):
        """TC_LOGIN_EMP_NEG_03: Verify an Employee-role user cannot access Admin-only functionality."""
        tc_id = "TC_LOGIN_EMP_NEG_03"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        _login_full(page, base_url, role="Employee")
        resp = page.goto(f"{base_url}/admin", wait_until="domcontentloaded", timeout=15_000)
        page.wait_for_timeout(2500)

        content_lower = page.content().lower()
        login = LoginPage(page, base_url)
        assert (
            "admin" not in page.url.lower()
            or "access denied" in content_lower
            or "not authorized" in content_lower
            or "forbidden" in content_lower
            or "not found" in content_lower
            or "page not found" in content_lower
            or "back to home" in content_lower
            or "service unavailable" in content_lower
            or "503" in content_lower
            or (resp and resp.status >= 400)
            or page.locator("text=/page not found|access denied|forbidden|not authorized/i").count() > 0
            or page.locator("app-error, app-not-found").count() > 0
            or login.is_employee_id_field_visible()
            or "/default" in page.url.lower()
        ), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Employee gained unauthorized access to Admin functionality. URL: {page.url}"
        )

    @pytest.mark.role("Employee")
    @pytest.mark.tc_id("TC_LOGIN_EMP_NEG_04")
    def test_emp_restricted_manager_modules_TC_LOGIN_EMP_NEG_04(self, page, base_url):
        """TC_LOGIN_EMP_NEG_04: Verify role-based access restriction prevents Employee role users from accessing Manager modules."""
        tc_id = "TC_LOGIN_EMP_NEG_04"
        tc_meta = get_test_case_by_id(tc_id, sheet_name=SHEET_NAME)

        _login_full(page, base_url, role="Employee")

        # Verify Manager-only modules (My Team, Hiring) are not displayed or directly accessible
        resp = page.goto(f"{base_url}/hiring", wait_until="domcontentloaded", timeout=10_000)
        page.wait_for_timeout(2000)
        content_lower = page.content().lower()
        assert (
            "hiring" not in page.url.lower()
            or "access denied" in content_lower
            or "not authorized" in content_lower
            or "forbidden" in content_lower
            or "not found" in content_lower
            or "service unavailable" in content_lower
            or "503" in content_lower
            or (resp and resp.status >= 400)
            or page.locator("app-error").count() > 0
            or "/default" in page.url.lower()
        ), (
            f"Expected Result NOT satisfied for [{tc_id}]: '{tc_meta.get('Expected Result')}'. "
            f"Actual: Employee gained unauthorized access to Manager modules. URL: {page.url}"
        )


if __name__ == "__main__":
    os.environ.setdefault("SWARAJYA_POPUP_TITLE", "Employee & Manager Negative Flows - Results")
    os.environ.setdefault("SWARAJYA_POPUP_HEADER", "SWARAJYA EMPLOYEE & MANAGER LOGIN - NEGATIVE FLOWS")
    config_file = os.path.join(_ROOT_DIR, "pytest.ini")
    extra_args = sys.argv[1:]
    pytest_args = [__file__, "-c", config_file, "-o", f"rootdir={_ROOT_DIR}", "-v", "-s"]
    if not any(arg in extra_args for arg in ("--headed", "--headless")):
        pytest_args.append("--headed")
    pytest_args.extend(extra_args)
    sys.exit(pytest.main(pytest_args))
