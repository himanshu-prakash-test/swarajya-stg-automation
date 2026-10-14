"""
Authentication and Navigation Verification for Employee Management (Create Module).
Tests login and access paths using credentials dynamically extracted from Excel.
"""

import os
import sys
import pytest

_TEST_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_TEST_DIR)
_ROOT_DIR = os.path.dirname(os.path.dirname(_MODULE_DIR))

for _p in (_MODULE_DIR, _ROOT_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shared.pages.login_page import LoginPage
from emp_pages.employee_page import EmployeePage
from emp_utils.excel_reader import read_credentials


@pytest.mark.login
@pytest.mark.employee
class TestEmployeeLoginFlow:
    """Authentication and session verification tests for Employee Management."""

    @pytest.mark.tc_id("TC_EMP_AUTH_01")
    def test_admin_login_and_employee_access(self, unauthenticated_page):
        """Verify Admin login succeeds using credentials dynamically fetched from Excel."""
        page = unauthenticated_page
        login_page = LoginPage(page)
        creds = read_credentials("Admin")
        expected_result = "Admin user successfully logs in and reaches authenticated dashboard."

        success = login_page.login(
            employee_id=creds["employee_id"],
            password=creds["password"],
            auth_code=creds.get("auth_code"),
            role=creds.get("role", "Admin"),
        )
        assert success, (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Actual: Admin login failed to authenticate with credentials from Excel."
        )
        assert not ("login" in page.url.lower() or "tfa" in page.url.lower()), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Actual: User remained on login or 2FA verification page: {page.url}"
        )

    @pytest.mark.tc_id("TC_EMP_NAV_01")
    def test_employee_create_navigation_path(self, authenticated_page):
        """Verify navigation path to create employee form: /default -> /employeeList -> /addNewEmployee."""
        expected_result = "User successfully traverses navigation path to employee list and opens Create form."
        emp = EmployeePage(authenticated_page)

        emp.navigate_to_employee_list()
        assert "employeelist" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed to navigate to employee list. Current URL: {authenticated_page.url}"
        )

        emp.open_create_employee_form()
        assert "addnewemployee" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed to open create employee form. Current URL: {authenticated_page.url}"
        )


if __name__ == "__main__":
    config_file = os.path.join(_ROOT_DIR, "pytest.ini")
    pytest_args = [__file__, "-c", config_file, "-o", f"rootdir={_ROOT_DIR}", "-v", "-s"]
    extra_args = sys.argv[1:]
    if not any(arg in extra_args for arg in ("--headed", "--headless")):
        pytest_args.append("--headed")
    pytest_args.extend(extra_args)
    sys.exit(pytest.main(pytest_args))
