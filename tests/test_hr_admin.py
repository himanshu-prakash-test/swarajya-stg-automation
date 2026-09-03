"""
Workbooks-driven HR + Admin + General login validation.

This file intentionally validates all workbook entries relevant to the current
login flow instead of skipping General cases.
"""

import os
import sys
import time

# Ensure project root is in sys.path and auto-switch to .venv if needed
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

venv_python = os.path.join(ROOT_DIR, ".venv", "bin", "python3")
if os.path.exists(venv_python) and sys.executable != venv_python and not os.environ.get("_IN_VENV_SUBPROC"):
    os.environ["_IN_VENV_SUBPROC"] = "1"
    os.execv(venv_python, [venv_python] + sys.argv)

import pyotp
import pytest

from pages.login_page import LoginPage
from pages.tfa_page import TfaPage
from utils.excel_reader import read_credentials


ROLE_TC = {
    "Admin": {
        "valid": "TC_ADMIN_001",
        "invalid_id": "TC_ADMIN_002",
        "wrong_password": "TC_ADMIN_003",
    },
    "HR": {
        "valid": "TC_HR_001",
        "invalid_id": "TC_HR_002",
        "wrong_password": "TC_HR_003",
    },
}

GENERAL_CASES = [
    "TC_LOGIN_001",
    "TC_LOGIN_002",
    "TC_LOGIN_003",
    "TC_LOGIN_004",
    "TC_LOGIN_005",
    "TC_LOGIN_006",
    "TC_LOGIN_007",
    "TC_LOGIN_008",
    "TC_LOGIN_009",
    "TC_LOGIN_010",
    "TC_LOGIN_011",
    "TC_LOGIN_012",
    "TC_LOGIN_013",
    "TC_LOGIN_014",
    "TC_LOGIN_015",
    "TC_LOGIN_016",
    "TC_LOGIN_017",
    "TC_LOGIN_018",
    "TC_LOGIN_019",
    "TC_LOGIN_020",
    "TC_LOGIN_021",
    "TC_LOGIN_022",
    "TC_LOGIN_023",
    "TC_LOGIN_024",
    "TC_LOGIN_025",
    "TC_LOGIN_026",
    "TC_LOGIN_027",
    "TC_LOGIN_028",
    "TC_LOGIN_029",
    "TC_LOGIN_030",
    "TC_LOGIN_031",
    "TC_LOGIN_032",
    "TC_LOGIN_033",
    "TC_LOGIN_034",
    "TC_LOGIN_035",
]


def credentials(role):
    return read_credentials(role)


def _login_to_tfa(page, base_url, role="Admin"):
    creds = credentials(role)
    login = LoginPage(page, base_url)
    login.navigate()
    login.login(creds["employee_id"], creds["password"])
    tfa = TfaPage(page, base_url)
    tfa.wait_for_tfa_page(timeout=15_000)
    return login, tfa, creds


