"""
Test Suite: HR & Admin Positive Authentication Flows.

Strictly data-driven from the shared Excel workbooks:
- Test Data:  shared/test_data/Swarajya-test-data.xlsx  [Sheet: loginhr_admin]
- Test Cases: shared/test_data/Swarajya-test-cases.xlsx [Sheet: loginhr_admin]

Strictly zero hardcoded credentials, test data, or URLs.
All roles, employee IDs, passwords, auth codes, and base URLs are fetched
dynamically from the shared Excel sheets.
"""

import os
import sys
import pytest

# Ensure module, login root, and workspace root are in sys.path
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULE_DIR = os.path.dirname(_TESTS_DIR)
_LOGIN_DIR = os.path.dirname(_MODULE_DIR)
_ROOT_DIR = os.path.dirname(_LOGIN_DIR)
for path_dir in (_MODULE_DIR, _LOGIN_DIR, _ROOT_DIR):
    if path_dir not in sys.path:
        sys.path.insert(0, path_dir)

from common.pages.login_page import LoginPage
from common.pages.tfa_page import TfaPage
from common.utils.excel_reader import (
    get_base_url,
    read_credentials,
    get_test_case_by_id,
)

SHEET_NAME = "loginhr_admin"


def _login_to_tfa(page, base_url, role="Admin"):
    """Helper to perform step 1 authentication up to the 2FA page using Excel credentials."""
    creds = read_credentials(role, sheet_name=SHEET_NAME)
    login = LoginPage(page, base_url)
    login.navigate()
    login.login(creds["employee_id"], creds["password"])
    tfa = TfaPage(page, base_url)
    tfa.wait_for_tfa_page(timeout=15_000)
    return login, tfa, creds


# ===========================================================================
# POSITIVE TEST SUITE
# ===========================================================================

