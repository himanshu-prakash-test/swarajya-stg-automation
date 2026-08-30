import pytest
from vendor_pages.login_page import LoginPage
from vendor_utils.excel_reader import read_credentials


@pytest.mark.login
class TestLoginFlow:
    """Authentication and landing verification for Vendor Management."""

    def test_manager_login_and_vendor_access(self, unauthenticated_page):
        page = unauthenticated_page
        login_page = LoginPage(page)
        creds = read_credentials("Manager")
        success = login_page.login(
            employee_id=creds["employee_id"],
            password=creds["password"],
            auth_code=creds.get("auth_code", "111111"),
        )
        assert success, "Manager login failed to authenticate"
        assert not ("login" in page.url.lower() or "tfa" in page.url.lower()), f"User did not reach authenticated dashboard: {page.url}"