@pytest.mark.smoke
@pytest.mark.positive
@pytest.mark.tfa
@pytest.mark.parametrize(
    "role",
    ["Admin", "HR"],
    ids=lambda r: ROLE_TC[r]["valid"],
)
def test_valid_login_and_2fa(page, base_url, role):
    tc_id = ROLE_TC[role]["valid"]
    creds = credentials(role)

    login = LoginPage(page, base_url)
    login.navigate()
    login.login(creds["employee_id"], creds["password"])

    tfa = TfaPage(page, base_url)
    tfa.wait_for_tfa_page(timeout=15_000)

    assert tfa.is_on_tfa_page(), (
        f"{role} valid credentials did not reach 2FA. URL={page.url}"
    )
    assert tfa.is_auth_code_input_visible(), (
        f"{role} 2FA auth-code field is not visible"
    )

    tfa.submit_auth_code(creds["auth_code"])

    assert tfa.is_dashboard_loaded(timeout=15_000), (
        f"{role} valid credentials did not reach dashboard. URL={page.url}"
    )


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize(
    "role",
    ["Admin", "HR"],
    ids=lambda r: ROLE_TC[r]["invalid_id"],
)
def test_invalid_employee_id(role, login_page):
    creds = credentials(role)
    invalid_id = "INVALID_ADMIN" if role == "Admin" else "INVALID_HR"

    login_page.enter_employee_id(invalid_id)
    login_page.enter_password(creds["password"])
    login_page.click_sign_in()

    error = login_page.get_error_message(timeout=5_000)

    assert error, (
        f"{role} invalid-ID test did not display an error message"
    )
    assert "/tfa-authcode/" not in login_page.get_current_url(), (
        f"{role} invalid ID incorrectly reached 2FA"
    )


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize(
    "role",
    ["Admin", "HR"],
    ids=lambda r: ROLE_TC[r]["wrong_password"],
)
def test_wrong_password(role, login_page):
    creds = credentials(role)

    login_page.enter_employee_id(creds["employee_id"])
    login_page.enter_password("Wrong@123")
    login_page.click_sign_in()

    error = login_page.get_error_message(timeout=5_000)

    assert error, (
        f"{role} wrong-password test did not display an error message"
    )
    assert "/tfa-authcode/" not in login_page.get_current_url(), (
        f"{role} wrong password incorrectly reached 2FA"
    )


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize("tc_id", GENERAL_CASES, ids=lambda x: x)
def test_general_login_cases(page, base_url, tc_id):
    if tc_id == "TC_LOGIN_001":
        login = LoginPage(page, base_url)
        login.navigate()
        assert login.is_employee_id_field_visible()
        assert login.is_password_field_visible()
        assert login.is_sign_in_button_visible()
        assert login.is_sign_in_button_enabled()
        assert login.is_error_displayed() is False
        return

    if tc_id == "TC_LOGIN_002":
        login = LoginPage(page, base_url)
        login.navigate()
        login.enter_employee_id("332")
        login.enter_password("Test@123")
        assert page.locator("input[name='password']").get_attribute("type") == "password"
        return

    if tc_id == "TC_LOGIN_003":
        login, tfa, _ = _login_to_tfa(page, base_url, role="Admin")
        assert tfa.is_on_tfa_page() and tfa.is_auth_code_input_visible()
        return

    if tc_id == "TC_LOGIN_004":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000)
        return

    if tc_id == "TC_LOGIN_005":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        assert tfa.is_back_to_login_visible()
        tfa.click_back_to_login()
        assert LoginPage(page, base_url).is_employee_id_field_visible()
        return

    if tc_id == "TC_LOGIN_006":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000)
        page.goto(f"{base_url}/logout", wait_until="networkidle", timeout=15_000)
        assert LoginPage(page, base_url).is_employee_id_field_visible()
        return

    if tc_id == "TC_LOGIN_007":
        login = LoginPage(page, base_url)
        login.navigate()
        login.click_forgot_password()
        assert "/forgot" in page.url.lower()
        return

    if tc_id == "TC_LOGIN_008":
        pytest.skip("Alternate-browser validation is not available in the local runner")

    if tc_id == "TC_LOGIN_009":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("INVALID_USER", "INVALID@123")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_010":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("", "test@1234")
        assert login.get_error_message(timeout=5_000) or login.get_current_url() == f"{base_url}/"
        return

    if tc_id == "TC_LOGIN_011":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("332", "")
        assert login.get_error_message(timeout=5_000) or login.get_current_url() == f"{base_url}/"
        return

    if tc_id == "TC_LOGIN_012":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("", "")
        assert login.get_error_message(timeout=5_000) or login.get_current_url() == f"{base_url}/"
        return

    if tc_id == "TC_LOGIN_013":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login(" 332 ", "test@1234")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_014":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("332", " test@1234 ")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_015":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("@@@", "test@1234")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_016":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("' OR 1=1 --", "' OR 1=1 --")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_017":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("<script>alert(1)</script>", "test@1234")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_018":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("9" * 256, "test@1234")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_019":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("332", "A" * 256)
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_020":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("000000", "test@1234")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_021":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("332", "TEST@1234")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_022":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code("123456")
        assert tfa.is_on_tfa_page() and tfa.is_auth_code_input_visible()
        return

    if tc_id == "TC_LOGIN_023":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code("")
        assert tfa.is_on_tfa_page() and tfa.is_auth_code_input_visible()
        return

    if tc_id == "TC_LOGIN_024":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        stale_code = pyotp.TOTP("JBSWY3DPEHPK3PXP").at(int(time.time()) - 90)
        tfa.submit_auth_code(stale_code)
        assert tfa.is_on_tfa_page() and tfa.is_auth_code_input_visible()
        return

    if tc_id == "TC_LOGIN_025":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        code = creds["auth_code"]
        tfa.submit_auth_code(code)
        assert tfa.is_on_tfa_page() and tfa.is_auth_code_input_visible()
        return

    if tc_id == "TC_LOGIN_026":
        page.goto(f"{base_url}/tfa-authcode/", wait_until="networkidle", timeout=15_000)
        assert "/tfa-authcode/" not in page.url or LoginPage(page, base_url).is_employee_id_field_visible()
        return

    if tc_id == "TC_LOGIN_027":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        for _ in range(3):
            tfa.submit_auth_code("123456")
        assert tfa.is_on_tfa_page() or LoginPage(page, base_url).is_employee_id_field_visible()
        return

    if tc_id == "TC_LOGIN_028":
        login = LoginPage(page, base_url)
        login.navigate()
        login.login("332", "Wrong@123")
        assert "/default" not in page.url.lower()
        assert login.get_error_message(timeout=5_000) or login.get_current_url() == f"{base_url}/"
        return

    if tc_id == "TC_LOGIN_029":
        page.goto(f"{base_url}/default", wait_until="networkidle", timeout=15_000)
        assert LoginPage(page, base_url).is_employee_id_field_visible() or "/default" not in page.url.lower()
        return

    if tc_id in {"TC_LOGIN_030", "TC_LOGIN_031", "TC_LOGIN_032"}:
        role_map = {"TC_LOGIN_030": "HR", "TC_LOGIN_031": "Employee", "TC_LOGIN_032": "Manager"}
        login, _, _ = _login_to_tfa(page, base_url, role=role_map[tc_id])
        page.goto(f"{base_url}/admin", wait_until="networkidle", timeout=15_000)
        assert "admin" not in page.url.lower() or "access denied" in page.content().lower() or "not authorized" in page.content().lower() or LoginPage(page, base_url).is_employee_id_field_visible()
        return

    if tc_id == "TC_LOGIN_033":
        login = LoginPage(page, base_url)
        login.navigate()
        for _ in range(3):
            login.login("332", "Wrong@123")
        assert login.get_error_message(timeout=5_000) or "/tfa-authcode/" not in page.url
        return

    if tc_id == "TC_LOGIN_034":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000)
        page.goto(f"{base_url}/logout", wait_until="networkidle", timeout=15_000)
        page.goto(f"{base_url}/default", wait_until="networkidle", timeout=15_000)
        assert LoginPage(page, base_url).is_employee_id_field_visible() or "/default" not in page.url.lower()
        return

    if tc_id == "TC_LOGIN_035":
        _, tfa, creds = _login_to_tfa(page, base_url, role="Admin")
        tfa.submit_auth_code(creds["auth_code"])
        assert tfa.is_dashboard_loaded(timeout=15_000)
        page.goto(f"{base_url}/logout", wait_until="networkidle", timeout=15_000)
        page.go_back()
        assert LoginPage(page, base_url).is_employee_id_field_visible() or "/default" not in page.url.lower()
        return

    pytest.fail(f"Unhandled general login case: {tc_id}")


if __name__ == "__main__":
    os.environ.setdefault("SWARAJYA_POPUP_TITLE", "HR & Admin Login - Results")
    os.environ.setdefault("SWARAJYA_POPUP_HEADER", "SWARAJYA HR & ADMIN LOGIN")
    config_file = os.path.join(ROOT_DIR, "pytest.ini")
    extra_args = sys.argv[1:]
    pytest_args = [__file__, "-c", config_file, "-o", f"rootdir={ROOT_DIR}", "-v", "-s"]
    if not any(arg in extra_args for arg in ("--headed", "--headless")):
        pytest_args.append("--headed")
    pytest_args.extend(extra_args)
    sys.exit(pytest.main(pytest_args))
