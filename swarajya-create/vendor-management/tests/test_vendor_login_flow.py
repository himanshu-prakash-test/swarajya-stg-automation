"""
Authentication and landing verification tests for Vendor Management (Create Module).
Loads credentials and URLs dynamically from Excel workbook banner rows.
Zero hardcoded credentials or endpoints.
"""

import pytest
from shared.pages.login_page import LoginPage
from vendor_pages.vendor_page import VendorPage
from vendor_utils.excel_reader import read_credentials, SHEET_NAME


@pytest.mark.login
@pytest.mark.vendor
class TestVendorLoginFlow:
    """Authentication and navigation verification for Vendor Management."""

    def test_admin_login_and_vendor_access(self, unauthenticated_page):
        """Verify Admin user authentication and landing on dashboard."""
        page = unauthenticated_page
        login_page = LoginPage(page)
        creds = read_credentials("Admin")
        success = login_page.login(
            employee_id=creds["employee_id"],
            password=creds["password"],
            auth_code=creds.get("auth_code"),
            role=creds.get("role", "Admin"),
            sheet_name=SHEET_NAME,
        )
        assert success, "Admin authentication failed: Invalid credentials or login sequence timeout"
        assert not ("login" in page.url.lower() or "tfa" in page.url.lower()), (
            f"User did not reach authenticated dashboard: {page.url}"
        )

    def test_vendor_management_navigation_path(self, authenticated_page):
        """Verify authenticated access to Vendor Management list and create form."""
        vendor_page = VendorPage(authenticated_page)
        vendor_page.open_vendor_list()
        assert not ("login" in authenticated_page.url.lower() or "404" in authenticated_page.title().lower()), (
            f"Failed to access Vendor Management directory: {authenticated_page.url}"
        )
        vendor_page.open_create_vendor_form()
        assert not ("login" in authenticated_page.url.lower() or "404" in authenticated_page.title().lower()), (
            f"Failed to open Create Vendor form: {authenticated_page.url}"
        )