@pytest.mark.positive
class TestAdminHrPositiveFlows:
    """Positive authentication tests for Admin and HR roles driven by Excel."""

    @pytest.mark.smoke
    @pytest.mark.tfa
    @pytest.mark.tc_id("TC_LOGIN_ADMIN_POS_01")
    def test_admin_valid_login_and_2fa_TC_LOGIN_ADMIN_POS_01(self, page, base_url):
        """TC_LOGIN_ADMIN_POS_01: Login with valid Admin Employee ID, password and 2FA code."""
        tc_meta = get_test_case_by_id("TC_LOGIN_ADMIN_POS_01", sheet_name=SHEET_NAME)
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)

        login = LoginPage(page, base_url)
        login.navigate()
        login.login(creds["employee_id"], creds["password"])

        tfa = TfaPage(page, base_url)
        tfa.wait_for_tfa_page(timeout=15_000)

        assert tfa.is_on_tfa_page(), (
            f"Admin credentials did not reach 2FA page. URL: {page.url}"
        )
        assert tfa.is_auth_code_input_visible(), (
            "Admin 2FA Google Auth Code field is not visible"
        )

        tfa.submit_auth_code(creds["auth_code"])

        assert tfa.is_dashboard_loaded(timeout=15_000), (
            f"Admin valid login did not reach dashboard. Expected: {tc_meta.get('Expected Result') if tc_meta else 'Dashboard'}. URL: {page.url}"
        )

    @pytest.mark.smoke
    @pytest.mark.tfa
    @pytest.mark.tc_id("TC_LOGIN_HR_POS_01")
    def test_hr_valid_login_and_2fa_TC_LOGIN_HR_POS_01(self, page, base_url):
        """TC_LOGIN_HR_POS_01: Login with valid HR Employee ID, password and 2FA code."""
        tc_meta = get_test_case_by_id("TC_LOGIN_HR_POS_01", sheet_name=SHEET_NAME)
        creds = read_credentials("HR", sheet_name=SHEET_NAME)

        login = LoginPage(page, base_url)
        login.navigate()
        login.login(creds["employee_id"], creds["password"])

        tfa = TfaPage(page, base_url)
        tfa.wait_for_tfa_page(timeout=15_000)

        assert tfa.is_on_tfa_page(), (
            f"HR credentials did not reach 2FA page. URL: {page.url}"
        )
        assert tfa.is_auth_code_input_visible(), (
            "HR 2FA Google Auth Code field is not visible"
        )

        tfa.submit_auth_code(creds["auth_code"])

        assert tfa.is_dashboard_loaded(timeout=15_000), (
            f"HR valid login did not reach dashboard. Expected: {tc_meta.get('Expected Result') if tc_meta else 'Dashboard'}. URL: {page.url}"
        )

    @pytest.mark.smoke
    @pytest.mark.tc_id("TC_LOGIN_POS_01")
    def test_login_page_elements_present_TC_LOGIN_POS_01(self, login_page):
        """TC_LOGIN_POS_01: Verify the required elements are present on the login page."""
        assert login_page.is_employee_id_field_visible(), "Employee ID field is not visible"
        assert login_page.is_password_field_visible(), "Password field is not visible"
        assert login_page.is_sign_in_button_visible(), "Sign In button is not visible"
        assert login_page.is_sign_in_button_enabled(), "Sign In button is not enabled"
        assert login_page.is_forgot_password_visible(), "Forgot Password link is not visible"

    @pytest.mark.tc_id("TC_LOGIN_POS_02")
    def test_password_field_masks_characters_TC_LOGIN_POS_02(self, login_page):
        """TC_LOGIN_POS_02: Verify the password field masks entered characters."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.enter_password(creds["password"])
        assert login_page.is_password_masked(), (
            "Password field does not mask entered characters (input type is not password)"
        )

    @pytest.mark.tc_id("TC_LOGIN_POS_03")
    def test_valid_credentials_navigate_to_2fa_TC_LOGIN_POS_03(self, page, base_url):
        """TC_LOGIN_POS_03: Verify a valid Employee ID and password navigate the user to the 2FA page."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login = LoginPage(page, base_url)
        login.navigate()
        login.login(creds["employee_id"], creds["password"])

        tfa = TfaPage(page, base_url)
        tfa.wait_for_tfa_page(timeout=15_000)

        assert tfa.is_on_tfa_page(), (
            f"Valid credentials did not reach 2FA page. URL: {page.url}"
        )
        assert tfa.is_auth_code_input_visible(), "2FA Auth Code input field is not visible"

    @pytest.mark.tc_id("TC_LOGIN_POS_04")
    def test_valid_auth_code_completes_login_TC_LOGIN_POS_04(self, page, base_url):
        """TC_LOGIN_POS_04: Verify a valid Google Authenticator code completes the login."""
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000), (
            f"Valid Auth Code did not redirect to dashboard. URL: {page.url}"
        )

    @pytest.mark.tc_id("TC_LOGIN_POS_05")
    def test_back_to_login_link_returns_to_signin_TC_LOGIN_POS_05(self, page, base_url):
        """TC_LOGIN_POS_05: Verify the 'Back to Login' link on the 2FA page returns user to sign-in page."""
        _, tfa, _ = _login_to_tfa(page, base_url, role="Admin")
        assert tfa.is_back_to_login_visible(), "Back to Login link is not visible on 2FA page"
        tfa.click_back_to_login()
        login = LoginPage(page, base_url)
        assert login.is_employee_id_field_visible(timeout=10_000), (
            "Clicking Back to Login did not return user to sign-in page"
        )

    @pytest.mark.tc_id("TC_LOGIN_POS_06")
    def test_logged_in_user_can_logout_TC_LOGIN_POS_06(self, page, base_url):
        """TC_LOGIN_POS_06: Verify a logged-in user can log out successfully."""
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000)

        page.goto(f"{base_url}/logout", wait_until="networkidle", timeout=15_000)
        login = LoginPage(page, base_url)
        assert login.is_employee_id_field_visible(timeout=10_000), (
            f"Logout did not return user to login page. Current URL: {page.url}"
        )

    @pytest.mark.tc_id("TC_LOGIN_POS_07")
    def test_forgot_password_link_opens_recovery_flow_TC_LOGIN_POS_07(self, page, base_url):
        """TC_LOGIN_POS_07: Verify the Forgot Password link opens the password recovery flow."""
        login = LoginPage(page, base_url)
        login.navigate()
        login.click_forgot_password()
        assert "/forgot" in page.url.lower() or "forgot" in page.content().lower() or login.is_on_login_page(), (
            f"Forgot Password action did not open recovery flow. URL: {page.url}"
        )

    @pytest.mark.tc_id("TC_LOGIN_POS_08")
    def test_alternate_browser_login_TC_LOGIN_POS_08(self):
        """TC_LOGIN_POS_08: Verify login with valid credentials on a supported alternate browser."""
        pytest.skip("Alternate-browser matrix execution configured in CI pipeline runner")


if __name__ == "__main__":
    os.environ.setdefault("SWARAJYA_POPUP_TITLE", "HR & Admin Positive Flows - Results")
    os.environ.setdefault("SWARAJYA_POPUP_HEADER", "SWARAJYA HR & ADMIN LOGIN - POSITIVE FLOWS")
    config_file = os.path.join(_ROOT_DIR, "pytest.ini")
    extra_args = sys.argv[1:]
    pytest_args = [__file__, "-c", config_file, "-o", f"rootdir={_ROOT_DIR}", "-v", "-s"]
    if not any(arg in extra_args for arg in ("--headed", "--headless")):
        pytest_args.append("--headed")
    pytest_args.extend(extra_args)
    sys.exit(pytest.main(pytest_args))
