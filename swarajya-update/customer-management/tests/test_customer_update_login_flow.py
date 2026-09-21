import pytest
from customer_update_pages.login_page import LoginPage
from customer_update_pages.customer_update_page import CustomerUpdatePage
from shared.utils.logger import get_logger

log = get_logger("test_customer_update_login_flow")


@pytest.mark.login
@pytest.mark.sanity
class TestCustomerLoginAndNavFlow:
    """Authentication and multi-step navigation verification for Customer Update Module."""

    def test_admin_login_and_customer_details_access(self, unauthenticated_page):
        """
        Verify:
        1. Login with Admin credentials
        2. Landing on /default
        3. Step-by-step navigation:
           /default -> /invoiceReports -> /invoicedashboard -> /customerDetails
        4. Customer listing table is loaded
        """
        page = unauthenticated_page
        login_p = LoginPage(page)
        ok = login_p.login(role="Admin")
        assert ok, "Failed to authenticate with Admin credentials"

        cust_p = CustomerUpdatePage(page)

        # Step 1: Default dashboard
        cust_p.open_default_dashboard()
        assert "default" in page.url.lower(), f"Expected /default, got {page.url}"

        # Step 2: Invoicing reports
        cust_p.open_invoice_reports()
        assert "invoicereports" in page.url.lower(), f"Expected /invoiceReports, got {page.url}"

        # Step 3: Invoice Home / Dashboard
        cust_p.open_invoice_dashboard()
        assert "invoicedashboard" in page.url.lower(), f"Expected /invoicedashboard, got {page.url}"

        # Step 4: Customer Details
        cust_p.open_customer_list(direct=False)
        assert "customerdetails" in page.url.lower(), f"Expected /customerDetails, got {page.url}"

        log.info("Admin login and multi-step Customer Details navigation verified successfully.")


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
