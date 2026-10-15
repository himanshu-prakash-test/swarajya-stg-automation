"""Test suite verifying login and navigation workflow for Employee Update module."""

import pytest
from shared.pages.login_page import LoginPage
from emp_update_pages.employee_update_page import EmployeeUpdatePage
from emp_update_utils.excel_reader import read_credentials, get_baseline_employee, SHEET_NAME


@pytest.mark.login
@pytest.mark.employee
@pytest.mark.employee_update
class TestEmployeeLoginAndNavFlow:
    """Authentication and navigation path verification for Employee Update."""

    @pytest.mark.tc_id("TC_EMP_AUTH_01")
    def test_admin_login_and_access(self, unauthenticated_page):
        """
        Verify:
        1. Login with Admin credentials dynamically loaded from Excel
        2. Landing on authenticated dashboard /default
        """
        page = unauthenticated_page
        login_page = LoginPage(page)
        creds = read_credentials("Admin")
        expected_result = "Admin user successfully logs in and reaches authenticated dashboard."

        import inspect
        sig = inspect.signature(login_page.login)
        kwargs = {}
        if "sheet_name" in sig.parameters:
            kwargs["sheet_name"] = SHEET_NAME

        success = login_page.login(
            employee_id=creds["employee_id"],
            password=creds["password"],
            auth_code=creds.get("auth_code"),
            role=creds.get("role", "Admin"),
            **kwargs,
        )
        assert success, (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Actual: Admin login failed to authenticate with provided credentials."
        )
        assert not ("login" in page.url.lower() or "tfa" in page.url.lower()), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Actual: User remained on login or 2FA verification page: {page.url}"
        )

    @pytest.mark.tc_id("TC_EMP_NAV_01")
    def test_employee_update_navigation_path(self, authenticated_page):
        """
        Verify the Employee Update navigation path:
        /default -> /employeeList -> click profile action icon -> /empProfile/<id> opens.
        """
        expected_result = (
            "User traverses: /default -> /employeeList -> clicks profile icon -> "
            "Employee Profile edit view opens."
        )
        emp_page = EmployeeUpdatePage(authenticated_page)

        # Step 1: Default dashboard
        emp_page.open_default_dashboard()
        assert "default" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 1 (/default). Current URL: {authenticated_page.url}"
        )

        # Step 2: Employee Listing
        emp_page.open_employee_list(direct=False)
        assert "employeelist" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 2 (/employeeList). Current URL: {authenticated_page.url}"
        )

        # Step 3: Open employee profile
        baseline = get_baseline_employee()
        target_name = baseline.get("First Name") or None
        emp_page.open_employee_profile(name=target_name, row_index=0)
        assert emp_page.is_profile_form_visible(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 3: Employee profile form is not visible after clicking profile icon."
        )

    @pytest.mark.tc_id("TC_EMP_FORM_01")
    def test_employee_update_form_controls(self, authenticated_page):
        """Verify that the Employee update form displays core fields, buttons, and read-only attributes."""
        emp_page = EmployeeUpdatePage(authenticated_page)
        emp_page.open_employee_list(direct=True)
        baseline = get_baseline_employee()
        target_name = baseline.get("First Name") or None
        emp_page.open_employee_profile(name=target_name, row_index=0)

        assert emp_page.is_profile_form_visible(), "Profile view did not open when clicking profile icon."

        # Verify Employee ID is read-only
        assert emp_page.employee_id_is_read_only(), "Employee ID field should be read-only on profile form."

        # Verify core fields can be retrieved
        first_name_val = emp_page.get_form_field_value("emp_first_name")
        assert len(first_name_val) > 0, "First Name field could not be retrieved from the update form."

        mobile_val = emp_page.get_form_field_value("emp_mobile_number")
        assert len(mobile_val) > 0, "Mobile Number field could not be retrieved from the update form."


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
