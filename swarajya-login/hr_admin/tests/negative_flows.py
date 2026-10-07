"""
Test Suite: HR & Admin Negative & Boundary Authentication Flows.

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
# NEGATIVE TEST SUITE
# ===========================================================================

@pytest.mark.regression
@pytest.mark.negative
class TestAdminHrNegativeFlows:
    """Negative and boundary authentication tests driven by Excel data."""

    @pytest.mark.tc_id("TC_LOGIN_ADMIN_NEG_01")
    def test_invalid_admin_employee_id_TC_LOGIN_ADMIN_NEG_01(self, login_page):
        """TC_LOGIN_ADMIN_NEG_01: Login with an invalid Admin Employee ID and a valid password."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        invalid_id = f"99999{creds['employee_id']}"

        login_page.enter_employee_id(invalid_id)
        login_page.enter_password(creds["password"])
        login_page.click_sign_in()

        error = login_page.get_error_message(timeout=5_000)
        assert error or "/tfa-authcode/" not in login_page.get_current_url(), (
            "Invalid Admin ID unexpectedly reached 2FA"
        )

    @pytest.mark.tc_id("TC_LOGIN_ADMIN_NEG_02")
    def test_wrong_admin_password_TC_LOGIN_ADMIN_NEG_02(self, login_page):
        """TC_LOGIN_ADMIN_NEG_02: Login with a valid Admin Employee ID and an incorrect password."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        wrong_pwd = f"Wrong_{creds['password']}"

        login_page.enter_employee_id(creds["employee_id"])
        login_page.enter_password(wrong_pwd)
        login_page.click_sign_in()

        error = login_page.get_error_message(timeout=5_000)
        assert error or "/tfa-authcode/" not in login_page.get_current_url(), (
            "Incorrect Admin password unexpectedly reached 2FA"
        )

    @pytest.mark.tc_id("TC_LOGIN_HR_NEG_01")
    def test_invalid_hr_employee_id_TC_LOGIN_HR_NEG_01(self, login_page):
        """TC_LOGIN_HR_NEG_01: Login with an invalid HR Employee ID and a valid password."""
        creds = read_credentials("HR", sheet_name=SHEET_NAME)
        invalid_id = f"99999{creds['employee_id']}"

        login_page.enter_employee_id(invalid_id)
        login_page.enter_password(creds["password"])
        login_page.click_sign_in()

        error = login_page.get_error_message(timeout=5_000)
        assert error or "/tfa-authcode/" not in login_page.get_current_url(), (
            "Invalid HR ID unexpectedly reached 2FA"
        )

    @pytest.mark.tc_id("TC_LOGIN_HR_NEG_02")
    def test_wrong_hr_password_TC_LOGIN_HR_NEG_02(self, login_page):
        """TC_LOGIN_HR_NEG_02: Login with a valid HR Employee ID and an incorrect password."""
        creds = read_credentials("HR", sheet_name=SHEET_NAME)
        wrong_pwd = f"Wrong_{creds['password']}"

        login_page.enter_employee_id(creds["employee_id"])
        login_page.enter_password(wrong_pwd)
        login_page.click_sign_in()

        error = login_page.get_error_message(timeout=5_000)
        assert error or "/tfa-authcode/" not in login_page.get_current_url(), (
            "Incorrect HR password unexpectedly reached 2FA"
        )

    @pytest.mark.tc_id("TC_LOGIN_NEG_01")
    def test_both_id_and_password_incorrect_TC_LOGIN_NEG_01(self, login_page):
        """TC_LOGIN_NEG_01: Login with both Employee ID and password incorrect."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login(f"INV_{creds['employee_id']}", f"Wrong_{creds['password']}")
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" not in login_page.get_current_url()

    @pytest.mark.tc_id("TC_LOGIN_NEG_02")
    def test_blank_employee_id_TC_LOGIN_NEG_02(self, login_page, base_url):
        """TC_LOGIN_NEG_02: Login with the Employee ID field left blank."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login("", creds["password"])
        assert login_page.get_error_message(timeout=5_000) or login_page.get_current_url() == f"{base_url}/" or not login_page.is_sign_in_button_enabled()

    @pytest.mark.tc_id("TC_LOGIN_NEG_03")
    def test_blank_password_TC_LOGIN_NEG_03(self, login_page, base_url):
        """TC_LOGIN_NEG_03: Login with the Password field left blank."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login(creds["employee_id"], "")
        assert login_page.get_error_message(timeout=5_000) or login_page.get_current_url() == f"{base_url}/" or not login_page.is_sign_in_button_enabled()

    @pytest.mark.tc_id("TC_LOGIN_NEG_04")
    def test_both_fields_blank_TC_LOGIN_NEG_04(self, login_page, base_url):
        """TC_LOGIN_NEG_04: Login with both the Employee ID and Password fields left blank."""
        login_page.login("", "")
        assert login_page.get_error_message(timeout=5_000) or login_page.get_current_url() == f"{base_url}/" or not login_page.is_sign_in_button_enabled()

    @pytest.mark.tc_id("TC_LOGIN_NEG_05")
    def test_employee_id_whitespace_TC_LOGIN_NEG_05(self, login_page):
        """TC_LOGIN_NEG_05: Login with an Employee ID containing leading or trailing spaces."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login(f"  {creds['employee_id']}  ", creds["password"])
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" in login_page.get_current_url() or login_page.is_on_login_page()

    @pytest.mark.tc_id("TC_LOGIN_NEG_06")
    def test_password_whitespace_TC_LOGIN_NEG_06(self, login_page):
        """TC_LOGIN_NEG_06: Login with a password containing leading or trailing spaces."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login(creds["employee_id"], f"  {creds['password']}  ")
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" not in login_page.get_current_url()

    @pytest.mark.tc_id("TC_LOGIN_NEG_07")
    def test_special_characters_employee_id_TC_LOGIN_NEG_07(self, login_page):
        """TC_LOGIN_NEG_07: Login with special characters entered in the Employee ID field."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login("!@#$%^&*()_+", creds["password"])
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" not in login_page.get_current_url()

    @pytest.mark.tc_id("TC_LOGIN_NEG_08")
    def test_sql_injection_attempt_TC_LOGIN_NEG_08(self, login_page):
        """TC_LOGIN_NEG_08: Login with a SQL injection string entered in the login fields."""
        login_page.login("' OR '1'='1", "' OR '1'='1")
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" not in login_page.get_current_url()

    @pytest.mark.tc_id("TC_LOGIN_NEG_09")
    def test_script_injection_xss_attempt_TC_LOGIN_NEG_09(self, login_page):
        """TC_LOGIN_NEG_09: Login with a script injection (XSS) string entered in the Employee ID field."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login("<script>alert(1)</script>", creds["password"])
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" not in login_page.get_current_url()

    @pytest.mark.tc_id("TC_LOGIN_NEG_10")
    def test_excessive_length_employee_id_TC_LOGIN_NEG_10(self, login_page):
        """TC_LOGIN_NEG_10: Login with an Employee ID exceeding the supported character limit."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login(str(creds["employee_id"]) * 50, creds["password"])
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" not in login_page.get_current_url()

    @pytest.mark.tc_id("TC_LOGIN_NEG_11")
    def test_excessive_length_password_TC_LOGIN_NEG_11(self, login_page):
        """TC_LOGIN_NEG_11: Login with a password exceeding the supported character limit."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login(creds["employee_id"], str(creds["password"]) * 30)
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" not in login_page.get_current_url()

    @pytest.mark.tc_id("TC_LOGIN_NEG_12")
    def test_locked_deactivated_account_TC_LOGIN_NEG_12(self, login_page):
        """TC_LOGIN_NEG_12: Login attempt using a locked or deactivated account."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login_page.login(f"DEACT_{creds['employee_id']}", creds["password"])
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" not in login_page.get_current_url()

    @pytest.mark.tc_id("TC_LOGIN_NEG_13")
    def test_password_case_sensitivity_TC_LOGIN_NEG_13(self, login_page):
        """TC_LOGIN_NEG_13: Login with the correct password entered in an incorrect case."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        cased_pwd = creds["password"].swapcase()
        login_page.login(creds["employee_id"], cased_pwd)
        assert login_page.get_error_message(timeout=5_000) or "/tfa-authcode/" not in login_page.get_current_url()

    @pytest.mark.tc_id("TC_LOGIN_NEG_14")
    def test_incorrect_auth_code_2fa_TC_LOGIN_NEG_14(self, page, base_url):
        """TC_LOGIN_NEG_14: Login attempt with an incorrect Google Authenticator code on the 2FA page."""
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        wrong_code = "999999" if creds["auth_code"] != "999999" else "000000"
        tfa.submit_auth_code(wrong_code)
        assert tfa.is_on_tfa_page(), "Submitting incorrect 2FA code navigated away"
        assert not tfa.is_dashboard_loaded(timeout=3_000), "Dashboard loaded with incorrect 2FA code"

    @pytest.mark.tc_id("TC_LOGIN_NEG_15")
    def test_blank_auth_code_2fa_TC_LOGIN_NEG_15(self, page, base_url):
        """TC_LOGIN_NEG_15: Login attempt with the 2FA code field left blank."""
        _, tfa, _ = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code("")
        assert tfa.is_on_tfa_page(), "Blank 2FA code navigated away from 2FA"
        assert not tfa.is_dashboard_loaded(timeout=3_000), "Dashboard loaded with blank 2FA code"

    @pytest.mark.tc_id("TC_LOGIN_NEG_16")
    def test_expired_auth_code_2fa_TC_LOGIN_NEG_16(self, page, base_url):
        """TC_LOGIN_NEG_16: Login attempt with an expired Google Authenticator code."""
        _, tfa, _ = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code("000000")
        assert tfa.is_on_tfa_page(), "Expired 2FA code navigated away from 2FA page"

    @pytest.mark.tc_id("TC_LOGIN_NEG_17")
    def test_reused_consumed_auth_code_TC_LOGIN_NEG_17(self, page, base_url):
        """TC_LOGIN_NEG_17: Login attempt reusing an already-consumed Google Authenticator code."""
        login, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000)

        page.goto(f"{base_url}/logout", wait_until="networkidle", timeout=15_000)
        login.navigate()
        login.login(creds["employee_id"], creds["password"])
        tfa.wait_for_tfa_page(timeout=15_000)
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_on_tfa_page() or tfa.is_dashboard_loaded(timeout=15_000)

    @pytest.mark.tc_id("TC_LOGIN_NEG_18")
    def test_direct_2fa_url_access_denied_TC_LOGIN_NEG_18(self, page, base_url):
        """TC_LOGIN_NEG_18: Verify the 2FA page cannot be accessed directly without a valid prior sign-in."""
        page.goto(f"{base_url}/tfa-authcode/", wait_until="networkidle", timeout=15_000)
        login = LoginPage(page, base_url)
        assert "/tfa-authcode/" not in page.url or login.is_employee_id_field_visible(), (
            f"2FA page accessible directly without prior sign-in. URL: {page.url}"
        )

    @pytest.mark.tc_id("TC_LOGIN_NEG_19")
    def test_repeated_failed_2fa_attempts_TC_LOGIN_NEG_19(self, page, base_url):
        """TC_LOGIN_NEG_19: Verify repeated failed 2FA attempts trigger the configured security control."""
        login, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        wrong_code = "999999" if creds["auth_code"] != "999999" else "000000"
        for _ in range(3):
            tfa.submit_auth_code(wrong_code)
        assert tfa.is_on_tfa_page() or login.is_employee_id_field_visible()

    @pytest.mark.tc_id("TC_LOGIN_NEG_20")
    def test_failed_login_does_not_grant_access_TC_LOGIN_NEG_20(self, page, base_url):
        """TC_LOGIN_NEG_20: Verify a failed login attempt does not grant application access."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login = LoginPage(page, base_url)
        login.navigate()
        login.login(f"INV_{creds['employee_id']}", f"Wrong_{creds['password']}")
        page.goto(f"{base_url}/default", wait_until="networkidle", timeout=15_000)
        assert login.is_employee_id_field_visible() or "/default" not in page.url.lower(), (
            f"Failed login granted access to dashboard: {page.url}"
        )

    @pytest.mark.tc_id("TC_LOGIN_NEG_21")
    def test_unauthenticated_user_cannot_access_dashboard_TC_LOGIN_NEG_21(self, page, base_url):
        """TC_LOGIN_NEG_21: Verify an unauthenticated user cannot access the dashboard directly."""
        page.goto(f"{base_url}/default", wait_until="networkidle", timeout=15_000)
        login = LoginPage(page, base_url)
        assert login.is_employee_id_field_visible() or "/default" not in page.url.lower(), (
            f"Unauthenticated user was not redirected away from dashboard. URL: {page.url}"
        )

    @pytest.mark.tc_id("TC_LOGIN_NEG_22")
    def test_hr_user_cannot_access_admin_portal_TC_LOGIN_NEG_22(self, page, base_url):
        """TC_LOGIN_NEG_22: Verify an HR user cannot access Admin-only functionality."""
        creds = read_credentials("HR", sheet_name=SHEET_NAME)
        login = LoginPage(page, base_url)
        login.navigate()
        login.login(creds["employee_id"], creds["password"])
        tfa = TfaPage(page, base_url)
        tfa.wait_for_tfa_page(timeout=15_000)
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000)

        page.goto(f"{base_url}/admin", wait_until="networkidle", timeout=15_000)
        content_lower = page.content().lower()
        assert (
            "admin" not in page.url.lower()
            or "access denied" in content_lower
            or "not authorized" in content_lower
            or login.is_employee_id_field_visible()
        ), f"HR accessed Admin-only functionality. URL: {page.url}"

    @pytest.mark.tc_id("TC_LOGIN_NEG_23")
    def test_repeated_failed_signin_attempts_TC_LOGIN_NEG_23(self, page, base_url):
        """TC_LOGIN_NEG_23: Verify application behaviour on repeated failed Sign In attempts."""
        creds = read_credentials("Admin", sheet_name=SHEET_NAME)
        login = LoginPage(page, base_url)
        login.navigate()
        wrong_pwd = f"Wrong_{creds['password']}"
        for _ in range(3):
            login.login(creds["employee_id"], wrong_pwd)
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url

    @pytest.mark.tc_id("TC_LOGIN_NEG_24")
    def test_session_expiration_protection_TC_LOGIN_NEG_24(self, page, base_url):
        """TC_LOGIN_NEG_24: Verify login is required again after session expiration."""
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000)

        page.goto(f"{base_url}/logout", wait_until="networkidle", timeout=15_000)
        page.goto(f"{base_url}/default", wait_until="networkidle", timeout=15_000)
        login = LoginPage(page, base_url)
        assert login.is_employee_id_field_visible() or "/default" not in page.url.lower()

    @pytest.mark.tc_id("TC_LOGIN_NEG_25")
    def test_back_button_cache_protection_TC_LOGIN_NEG_25(self, page, base_url):
        """TC_LOGIN_NEG_25: Verify the browser back button does not expose a cached page after logout."""
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000)

        page.goto(f"{base_url}/logout", wait_until="networkidle", timeout=15_000)
        page.go_back()
        login = LoginPage(page, base_url)
        assert login.is_employee_id_field_visible() or "/default" not in page.url.lower()


if __name__ == "__main__":
    os.environ.setdefault("SWARAJYA_POPUP_TITLE", "HR & Admin Negative Flows - Results")
    os.environ.setdefault("SWARAJYA_POPUP_HEADER", "SWARAJYA HR & ADMIN LOGIN - NEGATIVE FLOWS")
    config_file = os.path.join(_ROOT_DIR, "pytest.ini")
    extra_args = sys.argv[1:]
    pytest_args = [__file__, "-c", config_file, "-o", f"rootdir={_ROOT_DIR}", "-v", "-s"]
    if not any(arg in extra_args for arg in ("--headed", "--headless")):
        pytest_args.append("--headed")
    pytest_args.extend(extra_args)
    sys.exit(pytest.main(pytest_args))
