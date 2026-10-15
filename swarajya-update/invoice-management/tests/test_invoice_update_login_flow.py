"""Test suite verifying login and navigation workflow for Invoice Update module."""

import pytest
from shared.pages.login_page import LoginPage
from invoice_update_pages.invoice_update_page import InvoiceUpdatePage
from invoice_update_utils.excel_reader import read_credentials, get_baseline_invoice, SHEET_NAME


@pytest.mark.login
@pytest.mark.invoice
@pytest.mark.invoice_update
class TestInvoiceLoginAndNavFlow:
    """Authentication and navigation path verification for Invoice Update."""

    @pytest.mark.tc_id("TC_INV_AUTH_01")
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

    @pytest.mark.tc_id("TC_INV_NAV_01")
    def test_invoice_update_navigation_path(self, authenticated_page):
        """
        Verify the Invoice Update navigation path:
        /default -> /invoiceReports -> /invoicedashboard -> /invoice -> click edit icon -> /editInvoice opens.
        """
        expected_result = (
            "User traverses: /default -> /invoiceReports -> /invoicedashboard -> "
            "/invoice -> clicks edit icon -> Edit Invoice form opens."
        )
        inv_page = InvoiceUpdatePage(authenticated_page)

        # Step 1: Default dashboard
        inv_page.open_default_dashboard()
        assert "default" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 1 (/default). Current URL: {authenticated_page.url}"
        )

        # Step 2: Invoice Reports
        inv_page.open_invoice_reports()
        assert "invoicereports" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 2 (/invoiceReports). Current URL: {authenticated_page.url}"
        )

        # Step 3: Invoice Home / Dashboard
        inv_page.open_invoice_dashboard()
        assert "invoicedashboard" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 3 (/invoicedashboard). Current URL: {authenticated_page.url}"
        )

        # Step 4: Invoice listing
        inv_page.open_invoice_list(direct=False)
        assert "invoice" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 4 (/invoice). Current URL: {authenticated_page.url}"
        )

        # Step 5: Click edit button on row
        baseline = get_baseline_invoice()
        target_no = baseline.get("Invoice ID / Invoice No") or None
        inv_page.open_invoice_edit_view(invoice_no=target_no, row_index=0)
        assert inv_page.is_edit_form_visible(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 5: Edit Invoice view is not visible after clicking edit icon."
        )

    @pytest.mark.tc_id("TC_INV_FORM_01")
    def test_invoice_update_form_controls(self, authenticated_page):
        """Verify that the Invoice update form displays core fields and buttons."""
        inv_page = InvoiceUpdatePage(authenticated_page)
        inv_page.open_invoice_list(direct=True)
        baseline = get_baseline_invoice()
        target_no = baseline.get("Invoice ID / Invoice No") or None
        inv_page.open_invoice_edit_view(invoice_no=target_no, row_index=0)

        assert inv_page.is_edit_form_visible(), "Edit view did not open when clicking edit icon."

        # Verify summary banner and fields
        banner = inv_page.get_header_banner_text()
        assert len(banner) > 0, "Summary header banner is empty in edit view."

        date_val = inv_page.get_form_field_value("invoice_date")
        assert date_val is not None, "Invoice Date field could not be retrieved from the update form."

        is_cust_locked = inv_page.is_customer_name_readonly()
        assert is_cust_locked, "Customer name should be locked/read-only on edit invoice form."


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
