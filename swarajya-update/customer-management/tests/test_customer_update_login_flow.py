"""Test suite verifying login and navigation workflow for Customer Update module."""

import pytest
from shared.pages.login_page import LoginPage
from customer_update_pages.customer_update_page import CustomerUpdatePage
from customer_update_utils.excel_reader import read_credentials, get_baseline_customer, SHEET_NAME


@pytest.mark.login
@pytest.mark.customer
@pytest.mark.customer_update
class TestCustomerLoginAndNavFlow:
    """Authentication and navigation path verification for Customer Update."""

    @pytest.mark.tc_id("TC_CUSTOMER_AUTH_01")
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

        success = login_page.login(
            employee_id=creds["employee_id"],
            password=creds["password"],
            auth_code=creds.get("auth_code"),
            role=creds.get("role", "Admin"),
            sheet_name=SHEET_NAME,
        )
        assert success, (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Actual: Admin login failed to authenticate with provided credentials."
        )
        assert not ("login" in page.url.lower() or "tfa" in page.url.lower()), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Actual: User remained on login or 2FA verification page: {page.url}"
        )

    @pytest.mark.tc_id("TC_CUSTOMER_NAV_01")
    def test_customer_update_navigation_path(self, authenticated_page):
        """
        Verify the Customer Update navigation path:
        /default -> /invoiceReports -> /invoicedashboard -> /customerDetails -> click edit icon -> Edit form opens.
        """
        expected_result = (
            "User traverses: /default -> /invoiceReports -> /invoicedashboard -> "
            "/customerDetails -> clicks edit icon -> Edit Customer form opens."
        )
        cust_page = CustomerUpdatePage(authenticated_page)

        # Step 1: Default dashboard
        cust_page.open_default_dashboard()
        assert "default" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 1 (/default). Current URL: {authenticated_page.url}"
        )

        # Step 2: Invoice Reports
        cust_page.open_invoice_reports()
        assert "invoicereports" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 2 (/invoiceReports). Current URL: {authenticated_page.url}"
        )

        # Step 3: Invoice Home / Dashboard
        cust_page.open_invoice_dashboard()
        assert "invoicedashboard" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 3 (/invoicedashboard). Current URL: {authenticated_page.url}"
        )

        # Step 4: Customer listing
        cust_page.open_customer_list(direct=False)
        assert "customerdetails" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 4 (/customerDetails). Current URL: {authenticated_page.url}"
        )

        # Step 5: Click edit button on row
        baseline = get_baseline_customer()
        target_name = baseline.get("Customer Name") or None
        cust_page.open_customer_edit_modal(customer_name_or_code=target_name, row_index=0)
        assert cust_page.is_edit_modal_open(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 5: Edit Customer modal is not visible after clicking edit icon."
        )
        cust_page.cancel()

    @pytest.mark.tc_id("TC_CUSTOMER_FORM_01")
    def test_customer_update_form_controls(self, authenticated_page):
        """Verify that the Customer update form displays core fields and buttons."""
        cust_page = CustomerUpdatePage(authenticated_page)
        cust_page.open_customer_list(direct=True)
        baseline = get_baseline_customer()
        target_name = baseline.get("Customer Name") or None
        cust_page.open_customer_edit_modal(customer_name_or_code=target_name, row_index=0)

        assert cust_page.is_edit_modal_open(), "Edit modal did not open when clicking edit icon."

        # Verify key fields are accessible
        name_val = cust_page.get_field_value("customer name")
        assert name_val is not None, "Customer Name field could not be retrieved from the update form."

        inputs = authenticated_page.locator("form input, form mat-select, form textarea").all()
        assert len(inputs) >= 15, f"Expected customer form fields to be visible, found {len(inputs)}"
        cust_page.cancel()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
