import pytest
from customer_pages.login_page import LoginPage
from customer_utils.excel_reader import read_credentials


@pytest.mark.login
@pytest.mark.customer
class TestCustomerLoginFlow:
    """Authentication and session verification tests for Customer Management."""

    @pytest.mark.tc_id("TC_CUSTOMER_AUTH_01")
    def test_admin_login_and_customer_access(self, unauthenticated_page):
        page = unauthenticated_page
        login_page = LoginPage(page)
        creds = read_credentials("Admin")
        expected_result = "Admin user successfully logs in and reaches authenticated dashboard."

        success = login_page.login(
            employee_id=creds["employee_id"],
            password=creds["password"],
            auth_code=creds.get("auth_code", "111111"),
            role=creds.get("role", "Admin"),
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
    def test_customer_create_navigation_path(self, authenticated_page):
        """Verify the full navigation path: /default -> /invoiceReports -> /invoicedashboard -> /customerDetails -> /addNewCustomer."""
        from customer_pages.customer_page import CustomerPage

        expected_result = "User successfully traverses full navigation path to /addNewCustomer create form."
        customer = CustomerPage(authenticated_page)

        customer.open_default_dashboard()
        assert "default" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 1 (/default). Current URL: {authenticated_page.url}"
        )

        customer.open_invoice_reports()
        assert "invoicereports" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 2 (/invoiceReports). Current URL: {authenticated_page.url}"
        )

        customer.open_invoice_dashboard()
        assert "invoicedashboard" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 3 (/invoicedashboard). Current URL: {authenticated_page.url}"
        )

        customer.open_customer_list()
        assert "customerdetails" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 4 (/customerDetails). Current URL: {authenticated_page.url}"
        )

        customer.open_create_customer_form()
        assert "addnewcustomer" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 5 (/addNewCustomer). Current URL: {authenticated_page.url}"
        )
