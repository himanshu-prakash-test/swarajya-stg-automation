import pytest
from po_pages.login_page import LoginPage
from po_pages.po_page import POPage
from po_utils.excel_reader import read_credentials


@pytest.mark.login
@pytest.mark.purchase_order
class TestPurchaseOrderLoginFlow:
    """Authentication and navigation verification tests for Purchase Order Management."""

    @pytest.mark.tc_id("TC_PO_AUTH_01")
    def test_admin_login_and_po_access(self, unauthenticated_page):
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

    @pytest.mark.tc_id("TC_PO_NAV_01")
    def test_po_create_navigation_path(self, authenticated_page):
        """Verify the navigation path: /default -> /invoiceReports -> /invoicedashboard -> /purchaseOrder -> open create PO form."""
        expected_result = "User successfully traverses navigation path to /purchaseOrder and opens create form."
        po = POPage(authenticated_page)

        po.open_default_dashboard()
        assert "default" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 1 (/default). Current URL: {authenticated_page.url}"
        )

        po.open_invoice_reports()
        assert "invoicereports" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 2 (/invoiceReports). Current URL: {authenticated_page.url}"
        )

        po.open_invoice_dashboard()
        assert "invoicedashboard" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 3 (/invoicedashboard). Current URL: {authenticated_page.url}"
        )

        po.open_purchase_order_list()
        assert "purchaseorder" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 4 (/purchaseOrder). Current URL: {authenticated_page.url}"
        )

        po.open_create_po_form()
        assert po.is_create_form_visible(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 5: Purchase Order creation form/modal was not visible."
        )
