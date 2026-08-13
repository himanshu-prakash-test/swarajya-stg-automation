"""
HR + Admin only automation.

Do not run tests/test_login.py from the original repository if you want
HR/Admin only. This module is the only test module needed for this project.
"""

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


def credentials(role):
    return read_credentials(role)


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
