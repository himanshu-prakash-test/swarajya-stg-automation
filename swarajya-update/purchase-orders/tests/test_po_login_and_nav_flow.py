"""Test suite verifying login and navigation workflow for Purchase Order Update module."""

import pytest
from po_update_pages.login_page import LoginPage
from po_update_pages.po_update_page import POUpdatePage
from po_update_utils.excel_reader import read_credentials


@pytest.mark.login
@pytest.mark.purchase_order
@pytest.mark.po_update
class TestPurchaseOrderLoginAndNavFlow:
    """Authentication and navigation path verification for Purchase Order Update."""

    @pytest.mark.tc_id("TC_PO_AUTH_01")
    def test_admin_login_and_access(self, unauthenticated_page):
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
    def test_po_update_navigation_path(self, authenticated_page):
        """
        Verify the Purchase Order Update navigation path:
        /default -> /invoiceReports -> /invoicedashboard -> /purchaseOrder -> click pencil edit icon -> update form opens.
        Notice: Fourth customer path (/customerDetails) is removed; direct card transition to /purchaseOrder.
        """
        expected_result = (
            "User traverses: /default -> /invoiceReports -> /invoicedashboard -> "
            "/purchaseOrder -> clicks pencil edit button -> Update form opens."
        )
        po_page = POUpdatePage(authenticated_page)

        # Step 1: Default dashboard
        po_page.open_default_dashboard()
        assert "default" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 1 (/default). Current URL: {authenticated_page.url}"
        )

        # Step 2: Invoice Reports
        po_page.open_invoice_reports()
        assert "invoicereports" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 2 (/invoiceReports). Current URL: {authenticated_page.url}"
        )

        # Step 3: Invoice Home / Dashboard
        po_page.open_invoice_dashboard()
        assert "invoicedashboard" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 3 (/invoicedashboard). Current URL: {authenticated_page.url}"
        )

        # Step 4: Purchase Order listing (Directly from /invoicedashboard; /customerDetails bypassed)
        po_page.open_purchase_order_list(direct=False)
        assert "purchaseorder" in authenticated_page.url.lower(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 4 (/purchaseOrder). Current URL: {authenticated_page.url}"
        )

        # Step 5: Click pencil edit button on row
        po_page.open_po_edit_modal(row_index=0)
        assert po_page.is_update_form_visible(), (
            f"Expected Result NOT satisfied: '{expected_result}'. "
            f"Failed at step 5: Purchase Order update form is not visible after clicking pencil edit icon."
        )

        # Clean up by canceling the modal
        po_page.click_cancel()

    @pytest.mark.tc_id("TC_PO_FORM_01")
    def test_po_update_form_controls(self, authenticated_page):
        """Verify that the Purchase Order update form displays core fields and buttons."""
        po_page = POUpdatePage(authenticated_page)
        po_page.open_purchase_order_list(direct=True)
        po_page.open_po_edit_modal(row_index=0)

        assert po_page.is_update_form_visible(), "Update form did not open when clicking edit pencil icon."

        ref_no = po_page.get_form_field_value("po_ref_no")
        po_date = po_page.get_form_field_value("po_date")
        assert ref_no is not None, "PO Ref No field could not be retrieved from the update form."
        assert po_date is not None, "PO Date field could not be retrieved from the update form."

        po_page.click_cancel()
        assert not po_page.is_update_form_visible(), "Update form should be closed after clicking Cancel."
